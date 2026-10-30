"""Tarefas do tutorial no ITA: fonte única das páginas do site e dos notebooks.

Depois de editar, rode a partir da raiz do repositório:

    python notebooks/ita/build_material.py
"""

# Tema dos gráficos (paleta Instituto Kunumi). Executado antes da primeira tarefa,
# tanto no site (backend ou navegador) quanto nos notebooks.
THEME = """import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams.update({
    "figure.figsize": (7, 4),
    "figure.dpi": 110,
    "figure.facecolor": "#F0F0F0",
    "axes.facecolor": "#F0F0F0",
    "savefig.facecolor": "#F0F0F0",
    "axes.edgecolor": "#B4ADA4",
    "axes.labelcolor": "#1C2127",
    "axes.titlecolor": "#1C2127",
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#B4ADA4",
    "grid.alpha": 0.35,
    "xtick.color": "#5E5E5E",
    "ytick.color": "#5E5E5E",
    "text.color": "#1C2127",
    "legend.frameon": False,
    "lines.linewidth": 2.6,
    "axes.prop_cycle": mpl.cycler(color=["#F04E44", "#4392D2", "#2FB7CF", "#62CCA3", "#F0D449"]),
})
"""

PARTE_1 = {
    "key": "parte1",
    "title": "Nem todo exemplo é igualmente difícil",
    "minutes": 15,
    "goal": "Três classificadores com quase a mesma acurácia erram justamente nos mesmos poucos exemplos. A tabela de acertos e erros que aparece aqui é a matéria-prima da IRT.",
    "tasks": [
        {
            "title": "Olhe os dados",
            "minutes": 2,
            "do": "Execute a célula. Ela gera um problema de classificação com duas classes.",
            "question": "Onde as duas classes se misturam? Quais pontos você acha que um modelo vai errar?",
            "code": "from utils.handson import make_toy_classification_dataset\n\ndf = make_toy_classification_dataset(n_samples=300, class_sep=1.4, random_state=56)\n\nfig, ax = plt.subplots()\nfor label, grupo in df.groupby(\"label\"):\n    ax.scatter(grupo.feature_1, grupo.feature_2, s=18, alpha=0.8, label=f\"classe {label}\")\nax.set_title(\"Duas classes\")\nax.legend()\nplt.show()\n",
            "hints": [
                "Procure a faixa onde pontos vermelhos e azuis aparecem lado a lado.",
                "É nessa faixa de fronteira que os rótulos ficam ambíguos.",
            ],
            "answer": "As duas nuvens se encostam numa faixa no meio do gráfico. Os pontos nessa fronteira são os candidatos naturais a erro, para qualquer modelo.",
        },
        {
            "title": "Treine três modelos",
            "minutes": 3,
            "do": "Execute. A célula treina uma árvore de decisão, um k-vizinhos e uma regressão logística e mostra a acurácia de cada um no teste.",
            "question": "Qual modelo ganhou? A diferença é grande o suficiente para importar?",
            "code": "from utils.handson import evaluate_models_on_dataset, summarize_classification_results\n\nresultados = evaluate_models_on_dataset(df, scenario=\"ita\", random_state=56)\n\nsummarize_classification_results(resultados).set_index(\"model\")[[\"accuracy\"]].round(3)\n",
            "hints": [
                "Compare as três acurácias: estão a cerca de 2 pontos percentuais uma da outra.",
            ],
            "answer": "As três acurácias ficam entre 0,92 e 0,94. Só por essa tabela, os modelos parecem intercambiáveis — e ela não diz em quais exemplos cada um erra.",
        },
        {
            "title": "Quem acertou o quê?",
            "minutes": 3,
            "do": "Execute. Cada linha é um modelo e cada coluna é um exemplo de teste: `1` é acerto, `0` é erro. Aparecem só os 12 primeiros exemplos.",
            "question": "Encontre um exemplo que todos acertam e um exemplo em que os modelos discordam.",
            "code": "respostas = resultados.pivot(index=\"model\", columns=\"example_id\", values=\"correct\")\n\nprint(respostas.shape, \"→ (modelos, exemplos de teste)\")\nrespostas.iloc[:, :12]\n",
            "hints": [
                "Uma coluna só com `1` é um exemplo que todo mundo resolve.",
                "Procure uma coluna que misture `0` e `1`.",
            ],
            "answer": "Quase todas as colunas são só `1`. Algumas misturam `0` e `1`: já nas primeiras colunas há exemplos que só a árvore erra e um que só a árvore acerta. Essa tabela (modelos × exemplos, acerto/erro) é exatamente a entrada da IRT.",
        },
        {
            "title": "Meça a dificuldade",
            "minutes": 3,
            "do": "A dificuldade de um exemplo pode ser medida como a fração de modelos que erraram. Execute para listar os mais difíceis.",
            "question": "Quantos exemplos todos os modelos erram? E quantos ninguém erra?",
            "code": "dificuldade = 1 - respostas.mean(axis=0)   # fração de modelos que erraram\n\nprint(\"errados por todos:  \", int((dificuldade == 1).sum()))\nprint(\"errados por ninguém:\", int((dificuldade == 0).sum()))\ndificuldade.sort_values(ascending=False).head(8).round(2)\n",
            "hints": [
                "`respostas.mean(axis=0)` é a média de cada coluna: a fração de modelos que acertaram aquele exemplo.",
            ],
            "answer": "Cerca de 80 dos 90 exemplos têm dificuldade 0 e 2 são errados por todos. Quase toda a informação que separa os modelos vem de uns dez exemplos.",
        },
        {
            "title": "Veja onde eles estão",
            "minutes": 3,
            "do": "Execute para destacar, no mapa, os exemplos que pelo menos um modelo errou.",
            "question": "Os exemplos difíceis estão espalhados ao acaso ou concentrados em alguma região?",
            "code": "dificeis = dificuldade[dificuldade > 0].index\nteste = df[df.example_id.isin(respostas.columns)]\nfacil = teste[~teste.example_id.isin(dificeis)]\ndificil = teste[teste.example_id.isin(dificeis)]\n\nfig, ax = plt.subplots()\nfor label, cor in [(0, \"#B4ADA4\"), (1, \"#5E5E5E\")]:\n    grupo = facil[facil.label == label]\n    ax.scatter(grupo.feature_1, grupo.feature_2, s=16, color=cor, label=f\"classe {label}: todos acertam\")\nax.scatter(dificil.feature_1, dificil.feature_2, s=90, color=\"#F04E44\", label=\"algum modelo erra\")\nax.set_title(\"Onde os modelos erram\")\nax.legend()\nplt.show()\n",
            "hints": [
                "Compare com o gráfico da tarefa 1.",
            ],
            "answer": "Os exemplos difíceis ficam na faixa em que as duas nuvens se encontram. Dificuldade é uma propriedade do exemplo — não é ruído aleatório.",
        },
        {
            "title": "Desafio: deixe o problema mais difícil",
            "minutes": 3,
            "optional": True,
            "do": "Esta célula refaz tudo de uma vez. Mude `class_sep` de `1.4` para `0.6` e execute.",
            "question": "O que acontece com o número de exemplos difíceis e com a diferença entre os modelos?",
            "code": "class_sep = 1.4   # <- mude aqui\n\ndados = make_toy_classification_dataset(n_samples=300, class_sep=class_sep, random_state=56)\nres = evaluate_models_on_dataset(dados, scenario=\"desafio\", random_state=56)\ntabela = res.pivot(index=\"model\", columns=\"example_id\", values=\"correct\")\n\nprint(\"exemplos difíceis:\", int((tabela.mean(axis=0) < 1).sum()), \"de\", tabela.shape[1])\ntabela.mean(axis=1).round(3).rename(\"acurácia\")\n",
            "hints": [
                "Com `class_sep` menor, as classes se sobrepõem mais.",
            ],
            "answer": "Com `class_sep = 0.6` os exemplos difíceis passam de 11 para cerca de 36 e as acurácias caem para perto de 0,77. Com tanta sobreposição, quase todo exemplo da fronteira vira um teste para os modelos.",
        },
    ],
}

