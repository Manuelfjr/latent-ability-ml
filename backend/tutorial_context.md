# Material do tutorial

## Parte 1 · Nem todo exemplo é igualmente difícil (~15 min)

Três classificadores com acurácias praticamente iguais. O código já está pronto: seu trabalho é observar, levantar hipóteses e interpretar onde e por que cada um erra.

### Tarefa 1 · Olhe os dados antes dos modelos
Enunciado: Um problema sintético de classificação binária em duas dimensões, com 300 pontos. Execute e observe.
Pergunta: Antes de treinar qualquer modelo: em que região você espera erros, e por quê? Anote a sua hipótese; vamos voltar a ela.
Para explorar: Algum ponto parece estar "do lado errado"? Que explicações diferentes poderiam existir para ele estar ali?
Código:
```python
from utils.handson import make_toy_classification_dataset, plot_classification_dataset

df = make_toy_classification_dataset(n_samples=300, class_sep=1.4, random_state=56)

ax = plot_classification_dataset(df)
ax.set_title("Duas classes")
plt.show()
```
Gabarito (uma leitura possível): Uma leitura possível: os erros devem se concentrar na faixa de sobreposição entre as nuvens, onde P(y ∣ x) fica perto de 1/2 e parte do erro é irredutível (erro de Bayes). Pontos isolados no meio da outra classe são outra história: o gerador troca 2% dos rótulos ao acaso, e esses pontos tendem a ser errados por todos os modelos, por melhores que sejam.

### Tarefa 2 · Três modelos, quase o mesmo número
Enunciado: Árvore de decisão, k-vizinhos e regressão logística, avaliados nos mesmos 90 exemplos de teste, com três métricas agregadas.
Pergunta: Se você tivesse de escolher um modelo só com esta tabela, qual escolheria, e com que confiança? O que mais você gostaria de saber antes de decidir?
Para explorar: As três métricas concordam entre si? Em que situação acurácia, acurácia balanceada e F1 contariam histórias diferentes?
Código:
```python
from utils.handson import evaluate_models_on_dataset, summarize_classification_results

# Árvore de decisão, k-vizinhos e regressão logística; 30% dos dados (90 exemplos) ficam para teste
resultados = evaluate_models_on_dataset(df, scenario="ita", random_state=56)

summarize_classification_results(resultados).set_index("model")[["accuracy", "balanced_accuracy", "f1"]].round(3)
```
Gabarito (uma leitura possível): Uma leitura possível: as acurácias ficam entre 0,92 e 0,94, e com 90 exemplos 2 pontos percentuais são 2 exemplos, dentro do ruído amostral. As métricas concordam porque as classes estão equilibradas. O que falta é saber *quais* exemplos cada modelo erra, se os erros se sobrepõem e se algum deles é um erro "razoável".

### Tarefa 3 · Quem errou o quê?
Enunciado: O mesmo resultado como matriz de respostas: modelos nas linhas, exemplos de teste nas colunas, `1` para acerto e `0` para erro. Aparecem só as colunas em que algum modelo errou.
Pergunta: Que padrões você vê? Os modelos erram nos mesmos exemplos? Algum deles parece ter um "estilo" próprio de erro?
Para explorar: Quantas das 90 colunas sobraram? O que as colunas que desapareceram (todos acertam) dizem sobre o teste como instrumento de medida?
Código:
```python
# Modelos nas linhas, exemplos de teste nas colunas, 1 = acerto e 0 = erro
respostas = resultados.pivot(index="model", columns="example_id", values="correct")
print(respostas.shape, "→ (modelos, exemplos de teste)")

# Só as colunas em que pelo menos um modelo errou
respostas.loc[:, respostas.min(axis=0) == 0]
```
Gabarito (uma leitura possível): Uma leitura possível: só 11 dos 90 exemplos têm algum erro; os outros 79 não distinguem os modelos. Dois exemplos (200 e 248) são errados por todos. k-vizinhos e regressão logística erram quase nos mesmos lugares, enquanto a árvore tem um padrão próprio: erra exemplos que os outros acertam e acerta exemplos que os outros erram, coerente com uma fronteira em degraus. Esta matriz respondente × item é a entrada da IRT.

