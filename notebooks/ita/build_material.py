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

SETUP = """import subprocess
import sys
from pathlib import Path

# No Colab, baixa o repositório do tutorial; localmente, encontra a raiz a partir desta pasta.
if "google.colab" in sys.modules:
    ROOT = Path("/content/latent-ability-ml")
    if not ROOT.exists():
        subprocess.check_call(["git", "clone", "-q", "https://github.com/manuelfjr/latent-ability-ml.git", str(ROOT)])
else:
    ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "utils" / "handson.py").exists())

sys.path.insert(0, str(ROOT))
print("Raiz do projeto:", ROOT)
"""


def site_data(part: dict, number: int) -> dict:
    return {
        "number": number,
        "title": part["title"],
        "minutes": part["minutes"],
        "goal": part["goal"],
        "notebook": f"0{number}_{part['key']}_atividade.ipynb",
        "answer_notebook": f"0{number}_{part['key']}_respostas.ipynb",
        "tasks": [
            {
                "id": f"{part['key']}-t{index}",
                "title": task["title"],
                "minutes": task["minutes"],
                "optional": bool(task.get("optional")),
                "do": task["do"],
                "question": task["question"],
                "code": task["code"],
                "hints": task["hints"],
                "answer": task["answer"],
                "solution": task.get("solution", ""),
            }
            for index, task in enumerate(part["tasks"], 1)
        ],
    }


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": text.rstrip("\n").splitlines(keepends=True)}


def notebook(part: dict, number: int, answers: bool) -> dict:
    suffix = " — respostas" if answers else ""
    cells = [
        md(f"# Parte {number} · {part['title']}{suffix}\n\n**Avaliação com habilidade latente · Instituto Kunumi**\n\n{part['goal']}"),
        md("**Execute a célula de preparação primeiro.** Depois siga as tarefas em ordem: em cada uma, mude *uma* coisa, observe o resultado e responda *uma* pergunta."),
        code(SETUP),
        code(THEME),
    ]
    for index, task in enumerate(part["tasks"], 1):
        label = "Desafio" if task.get("optional") else f"Tarefa {index}"
        cells.append(md(f"## {label} · {task['title']} (~{task['minutes']} min)\n\n{task['do']}\n\n**Pergunta.** {task['question']}"))
        cells.append(code((task.get("solution") or task["code"]) if answers else task["code"]))
        cells.append(md(f"**Resposta.** {task['answer']}" if answers else "*Sua resposta:* "))
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


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
    print("dados:", sorted(p.name for p in DATA_DIR.glob("*.json")))
    print("notebooks:", sorted(p.name for p in NB_DIR.glob("*.ipynb")))


if __name__ == "__main__":
    main()
