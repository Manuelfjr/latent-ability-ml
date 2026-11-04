"""Tutorial assistant: a thin, rate-limited proxy from the site to the Claude API.

The API key stays on the server. Requests are streamed back to the browser as
server-sent events so answers appear while they are being written.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterator

MAX_TURNS = 20
MAX_MESSAGE_CHARS = 6000
MAX_CONTEXT_CHARS = 8000
CONTEXT_FILE = Path(__file__).resolve().parent / "tutorial_context.md"

SYSTEM_PROMPT = """Você é o assistente do tutorial "Avaliação com habilidade latente" (Instituto Kunumi e CIn/UFPE), \
apresentado no ITA por Manuel Ferreira Junior. O tutorial tem 20 minutos de apresentação e 40 de hands-on, em duas \
partes: avaliação de classificadores exemplo a exemplo, e Teoria de Resposta ao Item aplicada a uma \
população de modelos, com o β3-IRT (pacote birt-gd, respostas contínuas: a probabilidade que cada modelo dá à \
classe correta). O CLAIRE (avaliação de agrupamentos com IRT e β4-IRT) aparece só como demonstração.

Quem pergunta: doutorandos e pesquisadores de outras áreas. Têm boa formação quantitativa, mas não conhecem IRT nem \
necessariamente aprendizado de máquina. Pode usar matemática quando ajudar, sem jargão desnecessário.

O objetivo do hands-on é analisar e tirar conclusões, não programar. Por isso:
- Ajude a pessoa a raciocinar: aponte o que observar no gráfico ou na tabela, faça uma pergunta de volta quando isso \
ajudar, e valorize interpretações próprias e criativas, mesmo diferentes do gabarito, quando forem defensáveis.
- O gabarito abaixo é uma leitura possível, para você se orientar. Não o copie de cara: primeiro ajude a pessoa a \
chegar lá. Se ela já escreveu a própria análise ou pedir explicitamente a resposta, pode discuti-la abertamente.
- Se perguntarem sobre o código, explique o que ele faz e sugira mudanças para testar hipóteses. Você não executa \
código; quando um número importar, peça para a pessoa executar e contar o resultado.
- Respostas curtas e diretas (em geral até 150 palavras), em português, a menos que a pessoa escreva em outra língua. \
Use Markdown simples: parágrafos, listas, `código` e blocos de código. Não use travessão (— ou –); \
prefira vírgula, dois-pontos, parênteses ou uma frase nova.
- Fora do tema do tutorial, responda em uma frase e traga a conversa de volta.
- Não invente números do tutorial: use os do material abaixo ou os que a pessoa trouxer.

A cada pergunta você recebe, entre <contexto_da_pagina>, a página e a tarefa que a pessoa está vendo, com o código, a \
saída e a análise que ela escreveu. Use isso para responder sobre aquilo que ela tem na tela."""


def _load_context() -> str:
    try:
        return CONTEXT_FILE.read_text(encoding="utf-8")
    except OSError:
        return ""


class ChatUnavailable(Exception):
    """The assistant is not configured or is temporarily refusing new requests."""


class ChatService:
    def __init__(self, api_key: str, model: str, effort: str, max_tokens: int, max_concurrent: int, per_hour: int) -> None:
        import anthropic

        self._anthropic = anthropic
        self._client = anthropic.Anthropic(api_key=api_key, max_retries=2, timeout=120.0)
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens
        self.per_hour = per_hour
        self._slots = threading.BoundedSemaphore(max_concurrent)
        self._history: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        context = _load_context()
        self._system = [{"type": "text", "text": SYSTEM_PROMPT + ("\n\n" + context if context else "")}]

    # -- limits ---------------------------------------------------------------------

    def _check_rate(self, keys: list[str]) -> None:
        now = time.monotonic()
        with self._lock:
            for key in keys:
                window = self._history[key]
                while window and now - window[0] > 3600:
                    window.popleft()
                if len(window) >= self.per_hour:
                    raise ChatUnavailable("Limite de perguntas por hora atingido. Tente de novo mais tarde.")
            for key in keys:
                self._history[key].append(now)

    # -- request --------------------------------------------------------------------

    @staticmethod
    def _clean_messages(raw: Any) -> list[dict[str, str]]:
        if not isinstance(raw, list) or not raw:
            raise ValueError("Envie pelo menos uma mensagem.")
        messages: list[dict[str, str]] = []
        for item in raw[-MAX_TURNS:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            text = str(item.get("content") or "").strip()[:MAX_MESSAGE_CHARS]
            if role not in ("user", "assistant") or not text:
                continue
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"] += "\n\n" + text
            else:
                messages.append({"role": role, "content": text})
        while messages and messages[0]["role"] != "user":
            messages.pop(0)
        if not messages or messages[-1]["role"] != "user":
            raise ValueError("A última mensagem precisa ser da pessoa.")
        return messages

    @staticmethod
    def _format_context(context: Any) -> str:
        if not isinstance(context, dict):
            return ""
        labels = {
            "page": "Página",
            "task": "Tarefa em foco",
            "question": "Pergunta da tarefa",
            "code": "Código no editor",
            "output": "Última saída",
            "analysis": "Análise escrita pela pessoa",
        }
        parts = []
        for key, label in labels.items():
            value = str(context.get(key) or "").strip()
            if value:
                parts.append(f"{label}:\n{value[:3000]}")
        text = "\n\n".join(parts)[:MAX_CONTEXT_CHARS]
        return f"<contexto_da_pagina>\n{text}\n</contexto_da_pagina>\n\n" if text else ""

    def stream(self, raw_messages: Any, context: Any, rate_keys: list[str]) -> Iterator[dict[str, Any]]:
        """Yield ``{"type": "text"|"done"|"error", ...}`` events for one answer."""
        messages = self._clean_messages(raw_messages)
        self._check_rate(rate_keys)
        if not self._slots.acquire(timeout=20):
            raise ChatUnavailable("Muitas perguntas ao mesmo tempo. Tente de novo em alguns segundos.")
        try:
            # Page context goes into the newest user turn, after the cacheable prefix.
            messages[-1] = {"role": "user", "content": self._format_context(context) + messages[-1]["content"]}
            anthropic = self._anthropic
            try:
                with self._client.beta.messages.stream(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=self._system,
                    messages=messages,
                    output_config={"effort": self.effort},
                    cache_control={"type": "ephemeral"},
                    betas=["server-side-fallback-2026-07-01"],
                    fallbacks="default",
                ) as stream:
                    for text in stream.text_stream:
                        yield {"type": "text", "text": text}
                    final = stream.get_final_message()
                if final.stop_reason == "refusal":
                    yield {"type": "error", "error": "O modelo preferiu não responder a essa pergunta. Tente reformular."}
                elif final.stop_reason == "max_tokens":
                    yield {"type": "text", "text": "\n\n_(resposta cortada por tamanho)_"}
                yield {"type": "done"}
            except anthropic.AuthenticationError:
                yield {"type": "error", "error": "A chave da API do assistente é inválida. Avise o instrutor."}
            except anthropic.RateLimitError:
                yield {"type": "error", "error": "O assistente está sobrecarregado. Tente de novo em instantes."}
            except anthropic.APIStatusError as error:
                yield {"type": "error", "error": f"Erro do serviço do assistente ({error.status_code}). Tente de novo."}
            except anthropic.APIConnectionError:
                yield {"type": "error", "error": "Sem conexão com o serviço do assistente. Tente de novo."}
        finally:
            self._slots.release()
