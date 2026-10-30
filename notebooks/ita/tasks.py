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
    "goal": "Três classificadores com acurácias praticamente iguais. A pergunta é onde cada um erra, e a resposta já tem a forma da matriz de respostas da IRT.",
    "tasks": [
        {
            "title": "Olhe os dados",
            "minutes": 2,
            "do": "Gere um problema sintético de classificação binária em duas dimensões com `make_toy_classification_dataset`: 300 pontos, `class_sep=1.4` e `random_state=56`. Complete as lacunas `___` e execute.",
            "question": "Antes de treinar qualquer modelo: em que região você espera erros, e por quê?",
            "code": "from utils.handson import make_toy_classification_dataset, plot_classification_dataset\n\n# 300 pontos, class_sep=1.4, random_state=56\ndf = make_toy_classification_dataset(n_samples=___, class_sep=___, random_state=___)\n\nax = plot_classification_dataset(df)\nax.set_title(\"Duas classes\")\nplt.show()\n",
            "solution": "from utils.handson import make_toy_classification_dataset, plot_classification_dataset\n\n# 300 pontos, class_sep=1.4, random_state=56\ndf = make_toy_classification_dataset(n_samples=300, class_sep=1.4, random_state=56)\n\nax = plot_classification_dataset(df)\nax.set_title(\"Duas classes\")\nplt.show()\n",
            "hints": [
                "Passe o mouse sobre `make_toy_classification_dataset` para ver o que cada argumento faz.",
                "No gráfico, procure a faixa onde pontos das duas classes aparecem lado a lado.",
                "É nessa faixa de fronteira que os rótulos ficam ambíguos.",
            ],
            "answer": "Na faixa em que as duas nuvens se sobrepõem. Ali P(y ∣ x) fica perto de 1/2 e parte do erro é irredutível (erro de Bayes): nenhum classificador acerta esses pontos de forma sistemática.",
        },
        {
            "title": "Treine três modelos",
            "minutes": 3,
            "do": "Treine três classificadores com vieses indutivos diferentes (árvore de decisão, k-vizinhos e regressão logística) com `evaluate_models_on_dataset`, que reserva 30% dos dados (90 exemplos) para teste. Passe o `df` da tarefa anterior e mostre a coluna `\"accuracy\"` do resumo.",
            "question": "A diferença justificaria escolher um dos modelos? O que essa tabela não informa?",
            "code": "from utils.handson import evaluate_models_on_dataset, summarize_classification_results\n\n# Treina os três classificadores; devolve uma linha por (modelo, exemplo de teste)\nresultados = evaluate_models_on_dataset(___, scenario=\"ita\", random_state=56)\nprint(\"colunas:\", resultados.columns.tolist())\n\n# Uma linha por modelo: mostre só a coluna de acurácia\nsummarize_classification_results(resultados).set_index(\"model\")[[___]].round(3)\n",
            "solution": "from utils.handson import evaluate_models_on_dataset, summarize_classification_results\n\n# Treina os três classificadores; devolve uma linha por (modelo, exemplo de teste)\nresultados = evaluate_models_on_dataset(df, scenario=\"ita\", random_state=56)\nprint(\"colunas:\", resultados.columns.tolist())\n\n# Uma linha por modelo: mostre só a coluna de acurácia\nsummarize_classification_results(resultados).set_index(\"model\")[[\"accuracy\"]].round(3)\n",
            "hints": [
                "A primeira lacuna é o conjunto de dados; a segunda é o nome da coluna, entre aspas.",
                "Com 90 exemplos de teste, quantos exemplos são 2 pontos percentuais?",
            ],
            "answer": "As acurácias ficam entre 0,92 e 0,94. Com 90 exemplos, 2 pontos percentuais são 2 exemplos, dentro do ruído amostral. E um escalar por modelo não diz *quais* exemplos foram errados nem se os modelos erram nos mesmos lugares.",
        },
        {
            "title": "Quem acertou o quê?",
            "minutes": 3,
            "do": "Reorganize o resultado longo como matriz binária com `DataFrame.pivot`: modelos (`model`) nas linhas, exemplos de teste (`example_id`) nas colunas e acerto (`correct`: `1` acerto, `0` erro) nas células. Aparecem as 12 primeiras colunas.",
            "question": "Que tipo de coluna ajuda a comparar os modelos, e que tipo não ajuda?",
            "code": "# Modelos nas linhas, exemplos de teste nas colunas, acerto (1) ou erro (0) nas células\nrespostas = resultados.pivot(index=___, columns=___, values=___)\n\nprint(respostas.shape, \"→ (modelos, exemplos de teste)\")\nrespostas.iloc[:, :12]\n",
            "solution": "# Modelos nas linhas, exemplos de teste nas colunas, acerto (1) ou erro (0) nas células\nrespostas = resultados.pivot(index=\"model\", columns=\"example_id\", values=\"correct\")\n\nprint(respostas.shape, \"→ (modelos, exemplos de teste)\")\nrespostas.iloc[:, :12]\n",
            "hints": [
                "`pivot(index=\"model\", columns=\"example_id\", values=\"correct\")`.",
                "Uma coluna só com `1` é um exemplo que todo mundo resolve.",
                "Procure uma coluna que misture `0` e `1`.",
            ],
            "answer": "Colunas constantes (todos acertam ou todos erram) não distinguem os modelos; só as colunas mistas carregam informação. Esta matriz respondente × item com respostas dicotômicas é a entrada de um modelo de IRT: os modelos fazem o papel de alunos, e os exemplos, o de questões de uma prova.",
        },
        {
            "title": "Meça a dificuldade",
            "minutes": 3,
            "do": "Uma primeira medida de dificuldade, sem modelo latente: a fração de classificadores que erra cada exemplo (o análogo do índice de dificuldade da teoria clássica dos testes). Escreva-a a partir de `respostas`, em uma linha.",
            "question": "Quantos exemplos de fato diferenciam os modelos? O que isso diz sobre o tamanho efetivo do teste?",
            "code": "dificuldade = ___   # fração de modelos que erraram cada exemplo (uma série indexada por example_id)\n\nprint(\"errados por todos:  \", int((dificuldade == 1).sum()))\nprint(\"errados por ninguém:\", int((dificuldade == 0).sum()))\ndificuldade.sort_values(ascending=False).head(8).round(2)\n",
            "solution": "dificuldade = 1 - respostas.mean(axis=0)   # fração de modelos que erraram cada exemplo\n\nprint(\"errados por todos:  \", int((dificuldade == 1).sum()))\nprint(\"errados por ninguém:\", int((dificuldade == 0).sum()))\ndificuldade.sort_values(ascending=False).head(8).round(2)\n",
            "hints": [
                "`respostas.mean(axis=0)` é a média de cada coluna: a fração de modelos que acertaram aquele exemplo.",
                "A fração que errou é o complemento: `1 - respostas.mean(axis=0)`.",
            ],
            "answer": "79 dos 90 exemplos são acertados por todos e 2 são errados por todos; sobram 9 exemplos informativos. A comparação entre os modelos é decidida por menos de uma dezena de itens: o tamanho efetivo do teste é muito menor que 90.",
        },
        {
            "title": "Veja onde eles estão",
            "minutes": 3,
            "do": "Destaque, no plano das features, os exemplos de teste que pelo menos um modelo errou. Complete o filtro sobre `dificuldade`; o gráfico já está pronto.",
            "question": "A dificuldade parece uma propriedade do exemplo ou ruído? Que limitação tem a medida da tarefa anterior?",
            "code": "dificeis = dificuldade[___].index   # exemplos que pelo menos um modelo errou\nteste = df[df.example_id.isin(respostas.columns)]\nfacil = teste[~teste.example_id.isin(dificeis)]\ndificil = teste[teste.example_id.isin(dificeis)]\n\nfig, ax = plt.subplots()\nfor label, cor in [(0, \"#B4ADA4\"), (1, \"#5E5E5E\")]:\n    grupo = facil[facil.label == label]\n    ax.scatter(grupo.feature_1, grupo.feature_2, s=16, color=cor, label=f\"classe {label}: todos acertam\")\nax.scatter(dificil.feature_1, dificil.feature_2, s=90, color=\"#F04E44\", label=\"algum modelo erra\")\nax.set_title(\"Onde os modelos erram\")\nax.legend()\nplt.show()\n",
            "solution": "dificeis = dificuldade[dificuldade > 0].index   # exemplos que pelo menos um modelo errou\nteste = df[df.example_id.isin(respostas.columns)]\nfacil = teste[~teste.example_id.isin(dificeis)]\ndificil = teste[teste.example_id.isin(dificeis)]\n\nfig, ax = plt.subplots()\nfor label, cor in [(0, \"#B4ADA4\"), (1, \"#5E5E5E\")]:\n    grupo = facil[facil.label == label]\n    ax.scatter(grupo.feature_1, grupo.feature_2, s=16, color=cor, label=f\"classe {label}: todos acertam\")\nax.scatter(dificil.feature_1, dificil.feature_2, s=90, color=\"#F04E44\", label=\"algum modelo erra\")\nax.set_title(\"Onde os modelos erram\")\nax.legend()\nplt.show()\n",
            "hints": [
                "O filtro é uma condição booleana: `dificuldade > 0`.",
                "Compare com o gráfico da tarefa 1.",
                "Na fração de erros, o erro de um modelo forte e o de um fraco valem o mesmo?",
            ],
            "answer": "Os exemplos difíceis se concentram na região de sobreposição: dificuldade é uma propriedade do exemplo. A limitação é que a fração de erros trata todos os modelos como equivalentes: errar um exemplo que só o pior modelo erra pesa o mesmo que errar um que derruba o melhor. A IRT resolve isso estimando, ao mesmo tempo, a habilidade de cada modelo e a dificuldade de cada exemplo.",
        },
        {
            "title": "Desafio: deixe o problema mais difícil",
            "minutes": 3,
            "optional": True,
            "do": "Esta célula refaz tudo de uma vez. Mude `class_sep` de `1.4` para `0.6` e execute.",
            "question": "O que acontece com o número de exemplos informativos e com a separação entre os modelos?",
            "code": "class_sep = 1.4   # <- mude aqui\n\ndados = make_toy_classification_dataset(n_samples=300, class_sep=class_sep, random_state=56)\nres = evaluate_models_on_dataset(dados, scenario=\"desafio\", random_state=56)\ntabela = res.pivot(index=\"model\", columns=\"example_id\", values=\"correct\")\n\nprint(\"exemplos difíceis:\", int((tabela.mean(axis=0) < 1).sum()), \"de\", tabela.shape[1])\ntabela.mean(axis=1).round(3).rename(\"acurácia\")\n",
            "solution": "class_sep = 0.6   # <- mude aqui\n\ndados = make_toy_classification_dataset(n_samples=300, class_sep=class_sep, random_state=56)\nres = evaluate_models_on_dataset(dados, scenario=\"desafio\", random_state=56)\ntabela = res.pivot(index=\"model\", columns=\"example_id\", values=\"correct\")\n\nprint(\"exemplos difíceis:\", int((tabela.mean(axis=0) < 1).sum()), \"de\", tabela.shape[1])\ntabela.mean(axis=1).round(3).rename(\"acurácia\")\n",
            "hints": [
                "Com `class_sep` menor, as classes se sobrepõem mais.",
            ],
            "answer": "Com `class_sep = 0.6`, os exemplos que algum modelo erra passam de 11 para cerca de 36 e as acurácias caem para perto de 0,77. O teste fica mais informativo, mas também mais ruidoso. É nesse regime que um modelo latente compensa: ele separa o que é habilidade do modelo do que é dificuldade do exemplo.",
        },
    ],
}