### Tarefa 4 · Onde moram os exemplos difíceis
Enunciado: Uma primeira medida de dificuldade, sem modelo latente: a fração de modelos que erra cada exemplo (o análogo do índice de dificuldade da teoria clássica dos testes), desenhada no plano das features.
Pergunta: Sua hipótese da primeira tarefa se confirmou? Algum exemplo difícil parece mais um problema do rótulo do que do modelo?
Para explorar: Que limitação tem essa medida? Ela trata da mesma forma o erro de um modelo forte e o de um fraco?
Código:
```python
dificuldade = 1 - respostas.mean(axis=0)   # fração de modelos que erraram cada exemplo
teste = df.set_index("example_id").loc[respostas.columns].assign(dificuldade=dificuldade)

fig, ax = plt.subplots()
for label, cor in [(0, "#B4ADA4"), (1, "#5E5E5E")]:
    grupo = teste[(teste.label == label) & (teste.dificuldade == 0)]
    ax.scatter(grupo.feature_1, grupo.feature_2, s=16, color=cor, label=f"classe {label}: todos acertam")
erros = teste[teste.dificuldade > 0]
ax.scatter(erros.feature_1, erros.feature_2, s=60 + 200 * erros.dificuldade, color="#F04E44",
           edgecolor="#1C2127", linewidth=0.5, label="algum modelo erra (tamanho = fração de erros)")
ax.set_title("Onde os modelos erram")
ax.legend(fontsize=8)
plt.show()

erros.sort_values("dificuldade", ascending=False)[["feature_1", "feature_2", "label", "dificuldade"]].round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: a maioria dos exemplos difíceis fica na faixa de sobreposição, como esperado. Os dois errados por todos merecem atenção: se estão dentro da região da outra classe, o mais provável é rótulo trocado, não incapacidade dos modelos. A limitação da medida é que todo erro vale o mesmo, venha de um modelo forte ou fraco; com só três modelos, ela também é muito grosseira (só quatro valores possíveis). A IRT resolve as duas coisas estimando a habilidade de cada modelo junto com a dificuldade de cada exemplo.

### Livre · Livre: crie o seu cenário
Enunciado: Os mesmos três modelos, agora num cenário que você controla: separação entre classes, ruído de rótulo e desbalanceamento.
Pergunta: Que cenário você testou, o que esperava e o que aconteceu? Alguma métrica agregada enganaria você nesse cenário?
Para explorar: Algumas ideias: classes muito desbalanceadas (`peso_classe_0 = 0.9`) e compare acurácia com acurácia balanceada; muito ruído de rótulo (`flip_y = 0.15`); classes quase sobrepostas (`class_sep = 0.5`).
Código:
```python
# Mude o que quiser. Antes de executar, anote o que você espera que aconteça.
class_sep = 1.4       # separação entre as classes
flip_y = 0.02         # fração de rótulos trocados ao acaso
peso_classe_0 = 0.5   # 0.5 = classes equilibradas; 0.9 = 90% dos exemplos na classe 0

dados = make_toy_classification_dataset(n_samples=300, class_sep=class_sep, flip_y=flip_y,
                                        weights=(peso_classe_0, 1 - peso_classe_0), random_state=56)
res = evaluate_models_on_dataset(dados, scenario="livre", random_state=56)
tabela = res.pivot(index="model", columns="example_id", values="correct")

print("exemplos que algum modelo erra:", int((tabela.min(axis=0) == 0).sum()), "de", tabela.shape[1])
print("exemplos que todos erram:      ", int((tabela.max(axis=0) == 0).sum()))
summarize_classification_results(res).set_index("model")[["accuracy", "balanced_accuracy", "f1"]].round(3)
```
Gabarito (uma leitura possível): Não há resposta única. Alguns comportamentos típicos: com desbalanceamento forte, a acurácia fica alta mesmo para um modelo que ignora a classe minoritária, e a acurácia balanceada denuncia isso; com mais ruído de rótulo, cresce o número de exemplos que todos erram, e esses exemplos não informam nada sobre os modelos; com classes sobrepostas, o número de exemplos informativos cresce e a comparação entre modelos fica mais rica, e mais ruidosa.

## Parte 2 · Da matriz de respostas à IRT (~20 min)

Uma população de 24 modelos faz a mesma prova de 90 exemplos, alguns com rótulo trocado de propósito. Ajustamos um modelo de IRT de dois parâmetros (2PL) e lemos o que ele diz sobre modelos e exemplos.

### Tarefa 1 · Leia três itens
Enunciado: Três curvas características do item (CCI) do 2PL, P(θ) = 1 / (1 + exp(−a(θ − δ))). A faixa cinza marca modelos com habilidade entre 0 e 1.
Pergunta: Qual item você usaria para distinguir um modelo com θ = 0 de outro com θ = 1? E qual usaria para separar modelos muito fracos? Justifique lendo as curvas e a tabela.
Para explorar: No simulador acima, crie um item que não serve para comparar ninguém. Que combinações de δ e a produzem isso?
Código:
```python
import numpy as np
import pandas as pd
from utils.handson import binary_irt_probability

