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

# Escala sequencial de um só tom (azul da paleta de dados) para mapas de dificuldade.
from matplotlib.colors import LinearSegmentedColormap

if "kunumi_azul" not in mpl.colormaps:
    mpl.colormaps.register(LinearSegmentedColormap.from_list("kunumi_azul", ["#B9D2EA", "#4392D2", "#14304F"]))
"""

PARTE_1 = {
    "key": "parte1",
    "title": "Nem todo exemplo é igualmente difícil",
    "minutes": 15,
    "goal": "Três classificadores com acurácias praticamente iguais. O código já está pronto: seu trabalho é observar, levantar hipóteses e interpretar onde e por que cada um erra.",
    "tasks": [
        {
            "title": "Olhe os dados antes dos modelos",
            "minutes": 2,
            "do": "Um problema sintético de classificação binária em duas dimensões, com 300 pontos. Execute e observe.",
            "question": "Antes de treinar qualquer modelo: em que região você espera erros, e por quê? Anote a sua hipótese; vamos voltar a ela.",
            "explore": "Algum ponto parece estar \"do lado errado\"? Que explicações diferentes poderiam existir para ele estar ali?",
            "code": "from utils.handson import make_toy_classification_dataset, plot_classification_dataset\n\ndf = make_toy_classification_dataset(n_samples=300, class_sep=1.4, random_state=56)\n\nax = plot_classification_dataset(df)\nax.set_title(\"Duas classes\")\nplt.show()\n",
            "hints": ["Procure a faixa em que pontos das duas classes aparecem lado a lado.", "Um ponto isolado dentro da nuvem da outra classe pode ser ruído de rótulo, e não fronteira."],
            "answer": "Uma leitura possível: os erros devem se concentrar na faixa de sobreposição entre as nuvens, onde P(y ∣ x) fica perto de 1/2 e parte do erro é irredutível (erro de Bayes). Pontos isolados no meio da outra classe são outra história: o gerador troca 2% dos rótulos ao acaso, e esses pontos tendem a ser errados por todos os modelos, por melhores que sejam.",
        },
        {
            "title": "Três modelos, quase o mesmo número",
            "minutes": 3,
            "do": "Árvore de decisão, k-vizinhos e regressão logística, avaliados nos mesmos 90 exemplos de teste, com três métricas agregadas.",
            "question": "Se você tivesse de escolher um modelo só com esta tabela, qual escolheria, e com que confiança? O que mais você gostaria de saber antes de decidir?",
            "explore": "As três métricas concordam entre si? Em que situação acurácia, acurácia balanceada e F1 contariam histórias diferentes?",
            "code": "from utils.handson import evaluate_models_on_dataset, summarize_classification_results\n\n# Árvore de decisão, k-vizinhos e regressão logística; 30% dos dados (90 exemplos) ficam para teste\nresultados = evaluate_models_on_dataset(df, scenario=\"ita\", random_state=56)\n\nsummarize_classification_results(resultados).set_index(\"model\")[[\"accuracy\", \"balanced_accuracy\", \"f1\"]].round(3)\n",
            "hints": ["Com 90 exemplos de teste, quantos exemplos são 2 pontos percentuais?"],
            "answer": "Uma leitura possível: as acurácias ficam entre 0,92 e 0,94, e com 90 exemplos 2 pontos percentuais são 2 exemplos, dentro do ruído amostral. As métricas concordam porque as classes estão equilibradas. O que falta é saber *quais* exemplos cada modelo erra, se os erros se sobrepõem e se algum deles é um erro \"razoável\".",
        },
        {
            "title": "Quem errou o quê?",
            "minutes": 3,
            "do": "O mesmo resultado como matriz de respostas: modelos nas linhas, exemplos de teste nas colunas, `1` para acerto e `0` para erro. Aparecem só as colunas em que algum modelo errou.",
            "question": "Que padrões você vê? Os modelos erram nos mesmos exemplos? Algum deles parece ter um \"estilo\" próprio de erro?",
            "explore": "Quantas das 90 colunas sobraram? O que as colunas que desapareceram (todos acertam) dizem sobre o teste como instrumento de medida?",
            "code": "# Modelos nas linhas, exemplos de teste nas colunas, 1 = acerto e 0 = erro\nrespostas = resultados.pivot(index=\"model\", columns=\"example_id\", values=\"correct\")\nprint(respostas.shape, \"→ (modelos, exemplos de teste)\")\n\n# Só as colunas em que pelo menos um modelo errou\nrespostas.loc[:, respostas.min(axis=0) == 0]\n",
            "hints": ["Compare a linha da árvore com as outras duas.", "Procure colunas só com 0 e colunas em que um modelo destoa dos demais."],
            "answer": "Uma leitura possível: só 11 dos 90 exemplos têm algum erro; os outros 79 não distinguem os modelos. Dois exemplos (200 e 248) são errados por todos. k-vizinhos e regressão logística erram quase nos mesmos lugares, enquanto a árvore tem um padrão próprio: erra exemplos que os outros acertam e acerta exemplos que os outros erram, coerente com uma fronteira em degraus. Esta matriz respondente × item é a entrada da IRT.",
        },
        {
            "title": "Onde moram os exemplos difíceis",
            "minutes": 4,
            "do": "Uma primeira medida de dificuldade, sem modelo latente: a fração de modelos que erra cada exemplo (o análogo do índice de dificuldade da teoria clássica dos testes), desenhada no plano das features.",
            "question": "Sua hipótese da primeira tarefa se confirmou? Algum exemplo difícil parece mais um problema do rótulo do que do modelo?",
            "explore": "Que limitação tem essa medida? Ela trata da mesma forma o erro de um modelo forte e o de um fraco?",
            "code": "dificuldade = 1 - respostas.mean(axis=0)   # fração de modelos que erraram cada exemplo\nteste = df.set_index(\"example_id\").loc[respostas.columns].assign(dificuldade=dificuldade)\n\nfig, ax = plt.subplots()\nfor label, cor in [(0, \"#B4ADA4\"), (1, \"#5E5E5E\")]:\n    grupo = teste[(teste.label == label) & (teste.dificuldade == 0)]\n    ax.scatter(grupo.feature_1, grupo.feature_2, s=16, color=cor, label=f\"classe {label}: todos acertam\")\nerros = teste[teste.dificuldade > 0]\nax.scatter(erros.feature_1, erros.feature_2, s=60 + 200 * erros.dificuldade, color=\"#F04E44\",\n           edgecolor=\"#1C2127\", linewidth=0.5, label=\"algum modelo erra (tamanho = fração de erros)\")\nax.set_title(\"Onde os modelos erram\")\nax.legend(fontsize=8)\nplt.show()\n\nerros.sort_values(\"dificuldade\", ascending=False)[[\"feature_1\", \"feature_2\", \"label\", \"dificuldade\"]].round(2)\n",
            "hints": ["Olhe onde estão os dois exemplos com dificuldade 1,0 em relação às nuvens de cada classe.", "Com só três modelos, a fração de erros só pode valer 0, 1/3, 2/3 ou 1."],
            "answer": "Uma leitura possível: a maioria dos exemplos difíceis fica na faixa de sobreposição, como esperado. Os dois errados por todos merecem atenção: se estão dentro da região da outra classe, o mais provável é rótulo trocado, não incapacidade dos modelos. A limitação da medida é que todo erro vale o mesmo, venha de um modelo forte ou fraco; com só três modelos, ela também é muito grosseira (só quatro valores possíveis). A IRT resolve as duas coisas estimando a habilidade de cada modelo junto com a dificuldade de cada exemplo.",
        },
        {
            "title": "Livre: crie o seu cenário",
            "minutes": 3,
            "optional": True,
            "do": "Os mesmos três modelos, agora num cenário que você controla: separação entre classes, ruído de rótulo e desbalanceamento.",
            "question": "Que cenário você testou, o que esperava e o que aconteceu? Alguma métrica agregada enganaria você nesse cenário?",
            "explore": "Algumas ideias: classes muito desbalanceadas (`peso_classe_0 = 0.9`) e compare acurácia com acurácia balanceada; muito ruído de rótulo (`flip_y = 0.15`); classes quase sobrepostas (`class_sep = 0.5`).",
            "code": "# Mude o que quiser. Antes de executar, anote o que você espera que aconteça.\nclass_sep = 1.4       # separação entre as classes\nflip_y = 0.02         # fração de rótulos trocados ao acaso\npeso_classe_0 = 0.5   # 0.5 = classes equilibradas; 0.9 = 90% dos exemplos na classe 0\n\ndados = make_toy_classification_dataset(n_samples=300, class_sep=class_sep, flip_y=flip_y,\n                                        weights=(peso_classe_0, 1 - peso_classe_0), random_state=56)\nres = evaluate_models_on_dataset(dados, scenario=\"livre\", random_state=56)\ntabela = res.pivot(index=\"model\", columns=\"example_id\", values=\"correct\")\n\nprint(\"exemplos que algum modelo erra:\", int((tabela.min(axis=0) == 0).sum()), \"de\", tabela.shape[1])\nprint(\"exemplos que todos erram:      \", int((tabela.max(axis=0) == 0).sum()))\nsummarize_classification_results(res).set_index(\"model\")[[\"accuracy\", \"balanced_accuracy\", \"f1\"]].round(3)\n",
            "hints": ["Mude uma coisa de cada vez para conseguir atribuir o efeito."],
            "answer": "Não há resposta única. Alguns comportamentos típicos: com desbalanceamento forte, a acurácia fica alta mesmo para um modelo que ignora a classe minoritária, e a acurácia balanceada denuncia isso; com mais ruído de rótulo, cresce o número de exemplos que todos erram, e esses exemplos não informam nada sobre os modelos; com classes sobrepostas, o número de exemplos informativos cresce e a comparação entre modelos fica mais rica, e mais ruidosa.",
        },
    ],
}

PARTE_2 = {
    "key": "parte2",
    "title": "Da matriz de respostas à IRT",
    "minutes": 20,
    "goal": "Uma população de 24 modelos faz a mesma prova de 90 exemplos, alguns com rótulo trocado de propósito. Ajustamos um modelo de IRT de dois parâmetros (2PL) e lemos o que ele diz sobre modelos e exemplos.",
    "tasks": [
        {
            "title": "Leia três itens",
            "minutes": 3,
            "do": "Três curvas características do item (CCI) do 2PL, P(θ) = 1 / (1 + exp(−a(θ − δ))). A faixa cinza marca modelos com habilidade entre 0 e 1.",
            "question": "Qual item você usaria para distinguir um modelo com θ = 0 de outro com θ = 1? E qual usaria para separar modelos muito fracos? Justifique lendo as curvas e a tabela.",
            "explore": "No simulador acima, crie um item que não serve para comparar ninguém. Que combinações de δ e a produzem isso?",
            "code": "import numpy as np\nimport pandas as pd\nfrom utils.handson import binary_irt_probability\n\ntheta = np.linspace(-3, 3, 200)   # habilidade latente\nitens = {\"A\": (-1.0, 1.0), \"B\": (0.5, 1.0), \"C\": (0.5, 4.0)}   # nome: (dificuldade δ, discriminação a)\n\nfig, ax = plt.subplots()\nax.axvspan(0, 1, color=\"#B4ADA4\", alpha=0.25, label=\"modelos entre θ = 0 e θ = 1\")\nfor nome, (d, a) in itens.items():\n    ax.plot(theta, binary_irt_probability(theta, d, a), label=f\"item {nome}: δ = {d}, a = {a}\")\nax.axhline(0.5, color=\"#B4ADA4\", linestyle=\"--\", linewidth=1)\nax.set_xlabel(\"habilidade θ\")\nax.set_ylabel(\"P(acerto)\")\nax.set_title(\"Três itens, três comportamentos\")\nax.legend(fontsize=8)\nplt.show()\n\npd.DataFrame({nome: binary_irt_probability(np.array([-1.0, 0.0, 1.0]), d, a) for nome, (d, a) in itens.items()},\n             index=[\"θ = −1\", \"θ = 0\", \"θ = 1\"]).round(2)\n",
            "hints": ["Um item separa bem dois respondentes quando as probabilidades de acerto deles são muito diferentes.", "Olhe a linha θ = 0 e a linha θ = 1 da tabela, coluna por coluna."],
            "answer": "Uma leitura possível: o item C (δ = 0,5, a = 4) vai de 0,12 em θ = 0 para 0,88 em θ = 1: é o melhor para essa comparação, porque sua dificuldade está entre os dois e a curva é íngreme. O item A, centrado em θ = −1, é mais útil para separar modelos fracos. Itens inúteis têm a próxima de zero (curva achatada) ou δ muito longe das habilidades de interesse (todos acertam ou todos erram). Em termos formais, a informação de Fisher de um item, a²·P(1 − P), é máxima em θ = δ e cresce com a².",
        },
        {
            "title": "Uma população de modelos",
            "minutes": 3,
            "do": "O mesmo tipo de problema, agora com 8% dos rótulos trocados de propósito (e registrados). Quatro famílias de classificadores, cada uma treinada com 3%, 6%, 12%, 25%, 50% ou 100% do conjunto de treino: 24 respondentes para a mesma prova.",
            "question": "Quais modelos você esperava no topo e na base? A acurácia separa bem os modelos do meio da tabela?",
            "explore": "Passe o mouse sobre `make_model_population` e `flip_labels` e veja o que dá para mudar. O que você espera que aconteça com mais rótulos trocados?",
            "code": "from utils.handson import (\n    evaluate_models_on_dataset,\n    flip_labels,\n    make_model_population,\n    make_toy_classification_dataset,\n)\n\ndados = make_toy_classification_dataset(n_samples=300, class_sep=1.4, flip_y=0.0, random_state=56)\ndados = flip_labels(dados, fraction=0.08, random_state=0)   # 8% dos rótulos trocados, de propósito\n\npopulacao = make_model_population()   # 4 famílias × 6 frações do conjunto de treino = 24 modelos\nres = evaluate_models_on_dataset(dados, scenario=\"ita\", models=populacao, random_state=56)\nR = res.pivot(index=\"model\", columns=\"example_id\", values=\"correct\")\nprint(R.shape, \"→ (modelos, exemplos de teste)\")\n\nacuracia = R.mean(axis=1).sort_values()\nfig, ax = plt.subplots(figsize=(7, 6))\nax.barh(acuracia.index, acuracia.values, color=\"#4392D2\", height=0.7)\nax.set_xlim(0.4, 1.0)\nax.set_xlabel(\"acurácia no teste\")\nax.set_title(\"24 modelos, uma prova de 90 questões\")\nax.tick_params(axis=\"y\", labelsize=8)\nplt.show()\n",
            "hints": ["Quantos modelos têm acurácia entre 0,85 e 0,90?"],
            "answer": "Uma leitura possível: os modelos treinados com 3% dos dados ficam na base, perto do acaso, como esperado. Mas, a partir de uns 12% dos dados, quase todos ficam entre 0,85 e 0,90, e a acurácia praticamente não separa os modelos do meio. Também não é verdade que mais dados sempre dão acurácia maior: o ruído de rótulo e o tamanho do teste embaralham a ordem.",
        },
        {
            "title": "Habilidade não é acurácia",
            "minutes": 4,
            "do": "Ajustamos o 2PL na matriz 24 × 90 com `fit_binary_2pl`, que estima uma habilidade θ por modelo e uma dificuldade δ e uma discriminação a por exemplo. A função `compara` mostra a dificuldade dos exemplos que só um de dois modelos acerta.",
            "question": "Habilidade e acurácia contam a mesma história? Encontre dois modelos com acurácia (quase) igual e θ diferente: o que explica a diferença?",
            "explore": "Use `compara` com outros pares. Você consegue achar um par em que o modelo de menor acurácia tem θ maior?",
            "code": "from utils.handson import fit_binary_2pl\n\nhabilidade, itens = fit_binary_2pl(R)   # θ por modelo; δ e a por exemplo de teste\n\ncomparacao = pd.DataFrame({\"acurácia\": R.mean(axis=1), \"habilidade θ\": habilidade}).sort_values(\"habilidade θ\")\nprint(\"correlação de Spearman:\", round(comparacao.corr(method=\"spearman\").iloc[0, 1], 2))\n\nfig, ax = plt.subplots()\nax.scatter(comparacao[\"acurácia\"], comparacao[\"habilidade θ\"], s=40, color=\"#4392D2\", edgecolor=\"#1C2127\", linewidth=0.5)\nax.set_xlabel(\"acurácia\")\nax.set_ylabel(\"habilidade θ\")\nax.set_title(\"Mesma prova, duas réguas\")\nplt.show()\n\n\ndef compara(a, b):\n    \"\"\"Dificuldade dos exemplos que só um dos dois modelos acerta.\"\"\"\n    so_a = R.columns[(R.loc[a] == 1) & (R.loc[b] == 0)]\n    so_b = R.columns[(R.loc[a] == 0) & (R.loc[b] == 1)]\n    print(f\"só {a} acerta:\", itens.loc[so_a, \"difficulty\"].round(2).tolist())\n    print(f\"só {b} acerta:\", itens.loc[so_b, \"difficulty\"].round(2).tolist())\n\n\ncompara(\"logística · 100% dos dados\", \"árvore · 50% dos dados\")   # <- troque os nomes\ncomparacao.round(2)\n",
            "hints": ["\"logística · 100% dos dados\" e \"árvore · 50% dos dados\" têm a mesma acurácia.", "Olhe o sinal das dificuldades que só um deles acerta."],
            "answer": "Uma leitura possível: a correlação de Spearman é 0,86, então as duas réguas concordam no geral, mas discordam no detalhe. \"logística · 100% dos dados\" e \"árvore · 50% dos dados\" acertam ambos 87% da prova, e θ vale 1,42 e 1,93. A diferença está em *quais* exemplos: a logística acerta 4 exemplos fáceis que a árvore erra (δ ≈ −2,7 a −1,5), enquanto a árvore acerta 4 exemplos difíceis que a logística erra (δ ≈ 1,3 a 2,4). A IRT pondera cada acerto pelo que ele revela sobre a habilidade; a acurácia conta todos igual.",
        },
        {
            "title": "O que torna um exemplo difícil?",
            "minutes": 4,
            "do": "A dificuldade δ estimada de cada exemplo de teste, no plano das features. Os × marcam os rótulos que trocamos de propósito, uma informação que a IRT *não* viu.",
            "question": "Onde ficam os exemplos mais difíceis? Quantos dos mais difíceis são rótulos trocados, e o que explica os demais? Que uso prático você vê nisso?",
            "explore": "Procure os × que *não* estão entre os mais difíceis. Olhe a discriminação deles na tarefa seguinte.",
            "code": "teste = dados.set_index(\"example_id\").loc[R.columns].assign(\n    dificuldade=itens[\"difficulty\"], discriminacao=itens[\"discrimination\"]\n)\n\nfig, ax = plt.subplots()\npontos = ax.scatter(teste.feature_1, teste.feature_2, c=teste.dificuldade, cmap=\"kunumi_azul\",\n                    s=40, edgecolor=\"#5E5E5E\", linewidth=0.3)\ntrocados = teste[teste.label_flipped]\nax.scatter(trocados.feature_1, trocados.feature_2, marker=\"x\", s=110, linewidth=2.2, color=\"#F04E44\",\n           label=\"rótulo trocado\")\nfig.colorbar(pontos, ax=ax, label=\"dificuldade δ\")\nax.set_title(\"Dificuldade de cada exemplo de teste\")\nax.legend(fontsize=8)\nplt.show()\n\nteste.sort_values(\"dificuldade\", ascending=False).head(8)[[\"dificuldade\", \"discriminacao\", \"label\", \"label_flipped\"]].round(2)\n",
            "hints": ["Compare a coluna `label_flipped` da tabela com a ordem da dificuldade.", "Os mais difíceis que não são rótulos trocados estão em que região?"],
            "answer": "Uma leitura possível: os quatro exemplos mais difíceis (δ = 3,68, que nenhum modelo acerta) são todos rótulos trocados; a IRT os encontrou sem saber disso. Os seguintes ficam na região de sobreposição: são difíceis por ambiguidade real, não por erro de anotação. Na prática, ordenar exemplos por dificuldade é uma forma barata de priorizar revisão de rótulos, mas ela não distingue sozinha \"rótulo errado\" de \"exemplo ambíguo\"; para isso é preciso olhar a geometria, ou a discriminação.",
        },
        {
            "title": "Que exemplos realmente medem algo?",
            "minutes": 3,
            "do": "Exemplos que todos acertam ou todos erram não separam ninguém. Para os demais, vemos dificuldade e discriminação juntas.",
            "question": "Que fração da prova realmente informa? Se você só pudesse aplicar 15 exemplos para ranquear novos modelos, quais escolheria, e o que faria com os de discriminação negativa?",
            "explore": "Os exemplos com discriminação negativa são acertados mais por modelos fracos do que por fortes. Quantos deles são rótulos trocados (tarefa anterior)?",
            "code": "print(\"todos acertam:\", int((R.min(axis=0) == 1).sum()))\nprint(\"todos erram:  \", int((R.max(axis=0) == 0).sum()))\ninformativos = R.columns[(R.min(axis=0) == 0) & (R.max(axis=0) == 1)]   # pelo menos um acerto e um erro\nprint(\"informativos: \", len(informativos), \"de\", R.shape[1])\n\nfig, ax = plt.subplots()\nax.scatter(itens.loc[informativos, \"difficulty\"], itens.loc[informativos, \"discrimination\"],\n           s=40, color=\"#4392D2\", edgecolor=\"#1C2127\", linewidth=0.5)\nax.axhline(0, color=\"#B4ADA4\", linewidth=1)\nax.set_xlabel(\"dificuldade δ\")\nax.set_ylabel(\"discriminação a\")\nax.set_title(\"Os exemplos que separam os modelos\")\nplt.show()\n\nitens.loc[informativos].sort_values(\"discrimination\").head(10).round(2)\n",
            "hints": ["Discriminação negativa: a curva desce com θ.", "Um bom item para ranquear tem a alto e δ na faixa de habilidade que interessa."],
            "answer": "Uma leitura possível: 27 exemplos são acertados por todos e 4 errados por todos; só 59 de 90 informam alguma coisa, e muitos deles têm parâmetros quase idênticos (são redundantes). Para um teste curto, escolheria exemplos com a alto e δ espalhado na faixa das habilidades que quero separar (por volta de 0 a 2), evitando duplicatas. Os de discriminação negativa saem da prova: dos quatro, dois são justamente os rótulos trocados que não estavam entre os mais difíceis. Rótulo trocado aparece, portanto, de duas formas: dificuldade extrema (ninguém acerta) ou discriminação negativa (só os fracos \"acertam\").",
        },
        {
            "title": "Livre: sua análise",
            "minutes": 5,
            "optional": True,
            "do": "Todos os objetos das tarefas anteriores continuam disponíveis (`R`, `habilidade`, `itens`, `teste`, `fit_binary_2pl`). O código abaixo é só um ponto de partida: tira da prova os exemplos suspeitos e reajusta o modelo.",
            "question": "Que pergunta você investigou, como, e o que concluiu? O ranking dos modelos mudou ao limpar a prova?",
            "explore": "Outras ideias: monte uma prova curta com os k melhores itens e compare o ranking com o da prova completa; aumente a fração de rótulos trocados e veja quantos a IRT ainda acha; troque o critério de suspeito.",
            "code": "# Um ponto de partida: o ranking dos modelos muda se tirarmos da prova os exemplos suspeitos?\nsuspeitos = itens.index[(itens.discrimination < 0) | (itens.difficulty > itens.difficulty.quantile(0.95))]\nhabilidade_sem, _ = fit_binary_2pl(R.drop(columns=suspeitos))\n\nprint(len(suspeitos), \"exemplos removidos; deles,\", int(teste.loc[suspeitos, \"label_flipped\"].sum()), \"tinham rótulo trocado\")\npd.DataFrame({\n    \"posição antes\": habilidade.rank(ascending=False).astype(int),\n    \"posição depois\": habilidade_sem.rank(ascending=False).astype(int),\n}).sort_values(\"posição depois\")\n",
            "hints": ["Para comparar dois rankings, `scipy.stats.spearmanr` ou `.corr(method=\"spearman\")`."],
            "answer": "Não há resposta única. No ponto de partida, saem 9 exemplos, 6 deles com rótulo trocado (todos os do teste), e o topo do ranking se reorganiza: modelos que dependiam de \"acertar\" exemplos com rótulo errado perdem posições. A base do ranking não muda. Mensagem geral: a avaliação de modelos depende da qualidade da prova, e a IRT dá ferramentas para auditar a prova junto com os modelos.",
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