PARTE_2 = {
    "key": "parte2",
    "title": "Lendo curvas da IRT",
    "minutes": 20,
    "goal": "Um parâmetro de cada vez: a dificuldade move a curva, a discriminação muda a inclinação, e as duas juntas decidem quais itens separam modelos fortes de fracos.",
    "tasks": [
        {
            "title": "Um item, uma curva",
            "minutes": 3,
            "do": "Execute. A curva característica do item (CCI) dá a probabilidade de acerto para cada habilidade θ.",
            "question": "Por que a probabilidade é exatamente 0,5 quando a habilidade é igual à dificuldade?",
            "code": "import numpy as np\nfrom utils.handson import binary_irt_probability\n\ntheta = np.linspace(-3, 3, 200)   # habilidade latente\np = binary_irt_probability(theta, difficulty=0.0, discrimination=1.0)\n\nfig, ax = plt.subplots()\nax.plot(theta, p)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Uma curva característica do item\")\nplt.show()\n\nprint(\"P(acerto) com θ = 0:\", binary_irt_probability(0.0, difficulty=0.0, discrimination=1.0))\n",
            "hints": [
                "O modelo 2PL é P = 1 / (1 + exp(−a(θ − δ))).",
                "Com θ = δ o expoente vale zero, e 1 / (1 + 1) = 0,5.",
            ],
            "answer": "Em P = 1 / (1 + exp(−a(θ − δ))), θ = δ zera o expoente e P = 1/2. A dificuldade é a habilidade em que acertar vira cara ou coroa.",
        },
        {
            "title": "A dificuldade move a curva",
            "minutes": 3,
            "do": "Execute para ver três itens que só diferem na dificuldade. Depois acrescente `2.0` à lista e execute de novo.",
            "question": "Qual item é o mais difícil? Como você percebe isso só olhando?",
            "code": "dificuldades = [-1.0, 0.0, 1.0]   # <- acrescente 2.0\n\nfig, ax = plt.subplots()\nfor d in dificuldades:\n    ax.plot(theta, binary_irt_probability(theta, difficulty=d, discrimination=1.0), label=f\"δ = {d}\")\nax.axhline(0.5, color=\"#B4ADA4\", linestyle=\"--\", linewidth=1)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Mesma forma, posições diferentes\")\nax.legend()\nplt.show()\n",
            "hints": [
                "Todas as curvas têm a mesma forma: só a posição muda.",
                "Veja onde cada curva cruza a linha tracejada de 0,5.",
            ],
            "answer": "Aumentar a dificuldade desloca a curva para a direita. O item mais difícil é o mais à direita: exige mais habilidade para a probabilidade subir.",
        },
        {
            "title": "A discriminação muda a inclinação",
            "minutes": 3,
            "do": "Agora a dificuldade fica fixa em `0` e só a discriminação muda. Execute e depois acrescente `5.0` à lista.",
            "question": "Qual curva separa melhor alguém com θ = −0,5 de alguém com θ = 0,5?",
            "code": "discriminacoes = [0.5, 1.0, 3.0]   # <- acrescente 5.0\n\nfig, ax = plt.subplots()\nfor a in discriminacoes:\n    ax.plot(theta, binary_irt_probability(theta, difficulty=0.0, discrimination=a), label=f\"a = {a}\")\nax.axvspan(-0.5, 0.5, color=\"#B4ADA4\", alpha=0.25)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Mesmo ponto central, inclinações diferentes\")\nax.legend()\nplt.show()\n",
            "hints": [
                "Todas cruzam 0,5 no mesmo ponto: a dificuldade não mudou.",
                "Olhe quanto cada curva sobe dentro da faixa cinza.",
            ],
            "answer": "A curva mais inclinada (maior discriminação) sai de baixo para cima dentro da faixa cinza, então separa bem habilidades próximas. Uma curva achatada quase não distingue as duas.",
        },
        {
            "title": "Probabilidades numa tabela",
            "minutes": 3,
            "do": "Execute. A tabela mostra a probabilidade de acerto de três respondentes (linhas) em três itens (colunas).",
            "question": "Qual item separa melhor o respondente com θ = 0 do respondente com θ = 1?",
            "code": "import pandas as pd\n\nitens = {                # nome: (dificuldade, discriminação)\n    \"fácil\":   (-1.0, 1.0),\n    \"médio\":   (0.0, 1.0),\n    \"difícil\": (1.0, 2.0),\n}\nhabilidades = np.array([-1.0, 0.0, 1.0])\n\ntabela = pd.DataFrame(\n    {nome: binary_irt_probability(habilidades, d, a) for nome, (d, a) in itens.items()},\n    index=[f\"θ = {t:+.0f}\" for t in habilidades],\n)\ntabela.round(2)\n",
            "hints": [
                "Em cada coluna, compare a linha θ = +0 com a linha θ = +1.",
                "O item com o maior salto entre essas duas linhas é o que mais separa os dois.",
            ],
            "answer": "O item *difícil* salta de 0,12 para 0,50 entre θ = 0 e θ = 1: sua dificuldade está nessa faixa e ele é o mais discriminativo. O item fácil já está perto de 1 para os dois.",
        },
        {
            "title": "Uma curva ao contrário",
            "minutes": 3,
            "do": "Execute. O item tem discriminação negativa.",
            "question": "Numa avaliação de modelos, o que significaria um exemplo se comportar assim?",
            "code": "p = binary_irt_probability(theta, difficulty=0.0, discrimination=-1.5)\n\nfig, ax = plt.subplots()\nax.plot(theta, p)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Discriminação negativa\")\nplt.show()\n",
            "hints": [
                "Aqui, quem tem mais habilidade acerta *menos*.",
                "Pense num exemplo com rótulo errado no conjunto de teste.",
            ],
            "answer": "Modelos melhores erram mais esse exemplo. Na prática, isso sinaliza um exemplo suspeito — por exemplo, com rótulo errado: o modelo bom acerta a classe verdadeira e é contado como erro.",
        },
        {
            "title": "Desafio: projete um item",
            "minutes": 5,
            "optional": True,
            "do": "Escolha dificuldade e discriminação para que o item separe um modelo fraco (θ = 0) de um forte (θ = 1): o fraco deve acertar no máximo 30% das vezes e o forte pelo menos 90%.",
            "question": "Que combinação funcionou? Por que você precisou mexer nos dois parâmetros?",
            "code": "dificuldade = 0.0      # <- mude aqui\ndiscriminacao = 1.0    # <- e aqui\n\nfraco, forte = binary_irt_probability(np.array([0.0, 1.0]), dificuldade, discriminacao)\nprint(f\"modelo fraco (θ=0): {fraco:.2f}   modelo forte (θ=1): {forte:.2f}\")\nprint(\"Conseguiu!\" if fraco <= 0.30 and forte >= 0.90 else \"Ainda não: busque fraco ≤ 0,30 e forte ≥ 0,90\")\n",
            "solution": "dificuldade = 0.5\ndiscriminacao = 5.0\n\nfraco, forte = binary_irt_probability(np.array([0.0, 1.0]), dificuldade, discriminacao)\nprint(f\"modelo fraco (θ=0): {fraco:.2f}   modelo forte (θ=1): {forte:.2f}\")\nprint(\"Conseguiu!\" if fraco <= 0.30 and forte >= 0.90 else \"Ainda não: busque fraco ≤ 0,30 e forte ≥ 0,90\")\n",
            "hints": [
                "Coloque a dificuldade entre as duas habilidades, por exemplo perto de 0,5.",
                "Depois aumente a discriminação até a curva ficar íngreme o suficiente entre θ = 0 e θ = 1.",
            ],
            "answer": "Por exemplo, dificuldade 0,5 e discriminação 5 dão cerca de 0,08 para o fraco e 0,92 para o forte. A dificuldade posiciona a transição entre os dois modelos; a discriminação deixa essa transição abrupta o bastante.",
        },
    ],
}

PARTS = [PARTE_1, PARTE_2]