theta = np.linspace(-3, 3, 200)   # habilidade latente
itens = {"A": (-1.0, 1.0), "B": (0.5, 1.0), "C": (0.5, 4.0)}   # nome: (dificuldade δ, discriminação a)

fig, ax = plt.subplots()
ax.axvspan(0, 1, color="#B4ADA4", alpha=0.25, label="modelos entre θ = 0 e θ = 1")
for nome, (d, a) in itens.items():
    ax.plot(theta, binary_irt_probability(theta, d, a), label=f"item {nome}: δ = {d}, a = {a}")
ax.axhline(0.5, color="#B4ADA4", linestyle="--", linewidth=1)
ax.set_xlabel("habilidade θ")
ax.set_ylabel("P(acerto)")
ax.set_title("Três itens, três comportamentos")
ax.legend(fontsize=8)
plt.show()

pd.DataFrame({nome: binary_irt_probability(np.array([-1.0, 0.0, 1.0]), d, a) for nome, (d, a) in itens.items()},
             index=["θ = −1", "θ = 0", "θ = 1"]).round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: o item C (δ = 0,5, a = 4) vai de 0,12 em θ = 0 para 0,88 em θ = 1: é o melhor para essa comparação, porque sua dificuldade está entre os dois e a curva é íngreme. O item A, centrado em θ = −1, é mais útil para separar modelos fracos. Itens inúteis têm a próxima de zero (curva achatada) ou δ muito longe das habilidades de interesse (todos acertam ou todos erram). Em termos formais, a informação de Fisher de um item, a²·P(1 − P), é máxima em θ = δ e cresce com a².

### Tarefa 2 · Uma população de modelos
Enunciado: O mesmo tipo de problema, agora com 8% dos rótulos trocados de propósito (e registrados). Quatro famílias de classificadores, cada uma treinada com 3%, 6%, 12%, 25%, 50% ou 100% do conjunto de treino: 24 respondentes para a mesma prova.
Pergunta: Quais modelos você esperava no topo e na base? A acurácia separa bem os modelos do meio da tabela?
Para explorar: Passe o mouse sobre `make_model_population` e `flip_labels` e veja o que dá para mudar. O que você espera que aconteça com mais rótulos trocados?
Código:
```python
from utils.handson import (
    evaluate_models_on_dataset,
    flip_labels,
    make_model_population,
    make_toy_classification_dataset,
)

dados = make_toy_classification_dataset(n_samples=300, class_sep=1.4, flip_y=0.0, random_state=56)
dados = flip_labels(dados, fraction=0.08, random_state=0)   # 8% dos rótulos trocados, de propósito

populacao = make_model_population()   # 4 famílias × 6 frações do conjunto de treino = 24 modelos
res = evaluate_models_on_dataset(dados, scenario="ita", models=populacao, random_state=56)
R = res.pivot(index="model", columns="example_id", values="correct")
print(R.shape, "→ (modelos, exemplos de teste)")

acuracia = R.mean(axis=1).sort_values()
fig, ax = plt.subplots(figsize=(7, 6))
ax.barh(acuracia.index, acuracia.values, color="#4392D2", height=0.7)
ax.set_xlim(0.4, 1.0)
ax.set_xlabel("acurácia no teste")
ax.set_title("24 modelos, uma prova de 90 questões")
ax.tick_params(axis="y", labelsize=8)
plt.show()
```
Gabarito (uma leitura possível): Uma leitura possível: os modelos treinados com 3% dos dados ficam na base, perto do acaso, como esperado. Mas, a partir de uns 12% dos dados, quase todos ficam entre 0,85 e 0,90, e a acurácia praticamente não separa os modelos do meio. Também não é verdade que mais dados sempre dão acurácia maior: o ruído de rótulo e o tamanho do teste embaralham a ordem.

