"""Gera os dados das tarefas do site e os notebooks do tutorial no ITA a partir de tasks.py.

Rode a partir da raiz do repositório:

    python notebooks/ita/build_material.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tasks import PARTS, THEME  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA_DIR = REPO / "site" / "_data" / "ita"
NB_DIR = REPO / "notebooks" / "ita"
CHAT_CONTEXT = REPO / "backend" / "tutorial_context.md"
HELPERS = REPO / "utils" / "handson.py"

SETUP = """import subprocess
import sys
from pathlib import Path

# No Colab, baixa o repositório do tutorial e instala o birt-gd (β3-IRT); localmente, encontra a raiz.
if "google.colab" in sys.modules:
    ROOT = Path("/content/latent-ability-ml")
    if not ROOT.exists():
        subprocess.check_call(["git", "clone", "-q", "https://github.com/manuelfjr/latent-ability-ml.git", str(ROOT)])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "birt-gd"])
else:
    ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "utils" / "handson.py").exists())

sys.path.insert(0, str(ROOT))
print("Raiz do projeto:", ROOT)
"""


EXTRA_INTRO = (
    "Para quem terminou antes ou quer continuar depois. Estas tarefas não contam no tempo do hands-on "
    "e usam os objetos das tarefas anteriores."
)


def task_labels(part: dict) -> list[str]:
    """Tarefa 1, 2, …; "Livre" for the open task; "Extra 1, 2, …" for the bonus block."""
    labels, extra = [], 0
    for index, task in enumerate(part["tasks"], 1):
        if task.get("extra"):
            extra += 1
            labels.append(f"Extra {extra}")
        else:
            labels.append("Livre" if task.get("optional") else f"Tarefa {index}")
    return labels


def site_data(part: dict, number: int) -> dict:
    return {
        "number": number,
        "title": part["title"],
        "minutes": part["minutes"],
        "goal": part["goal"],
        "notebook": f"0{number}_{part['key']}_atividade.ipynb",
        "answer_notebook": f"0{number}_{part['key']}_respostas.ipynb",
        "extra_intro": EXTRA_INTRO,
        "tasks": [
            {
                "id": f"{part['key']}-t{index}",
                "title": task["title"],
                "minutes": task["minutes"],
                "optional": bool(task.get("optional")),
                "extra": bool(task.get("extra")),
                "badge": f"E{label.split()[-1]}" if task.get("extra") else "",
                "do": task["do"],
                "question": task["question"],
                "explore": task.get("explore", ""),
                "code": task["code"],
                "hints": task["hints"],
                "answer": task["answer"],
                "solution": task.get("solution", ""),
            }
            for index, (task, label) in enumerate(zip(part["tasks"], task_labels(part)), 1)
        ],
    }


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text.rstrip("\n").splitlines(keepends=True)}


def notebook(part: dict, number: int, answers: bool) -> dict:
    suffix = " (gabarito)" if answers else ""
    cells = [
        md(f"# Parte {number} · {part['title']}{suffix}\n\n**Avaliação com habilidade latente · Instituto Kunumi**\n\n{part['goal']}"),
        md(
            "**Execute a célula de preparação primeiro.** Depois siga as tarefas em ordem. O código já está pronto: "
            "execute, observe e escreva a sua análise. Mude o que quiser para testar hipóteses; as funções de "
            "`utils/handson.py` estão documentadas (`help(funcao)` ou Shift + Tab no Jupyter e no Colab)."
        ),
        code(SETUP),
        code(THEME),
    ]
    for task, label in zip(part["tasks"], task_labels(part)):
        if task.get("extra") and label == "Extra 1":
            cells.append(md(f"# Para ir além\n\n{EXTRA_INTRO}"))
        explore = f"\n\n**Para explorar.** {task['explore']}" if task.get("explore") else ""
        heading = task["title"] if label == "Livre" else f"{label} · {task['title']}"
        cells.append(md(f"## {heading} (~{task['minutes']} min)\n\n{task['do']}\n\n**Pergunta.** {task['question']}{explore}"))
        cells.append(code((task.get("solution") or task["code"]) if answers else task["code"]))
        cells.append(md(f"**Gabarito.** {task['answer']}" if answers else "*Sua análise:* "))
    if part.get("epilogue"):
        cells.append(md(part["epilogue"]))
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def helper_summaries() -> str:
    """One line per public helper in utils/handson.py: signature and first docstring line."""
    import ast

    tree = ast.parse(HELPERS.read_text(encoding="utf-8"))
    lines = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
            doc = (ast.get_docstring(node) or "").split("\n")[0]
            args = ", ".join(a.arg for a in node.args.args) if isinstance(node, ast.FunctionDef) else ""
            lines.append(f"- `{node.name}({args})`: {doc}")
    return "\n".join(lines)


def chat_context() -> str:
    """Reference material for the tutorial assistant (backend/chat.py)."""
    claire = json.loads((DATA_DIR / "claire.json").read_text(encoding="utf-8"))
    out = ["# Material do tutorial", ""]
    for number, part in enumerate(PARTS, 1):
        out += [f"## Parte {number} · {part['title']} (~{part['minutes']} min)", "", part["goal"], ""]
        for task, label in zip(part["tasks"], task_labels(part)):
            out += [
                f"### {task['title'] if label == 'Livre' else label + ' · ' + task['title']}",
                f"Enunciado: {task['do']}",
                f"Pergunta: {task['question']}",
                *( [f"Para explorar: {task['explore']}"] if task.get("explore") else [] ),
                "Código:",
                "```python",
                task["code"].rstrip(),
                "```",
                f"Gabarito (uma leitura possível): {task['answer']}",
                "",
            ]
    out += [
        "## Demonstração do CLAIRE (fim da Parte 2, sem exercício)",
        f"{claire['n_points']} pontos em três grupos de dispersões diferentes, {claire['n_models']} algoritmos de agrupamento. "
        "A concordância entre partições vira uma matriz de respostas contínuas e o β4-IRT estima a habilidade de cada "
        f"algoritmo e a dificuldade de cada ponto, sem rótulos. Correlação de Spearman entre habilidade CLAIRE e ARI: "
        f"{claire['spearman_ari']}; entre habilidade e silhueta: {claire['spearman_silhouette']}.",
        "Referência: Ferreira-Junior et al. (2025), CLAIRE, Machine Learning 114, 256. doi:10.1007/s10994-025-06911-0",
        "",
        "## Funções disponíveis (utils/handson.py)",
        helper_summaries(),
        "",
    ]
    return "\n".join(out)


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NB_DIR.mkdir(parents=True, exist_ok=True)
    for stale in NB_DIR.glob("*.ipynb"):
        stale.unlink()
    (DATA_DIR / "theme.json").write_text(json.dumps({"code": THEME}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for number, part in enumerate(PARTS, 1):
        data = site_data(part, number)
        (DATA_DIR / f"{part['key']}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for answers, name in ((False, data["notebook"]), (True, data["answer_notebook"])):
            content = json.dumps(notebook(part, number, answers), indent=1, ensure_ascii=False) + "\n"
            (NB_DIR / name).write_text(content, encoding="utf-8")
    CHAT_CONTEXT.write_text(chat_context(), encoding="utf-8")
    print("dados:", sorted(p.name for p in DATA_DIR.glob("*.json")))
    print("notebooks:", sorted(p.name for p in NB_DIR.glob("*.ipynb")))


if __name__ == "__main__":
    main()