PARTE_2 = {
    "key": "parte2",
    "title": "Lendo curvas da IRT",
    "minutes": 20,
    "goal": "O modelo logístico de dois parâmetros (2PL), um parâmetro por vez: a dificuldade δ posiciona a curva, a discriminação a controla a inclinação, e as duas juntas determinam quais itens separam modelos fortes de fracos.",
    "tasks": [
        {
            "title": "Um item, uma curva",
            "minutes": 3,
            "do": "No 2PL, a probabilidade de um respondente com habilidade θ acertar o item j é P(θ) = 1 / (1 + exp(−aⱼ(θ − δⱼ))). Use `binary_irt_probability` para traçar a curva característica do item (CCI) com δ = 0 e a = 1.",
            "question": "Por que P = 0,5 exatamente quando θ = δ? Que interpretação isso dá a δ?",
            "code": "import numpy as np\nfrom utils.handson import binary_irt_probability\n\ntheta = np.linspace(-3, 3, 200)   # habilidade latente\np = binary_irt_probability(theta, difficulty=___, discrimination=___)   # δ = 0, a = 1\n\nfig, ax = plt.subplots()\nax.plot(theta, p)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Uma curva característica do item\")\nplt.show()\n\nprint(\"P(acerto) com θ = 0:\", binary_irt_probability(0.0, difficulty=0.0, discrimination=1.0))\n",
            "solution": "import numpy as np\nfrom utils.handson import binary_irt_probability\n\ntheta = np.linspace(-3, 3, 200)   # habilidade latente\np = binary_irt_probability(theta, difficulty=0.0, discrimination=1.0)   # δ = 0, a = 1\n\nfig, ax = plt.subplots()\nax.plot(theta, p)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Uma curva característica do item\")\nplt.show()\n\nprint(\"P(acerto) com θ = 0:\", binary_irt_probability(0.0, difficulty=0.0, discrimination=1.0))\n",
            "hints": [
                "O modelo 2PL é P = 1 / (1 + exp(−a(θ − δ))).",
                "Com θ = δ o expoente vale zero, e 1 / (1 + 1) = 0,5.",
            ],
            "answer": "Com θ = δ o expoente se anula e P = 1 / (1 + 1) = 1/2. A dificuldade é a habilidade em que acertar vira cara ou coroa. Como δ e θ estão na mesma escala, faz sentido dizer que um item é \"difícil para modelos desse nível\".",
        },
        {
            "title": "A dificuldade move a curva",
            "minutes": 3,
            "do": "Três itens que só diferem na dificuldade. Complete a chamada com a dificuldade da curva da vez, execute, acrescente `2.0` à lista e execute de novo.",
            "question": "Qual item é o mais difícil, e como isso se lê no gráfico? Para um θ fixo, o que muda?",
            "code": "dificuldades = [-1.0, 0.0, 1.0]   # <- acrescente 2.0\n\nfig, ax = plt.subplots()\nfor d in dificuldades:\n    ax.plot(theta, binary_irt_probability(theta, difficulty=___, discrimination=1.0), label=f\"δ = {d}\")\nax.axhline(0.5, color=\"#B4ADA4\", linestyle=\"--\", linewidth=1)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Mesma forma, posições diferentes\")\nax.legend()\nplt.show()\n",
            "solution": "dificuldades = [-1.0, 0.0, 1.0]   # <- acrescente 2.0\n\nfig, ax = plt.subplots()\nfor d in dificuldades:\n    ax.plot(theta, binary_irt_probability(theta, difficulty=d, discrimination=1.0), label=f\"δ = {d}\")\nax.axhline(0.5, color=\"#B4ADA4\", linestyle=\"--\", linewidth=1)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Mesma forma, posições diferentes\")\nax.legend()\nplt.show()\n",
            "hints": [
                "A variável do laço `d` é a dificuldade de cada curva.",
                "Todas as curvas têm a mesma forma: só a posição muda.",
                "Veja onde cada curva cruza a linha tracejada de 0,5.",
            ],
            "answer": "δ é um parâmetro de posição: aumentá-lo translada a CCI para a direita sem mudar sua forma. O item mais difícil é o mais à direita; para um θ fixo, sua probabilidade de acerto é a menor.",
        },
        {
            "title": "A discriminação muda a inclinação",
            "minutes": 3,
            "do": "Agora a dificuldade fica fixa em `0` e só a discriminação muda. Complete a chamada, execute e acrescente `5.0` à lista.",
            "question": "Qual curva separa melhor alguém com θ = −0,5 de alguém com θ = 0,5?",
            "code": "discriminacoes = [0.5, 1.0, 3.0]   # <- acrescente 5.0\n\nfig, ax = plt.subplots()\nfor a in discriminacoes:\n    ax.plot(theta, binary_irt_probability(theta, difficulty=0.0, discrimination=___), label=f\"a = {a}\")\nax.axvspan(-0.5, 0.5, color=\"#B4ADA4\", alpha=0.25)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Mesmo ponto central, inclinações diferentes\")\nax.legend()\nplt.show()\n",
            "solution": "discriminacoes = [0.5, 1.0, 3.0]   # <- acrescente 5.0\n\nfig, ax = plt.subplots()\nfor a in discriminacoes:\n    ax.plot(theta, binary_irt_probability(theta, difficulty=0.0, discrimination=a), label=f\"a = {a}\")\nax.axvspan(-0.5, 0.5, color=\"#B4ADA4\", alpha=0.25)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Mesmo ponto central, inclinações diferentes\")\nax.legend()\nplt.show()\n",
            "hints": [
                "A variável do laço `a` é a discriminação de cada curva.",
                "Todas cruzam 0,5 no mesmo ponto: a dificuldade não mudou.",
                "Olhe quanto cada curva sobe dentro da faixa cinza.",
            ],
            "answer": "A curva mais inclinada (maior a) vai de perto de 0 a perto de 1 dentro da faixa cinza, então separa bem habilidades próximas; uma curva achatada quase não as distingue. Formalmente, a inclinação em θ = δ vale a/4, e a informação de Fisher do item, a²·P(1 − P), é máxima ali: itens muito discriminativos medem com precisão, mas numa faixa estreita de habilidades.",
        },
        {
            "title": "Probabilidades numa tabela",
            "minutes": 3,
            "do": "Um banco com três itens (`make_binary_item_bank`), suas curvas (`plot_binary_iccs`) e a probabilidade de acerto de três respondentes (linhas) em cada item (colunas). Complete a tabela com os parâmetros de cada item.",
            "question": "Qual item separa melhor o respondente com θ = 0 do respondente com θ = 1?",
            "code": "import pandas as pd\nfrom utils.handson import make_binary_item_bank, plot_binary_iccs\n\nbanco = make_binary_item_bank([\n    {\"item\": \"fácil\",   \"difficulty\": -1.0, \"discrimination\": 1.0},\n    {\"item\": \"médio\",   \"difficulty\": 0.0,  \"discrimination\": 1.0},\n    {\"item\": \"difícil\", \"difficulty\": 1.0,  \"discrimination\": 2.0},\n])\nplot_binary_iccs(banco, theta=theta, title=\"Três itens\")\nplt.show()\n\nhabilidades = np.array([-1.0, 0.0, 1.0])\ntabela = pd.DataFrame(\n    {item.item: binary_irt_probability(habilidades, ___, ___) for item in banco.itertuples()},\n    index=[f\"θ = {t:+.0f}\" for t in habilidades],\n)\ntabela.round(2)\n",
            "solution": "import pandas as pd\nfrom utils.handson import make_binary_item_bank, plot_binary_iccs\n\nbanco = make_binary_item_bank([\n    {\"item\": \"fácil\",   \"difficulty\": -1.0, \"discrimination\": 1.0},\n    {\"item\": \"médio\",   \"difficulty\": 0.0,  \"discrimination\": 1.0},\n    {\"item\": \"difícil\", \"difficulty\": 1.0,  \"discrimination\": 2.0},\n])\nplot_binary_iccs(banco, theta=theta, title=\"Três itens\")\nplt.show()\n\nhabilidades = np.array([-1.0, 0.0, 1.0])\ntabela = pd.DataFrame(\n    {item.item: binary_irt_probability(habilidades, item.difficulty, item.discrimination) for item in banco.itertuples()},\n    index=[f\"θ = {t:+.0f}\" for t in habilidades],\n)\ntabela.round(2)\n",
            "hints": [
                "Cada `item` do laço tem os atributos `item.difficulty` e `item.discrimination`.",
                "Em cada coluna, compare a linha θ = +0 com a linha θ = +1.",
                "O item com o maior salto entre essas duas linhas é o que mais separa os dois.",
            ],
            "answer": "O item *difícil* salta de 0,12 para 0,50 entre θ = 0 e θ = 1: sua dificuldade está nessa faixa e ele é o mais discriminativo. O item fácil já está perto de 1 para os dois. O item mais útil depende de *quem* se quer comparar, e é isso que permite montar testes sob medida (testes adaptativos).",
        },
        {
            "title": "Uma curva ao contrário",
            "minutes": 3,
            "do": "Um item com discriminação negativa. Escolha um valor negativo para `a`, por exemplo −1,5.",
            "question": "Numa avaliação de modelos, o que um exemplo com essa curva sugere sobre os dados?",
            "code": "p = binary_irt_probability(theta, difficulty=0.0, discrimination=___)   # a < 0\n\nfig, ax = plt.subplots()\nax.plot(theta, p)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Discriminação negativa\")\nplt.show()\n",
            "solution": "p = binary_irt_probability(theta, difficulty=0.0, discrimination=-1.5)   # a < 0\n\nfig, ax = plt.subplots()\nax.plot(theta, p)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Discriminação negativa\")\nplt.show()\n",
            "hints": [
                "Aqui, quem tem mais habilidade acerta *menos*.",
                "Pense num exemplo com rótulo errado no conjunto de teste.",
            ],
            "answer": "Modelos melhores erram mais esse exemplo. Na prática, isso sinaliza um exemplo suspeito, tipicamente com rótulo errado: o modelo bom prevê a classe verdadeira e é contado como erro. A discriminação estimada funciona, assim, como um diagnóstico automático de qualidade dos dados.",
        },
        {
            "title": "Desafio: projete um item",
            "minutes": 5,
            "optional": True,
            "do": "Escolha δ e a para que o item separe um modelo fraco (θ = 0) de um forte (θ = 1): o fraco deve acertar no máximo 30% das vezes e o forte, pelo menos 90%.",
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

PARTE_2["epilogue"] = (
    "## Para ir além: e quando não há rótulos?\n\n"
    "Em agrupamento não existe acerto, então não há matriz de acertos. O **CLAIRE** troca acerto por "
    "*concordância*: para cada ponto i e algoritmo j, p_ij ∈ [0, 1] mede quanto j concorda com os demais "
    "sobre com quem i foi agrupado. Como essas respostas são contínuas, o β4-IRT estima a habilidade de "
    "cada algoritmo e a dificuldade de cada ponto, sem usar rótulo nenhum.\n\n"
    "A demonstração está no fim da Parte 2 no site (código em `notebooks/ita/claire_demo.py`). Referência: "
    "Ferreira-Junior et al. (2025), *CLAIRE: clustering evaluation based on item response theory and model "
    "agreement*, Machine Learning 114, 256. https://doi.org/10.1007/s10994-025-06911-0"
)

PARTS = [PARTE_1, PARTE_2]