### Tarefa 3 · Habilidade não é acurácia
Enunciado: Ajustamos o 2PL na matriz 24 × 90 com `fit_binary_2pl`, que estima uma habilidade θ por modelo e uma dificuldade δ e uma discriminação a por exemplo. A função `compara` mostra a dificuldade dos exemplos que só um de dois modelos acerta.
Pergunta: Habilidade e acurácia contam a mesma história? Encontre dois modelos com acurácia (quase) igual e θ diferente: o que explica a diferença?
Para explorar: Use `compara` com outros pares. Você consegue achar um par em que o modelo de menor acurácia tem θ maior?
Código:
```python
from utils.handson import fit_binary_2pl

habilidade, itens = fit_binary_2pl(R)   # θ por modelo; δ e a por exemplo de teste

comparacao = pd.DataFrame({"acurácia": R.mean(axis=1), "habilidade θ": habilidade}).sort_values("habilidade θ")
print("correlação de Spearman:", round(comparacao.corr(method="spearman").iloc[0, 1], 2))

fig, ax = plt.subplots()
ax.scatter(comparacao["acurácia"], comparacao["habilidade θ"], s=40, color="#4392D2", edgecolor="#1C2127", linewidth=0.5)
ax.set_xlabel("acurácia")
ax.set_ylabel("habilidade θ")
ax.set_title("Mesma prova, duas réguas")
plt.show()


def compara(a, b):
    """Dificuldade dos exemplos que só um dos dois modelos acerta."""
    so_a = R.columns[(R.loc[a] == 1) & (R.loc[b] == 0)]
    so_b = R.columns[(R.loc[a] == 0) & (R.loc[b] == 1)]
    print(f"só {a} acerta:", itens.loc[so_a, "difficulty"].round(2).tolist())
    print(f"só {b} acerta:", itens.loc[so_b, "difficulty"].round(2).tolist())


compara("logística · 100% dos dados", "árvore · 50% dos dados")   # <- troque os nomes
comparacao.round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: a correlação de Spearman é 0,86, então as duas réguas concordam no geral, mas discordam no detalhe. "logística · 100% dos dados" e "árvore · 50% dos dados" acertam ambos 87% da prova, e θ vale 1,42 e 1,93. A diferença está em *quais* exemplos: a logística acerta 4 exemplos fáceis que a árvore erra (δ ≈ −2,7 a −1,5), enquanto a árvore acerta 4 exemplos difíceis que a logística erra (δ ≈ 1,3 a 2,4). A IRT pondera cada acerto pelo que ele revela sobre a habilidade; a acurácia conta todos igual.

### Tarefa 4 · O que torna um exemplo difícil?
Enunciado: A dificuldade δ estimada de cada exemplo de teste, no plano das features. Os × marcam os rótulos que trocamos de propósito, uma informação que a IRT *não* viu.
Pergunta: Onde ficam os exemplos mais difíceis? Quantos dos mais difíceis são rótulos trocados, e o que explica os demais? Que uso prático você vê nisso?
Para explorar: Procure os × que *não* estão entre os mais difíceis. Olhe a discriminação deles na tarefa seguinte.
Código:
```python
teste = dados.set_index("example_id").loc[R.columns].assign(
    dificuldade=itens["difficulty"], discriminacao=itens["discrimination"]
)

fig, ax = plt.subplots()
pontos = ax.scatter(teste.feature_1, teste.feature_2, c=teste.dificuldade, cmap="kunumi_azul",
                    s=40, edgecolor="#5E5E5E", linewidth=0.3)
trocados = teste[teste.label_flipped]
ax.scatter(trocados.feature_1, trocados.feature_2, marker="x", s=110, linewidth=2.2, color="#F04E44",
           label="rótulo trocado")
fig.colorbar(pontos, ax=ax, label="dificuldade δ")
ax.set_title("Dificuldade de cada exemplo de teste")
ax.legend(fontsize=8)
plt.show()

teste.sort_values("dificuldade", ascending=False).head(8)[["dificuldade", "discriminacao", "label", "label_flipped"]].round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: os quatro exemplos mais difíceis (δ = 3,68, que nenhum modelo acerta) são todos rótulos trocados; a IRT os encontrou sem saber disso. Os seguintes ficam na região de sobreposição: são difíceis por ambiguidade real, não por erro de anotação. Na prática, ordenar exemplos por dificuldade é uma forma barata de priorizar revisão de rótulos, mas ela não distingue sozinha "rótulo errado" de "exemplo ambíguo"; para isso é preciso olhar a geometria, ou a discriminação.

### Tarefa 5 · Que exemplos realmente medem algo?
Enunciado: Exemplos que todos acertam ou todos erram não separam ninguém. Para os demais, vemos dificuldade e discriminação juntas.
Pergunta: Que fração da prova realmente informa? Se você só pudesse aplicar 15 exemplos para ranquear novos modelos, quais escolheria, e o que faria com os de discriminação negativa?
Para explorar: Os exemplos com discriminação negativa são acertados mais por modelos fracos do que por fortes. Quantos deles são rótulos trocados (tarefa anterior)?
Código:
```python
print("todos acertam:", int((R.min(axis=0) == 1).sum()))
print("todos erram:  ", int((R.max(axis=0) == 0).sum()))
informativos = R.columns[(R.min(axis=0) == 0) & (R.max(axis=0) == 1)]   # pelo menos um acerto e um erro
print("informativos: ", len(informativos), "de", R.shape[1])

fig, ax = plt.subplots()
ax.scatter(itens.loc[informativos, "difficulty"], itens.loc[informativos, "discrimination"],
           s=40, color="#4392D2", edgecolor="#1C2127", linewidth=0.5)
ax.axhline(0, color="#B4ADA4", linewidth=1)
ax.set_xlabel("dificuldade δ")
ax.set_ylabel("discriminação a")
ax.set_title("Os exemplos que separam os modelos")
plt.show()

itens.loc[informativos].sort_values("discrimination").head(10).round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: 27 exemplos são acertados por todos e 4 errados por todos; só 59 de 90 informam alguma coisa, e muitos deles têm parâmetros quase idênticos (são redundantes). Para um teste curto, escolheria exemplos com a alto e δ espalhado na faixa das habilidades que quero separar (por volta de 0 a 2), evitando duplicatas. Os de discriminação negativa saem da prova: dos quatro, dois são justamente os rótulos trocados que não estavam entre os mais difíceis. Rótulo trocado aparece, portanto, de duas formas: dificuldade extrema (ninguém acerta) ou discriminação negativa (só os fracos "acertam").

### Livre · Livre: sua análise
Enunciado: Todos os objetos das tarefas anteriores continuam disponíveis (`R`, `habilidade`, `itens`, `teste`, `fit_binary_2pl`). O código abaixo é só um ponto de partida: tira da prova os exemplos suspeitos e reajusta o modelo.
Pergunta: Que pergunta você investigou, como, e o que concluiu? O ranking dos modelos mudou ao limpar a prova?
Para explorar: Outras ideias: monte uma prova curta com os k melhores itens e compare o ranking com o da prova completa; aumente a fração de rótulos trocados e veja quantos a IRT ainda acha; troque o critério de suspeito.
Código:
```python
# Um ponto de partida: o ranking dos modelos muda se tirarmos da prova os exemplos suspeitos?
suspeitos = itens.index[(itens.discrimination < 0) | (itens.difficulty > itens.difficulty.quantile(0.95))]
habilidade_sem, _ = fit_binary_2pl(R.drop(columns=suspeitos))

print(len(suspeitos), "exemplos removidos; deles,", int(teste.loc[suspeitos, "label_flipped"].sum()), "tinham rótulo trocado")
pd.DataFrame({
    "posição antes": habilidade.rank(ascending=False).astype(int),
    "posição depois": habilidade_sem.rank(ascending=False).astype(int),
}).sort_values("posição depois")
```
Gabarito (uma leitura possível): Não há resposta única. No ponto de partida, saem 9 exemplos, 6 deles com rótulo trocado (todos os do teste), e o topo do ranking se reorganiza: modelos que dependiam de "acertar" exemplos com rótulo errado perdem posições. A base do ranking não muda. Mensagem geral: a avaliação de modelos depende da qualidade da prova, e a IRT dá ferramentas para auditar a prova junto com os modelos.

## Demonstração do CLAIRE (fim da Parte 2, sem exercício)
300 pontos em três grupos de dispersões diferentes, 9 algoritmos de agrupamento. A concordância entre partições vira uma matriz de respostas contínuas e o β4-IRT estima a habilidade de cada algoritmo e a dificuldade de cada ponto, sem rótulos. Correlação de Spearman entre habilidade CLAIRE e ARI: 0,90; entre habilidade e silhueta: 0,35.
Referência: Ferreira-Junior et al. (2025), CLAIRE, Machine Learning 114, 256. doi:10.1007/s10994-025-06911-0

## Funções disponíveis (utils/handson.py)
- `set_project_root(level)`: Add the project root to ``sys.path`` and return that path.
- `sigmoid(x)`: Evaluate the logistic function elementwise.
- `logit(p)`: Apply a clipped logit transform to probabilities.
- `make_toy_classification_dataset(n_samples, class_sep, flip_y, weights, random_state)`: Create a 2D classification dataset for workshop demos.
- `get_default_supervised_models(random_state)`: Return the default supervised model pool used in the workshop.
- `evaluate_models_on_dataset(df, scenario, models, test_size, random_state)`: Fit several classifiers and return a long prediction table.
- `summarize_classification_results(results, scenario)`: Summarize supervised predictions at the model level.
- `summarize_instance_difficulty(results)`: Aggregate supervised predictions at the example level.
- `plot_classification_dataset(df, ax)`: Plot a 2D supervised dataset colored by class label.
- `plot_example_difficulty(summary, ax)`: Plot supervised example difficulty in feature space.
- `make_toy_clustering_dataset(scenario, n_samples, random_state)`: Create a small 2D clustering dataset for workshop experiments.
- `get_default_clustering_models(n_clusters, random_state)`: Return the default clustering model pool used in the workshop.
- `evaluate_clustering_models_on_dataset(df, scenario, models, random_state)`: Fit a clustering model pool and return long-form assignments.
- `summarize_clustering_results(assignments)`: Compute aggregate clustering metrics from long-form assignments.
- `summarize_clustering_instance_difficulty(assignments)`: Estimate instance difficulty from clustering-model agreement.
- `plot_clustering_dataset(df, ax, title)`: Plot a clustering dataset colored by teaching labels.
- `plot_clustering_instance_difficulty(summary, ax)`: Plot agreement-based clustering difficulty in feature space.
- `binary_irt_probability(theta, difficulty, discrimination)`: Compute a binary 2PL success probability.
- `make_binary_item_bank(content)`: Create a compact item bank for binary IRT and 2PL demos.
- `plot_binary_iccs(item_bank, theta, ax, title)`: Plot binary IRT or 2PL item characteristic curves.
- `beta4_expected_response(theta, difficulty, discrimination_sign, discrimination_magnitude, discrimination)`: Compute a Beta4-style expected bounded response.
- `make_beta4_item_bank(content)`: Create a compact item bank for Beta4 workshop examples.
- `plot_beta4_iccs(item_bank, theta, ax)`: Plot Beta4-style item curves on an ability grid in ``(0, 1)``.
- `plot_beta4_family(parameter_pairs, theta, ax)`: Plot an explicit family of Beta4 curves for discussion.
- `make_model_ability_grid(n_models, low, high)`: Create an ordered grid of latent abilities for synthetic models.
- `simulate_beta4_responses(n_models, item_bank, random_state)`: Simulate model-item responses under a Beta4-style latent setup.
- `summarize_latent_results(df)`: Aggregate simulated Beta4 responses at the model level.
- `make_response_matrix(df, value_column)`: Convert long-form responses into a model-by-item matrix.
- `make_toy_clustering_partitions()`: Return a tiny pool of clustering partitions for a CLAIRE demo.
- `build_claire_response_matrix(partitions)`: Compute a CLAIRE-style agreement matrix from clustering partitions.
- `estimate_case_statistics(response_matrix)`: Estimate simple item statistics from a response matrix.
- `compute_claire_like_scores(response_matrix)`: Create a simple CLAIRE-like model ranking from a response matrix.
- `plot_latent_accuracy(summary, ax)`: Plot observed and expected performance against latent ability.
- `SubsampleClassifier()`: Train a classifier on a random fraction of the training set.
- `make_model_population(fractions, random_state)`: Build a population of classifiers with a spread of abilities.
- `flip_labels(df, fraction, random_state)`: Swap the label of a random fraction of examples, keeping a record.
- `fit_binary_2pl(responses, n_iter, learning_rate)`: Fit a 2PL IRT model to a binary response matrix.
