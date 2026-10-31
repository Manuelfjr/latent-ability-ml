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

### Livre: crie o seu cenário
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

### Extra 1 · Os modelos sabem quando erram?
Enunciado: Além da classe, cada modelo dá uma probabilidade. Transformamos isso em confiança (0 = em cima do muro, 1 = certeza total) e comparamos acertos com erros.
Pergunta: Algum modelo erra com a mesma convicção com que acerta? Em que aplicação isso seria um problema? E o que as probabilidades dizem sobre os exemplos 200 e 248, que todos erram?
Para explorar: Volte ao mapa da tarefa 4 e localize os exemplos 200 e 248. A confiança dos modelos ajuda a separar rótulo trocado de exemplo ambíguo?
Código:
```python
import numpy as np

# Confiança na classe prevista: 0 = em cima do muro (P = 0,5); 1 = certeza total (P = 0 ou 1)
resultados["confianca"] = (resultados["predicted_probability"] - 0.5).abs() * 2

rng = np.random.default_rng(0)
fig, ax = plt.subplots()
for posicao, (modelo, grupo) in enumerate(resultados.groupby("model")):
    for acerto, cor, desvio, nome in [(1, "#4392D2", -0.15, "acertos"), (0, "#F04E44", 0.15, "erros")]:
        y = grupo.loc[grupo.correct == acerto, "confianca"]
        x = posicao + desvio + rng.uniform(-0.07, 0.07, len(y))
        ax.scatter(x, y, s=22 if acerto else 48, color=cor, alpha=0.6 if acerto else 0.95,
                   edgecolor="#1C2127", linewidth=0.3, label=nome if posicao == 0 else None)
ax.set_xticks(range(3), sorted(resultados.model.unique()))
ax.set_ylabel("confiança na classe prevista")
ax.set_title("Os modelos sabem quando erram?")
ax.legend(fontsize=8)
plt.show()

print("Confiança média:")
print(resultados.groupby(["model", "correct"])["confianca"].mean().unstack()
      .rename(columns={0: "quando erra", 1: "quando acerta"}).round(2).to_string())

# P(classe 1) dada por cada modelo aos dois exemplos que todos erram (o rótulo dos dois é 1)
resultados[resultados.example_id.isin([200, 248])].pivot(index="model", columns="example_id", values="predicted_probability").round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: a árvore erra com quase a mesma convicção com que acerta (confiança média de 0,90 nos erros e 0,98 nos acertos), porque cada folha pura dá probabilidade 0 ou 1. k-vizinhos (0,47) e logística (0,37) hesitam quando erram. Com acurácias praticamente iguais, os modelos se comportam de forma bem diferente: se a aplicação usa a probabilidade, por exemplo para mandar casos duvidosos a um especialista, a árvore é a pior escolha. Os dois exemplos que todos erram também se separam. No 248, os três dão P(classe 1) ≤ 0,01, certeza quase total contra o rótulo, a assinatura típica de rótulo trocado. No 200, as probabilidades ficam entre 0,24 e 0,33, mais compatível com um exemplo ambíguo perto da fronteira.

### Extra 2 · Outro sorteio, outro vencedor?
Enunciado: A tabela da tarefa 2 veio de um único sorteio de quais 90 exemplos ficam para teste. Repetimos a avaliação com 20 sorteios diferentes dos mesmos dados.
Pergunta: A diferença entre os modelos na tarefa 2 sobrevive a outros sorteios? O que isso muda na forma de reportar um resultado?
Para explorar: Aumente para 50 sorteios, ou mude `test_size` em `evaluate_models_on_dataset` (passe o mouse sobre ela). Com um teste maior, a variação diminui?
Código:
```python
import numpy as np
import pandas as pd

# Mesmos 300 pontos, 20 sorteios diferentes de quais 90 ficam para teste
acuracias = pd.DataFrame({
    semente: evaluate_models_on_dataset(df, scenario="sorteio", random_state=semente).groupby("model")["correct"].mean()
    for semente in range(20)
}).T

rng = np.random.default_rng(0)
fig, ax = plt.subplots()
for posicao, modelo in enumerate(acuracias.columns):
    ax.scatter(posicao + rng.uniform(-0.12, 0.12, 20), acuracias[modelo], s=30, color="#4392D2", alpha=0.6, edgecolor="#1C2127", linewidth=0.3)
    ax.hlines(acuracias[modelo].mean(), posicao - 0.25, posicao + 0.25, color="#F04E44", linewidth=2.6)
ax.set_xticks(range(len(acuracias.columns)), acuracias.columns)
ax.set_ylabel("acurácia no teste")
ax.set_title("20 sorteios do conjunto de teste (traço = média)")
plt.show()

print("Quantas vezes cada modelo ficou em primeiro (empates contam para todos os empatados):")
print((acuracias.eq(acuracias.max(axis=1), axis=0)).sum().to_string())
acuracias.describe().loc[["mean", "std", "min", "max"]].round(3)
```
Gabarito (uma leitura possível): Uma leitura possível: as médias ficam entre 0,913 e 0,922, enquanto cada modelo varia de 0,87 a 0,97 conforme o sorteio (desvio padrão de cerca de 0,025). A diferença entre os modelos é bem menor que a variação de um sorteio para outro: cada um fica em primeiro (ou empatado) em 7 a 13 dos 20 sorteios. Escolher o "melhor" pela tabela da tarefa 2 seria quase cara ou coroa. Um único número esconde isso; vale reportar a variação (vários sorteios, validação cruzada, intervalos) e, mais ainda, olhar *quais* exemplos cada modelo erra, que é o caminho da IRT.

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

### Livre: sua análise
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

### Extra 1 · Onde a prova mede bem?
Enunciado: Cada item contribui com informação a²·P(1 − P), concentrada perto da sua dificuldade. Somando todos, temos a informação da prova e, dela, um erro padrão aproximado de θ em cada nível de habilidade. Os traços vermelhos são os 24 modelos.
Pergunta: Em que faixa de habilidade a prova mede bem, e onde estão os modelos? A diferença entre "logística · 100%" (θ = 1,42) e "árvore · 50%" (θ = 1,93), da tarefa 3, é confiável?
Para explorar: Que tipo de exemplo você acrescentaria à prova para medir melhor os modelos do topo? Essa é a ideia por trás dos testes adaptativos.
Código:
```python
from utils.handson import binary_irt_probability

# Informação de Fisher da prova: soma, item a item, de a² · P(θ) · (1 − P(θ))
theta = np.linspace(-3, 4, 300)
a = itens["discrimination"].to_numpy()
d = itens["difficulty"].to_numpy()
P = binary_irt_probability(theta[:, None], d[None, :], a[None, :])
informacao = (a[None, :] ** 2 * P * (1 - P)).sum(axis=1)
erro_padrao = 1 / np.sqrt(informacao)   # quanto θ pode oscilar só por causa da prova

fig, ax = plt.subplots()
ax.plot(theta, erro_padrao, color="#4392D2")
ax.plot(habilidade, np.full(len(habilidade), 0.02), "|", color="#F04E44", markersize=18, markeredgewidth=2,
        label="habilidade estimada de cada modelo")
ax.set_ylim(0, 0.8)
ax.set_xlabel("habilidade θ")
ax.set_ylabel("erro padrão de θ (aproximado)")
ax.set_title("Onde a prova mede bem?")
ax.legend(fontsize=8)
plt.show()

pd.DataFrame({"θ": [-1, 0, 1, 2, 3]}).assign(
    **{"erro padrão": lambda t: 1 / np.sqrt(np.interp(t["θ"], theta, informacao))}
).round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: a prova é mais precisa entre θ ≈ −0,4 e 0 (erro padrão de cerca de 0,16) e piora para cima: 0,26 em θ = 1 e 0,40 em θ = 2. Mas dois terços dos modelos (16 de 24) estão entre θ = 1 e 2,2, justamente onde a prova mede pior. A diferença entre os dois modelos da tarefa 3 (cerca de 0,5) é só um pouco maior que um erro padrão nessa região: indica uma diferença, mas sem folga. Para separar os melhores, faltam exemplos difíceis e discriminativos (δ entre 1 e 2,5). Escolher itens cuja informação está onde o respondente está é o princípio dos testes adaptativos. O erro padrão aqui é aproximado: ignora a incerteza dos próprios parâmetros dos itens.

### Extra 2 · Uma prova de 15 questões
Enunciado: Uma prova menor ranqueia os modelos tão bem quanto a completa? Comparamos os 15 exemplos mais discriminativos com 30 provas de 15 exemplos sorteados, medindo a concordância (Spearman) com o ranking da prova de 90.
Pergunta: Quanto se perde com uma prova curta bem escolhida, e quanto com uma sorteada? Na tabela, o que os 15 escolhidos têm em comum, e o que isso implica para os modelos do topo?
Para explorar: Mude `k` (5, 10, 30). Tente outro critério, por exemplo espalhar δ entre 0 e 2,5 em vez de pegar só a maior discriminação.
Código:
```python
k = 15   # tamanho da prova curta

# Os k exemplos mais discriminativos (entre os que alguém acerta e alguém erra, com a > 0)
informativos = R.columns[(R.min(axis=0) == 0) & (R.max(axis=0) == 1)]
melhores = itens.loc[informativos].query("discrimination > 0").nlargest(k, "discrimination").index
habilidade_curta, _ = fit_binary_2pl(R[melhores])
concordancia = habilidade_curta.corr(habilidade, method="spearman")

# Comparação: 30 provas de k exemplos sorteados ao acaso
rng = np.random.default_rng(0)
sorteadas = []
for _ in range(30):
    sorteio = rng.choice(R.columns, size=k, replace=False)
    h, _ = fit_binary_2pl(R[sorteio])
    sorteadas.append(h.corr(habilidade, method="spearman"))

fig, ax = plt.subplots()
ax.hist(sorteadas, bins=12, color="#4392D2", edgecolor="#F0F0F0")
ax.axvline(concordancia, color="#F04E44", linewidth=2.6, label=f"os {k} mais discriminativos")
ax.set_xlabel("Spearman com o ranking da prova completa")
ax.set_ylabel("provas sorteadas")
ax.set_title(f"Uma prova de {k} questões ranqueia tão bem quanto a de 90?")
ax.legend(fontsize=8)
plt.show()

print(f"{k} mais discriminativos: {concordancia:.2f}")
print(f"{k} sorteados: mediana {np.median(sorteadas):.2f}, pior {min(sorteadas):.2f}, melhor {max(sorteadas):.2f}")
itens.loc[melhores].sort_values("difficulty").round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: os 15 mais discriminativos reproduzem o ranking com Spearman de 0,95; provas sorteadas de 15 exemplos têm mediana 0,81 e podem cair a 0,40. Escolher bem os itens importa mais que o tamanho da prova. Mas a tabela mostra um problema: muitos dos escolhidos são clones (mesmo padrão de acertos, mesmos δ e a), e 13 dos 15 têm δ entre −0,6 e 0,2. A prova curta mede bem o meio e quase nada do topo, onde estão os modelos que mais interessam. Um critério melhor evitaria duplicatas e espalharia δ pela faixa de interesse. É essa ideia que permite avaliar modelos novos com uma fração do custo, por exemplo em benchmarks de modelos de linguagem.

### Extra 3 · Quanto ruído a IRT aguenta?
Enunciado: Repetimos todo o processo com 0%, 4%, 8%, 15% e 25% de rótulos trocados. Em cada caso, os suspeitos são os n exemplos mais difíceis (n = número real de trocados no teste) mais os de discriminação negativa. Leva alguns segundos.
Pergunta: Até que nível de ruído a IRT ainda encontra os rótulos trocados? O que acontece com os falsos alarmes? E por que aparecem suspeitos mesmo com 0% de ruído?
Para explorar: Aqui usamos o número real de trocados, que na prática ninguém sabe. Troque por um critério que não depende disso (por exemplo, `itens_f.difficulty > 2`) e compare.
Código:
```python
# Mesma população, cada vez mais rótulos trocados. A IRT continua achando os trocados?
base = make_toy_classification_dataset(n_samples=300, class_sep=1.4, flip_y=0.0, random_state=56)
linhas = []
for fracao in [0.0, 0.04, 0.08, 0.15, 0.25]:
    d = flip_labels(base, fraction=fracao, random_state=0)
    r = evaluate_models_on_dataset(d, scenario="ruido", models=populacao, random_state=56)
    Rf = r.pivot(index="model", columns="example_id", values="correct")
    _, itens_f = fit_binary_2pl(Rf)
    trocado = d.set_index("example_id").loc[Rf.columns, "label_flipped"]
    n = int(trocado.sum())
    # suspeitos: os n mais difíceis, mais os de discriminação negativa
    suspeitos = itens_f.nlargest(n, "difficulty").index.union(itens_f.index[itens_f.discrimination < 0])
    linhas.append({
        "fração trocada": fracao,
        "acurácia média": Rf.to_numpy().mean(),
        "trocados no teste": n,
        "suspeitos": len(suspeitos),
        "trocados entre os suspeitos": int(trocado[suspeitos].sum()),
    })

ruido = pd.DataFrame(linhas).set_index("fração trocada")
ruido.round(3)
```
Gabarito (uma leitura possível): Uma leitura possível: a busca encontra praticamente todos os rótulos trocados até 25% (24 de 25), mas o preço cresce: os suspeitos passam de 4 (com 3 trocados) para 37 (com 25 trocados), ou seja, 13 falsos alarmes. Com 0% de ruído ainda aparecem 2 suspeitos, ambos de discriminação negativa: exemplos ambíguos que modelos fracos acertam por acaso. Conforme o ruído cresce, a própria prova fica menos confiável (a acurácia média cai de 0,90 para 0,61) e fica mais difícil distinguir rótulo errado de exemplo difícil. A IRT é uma boa ferramenta de triagem para revisão humana, não um detector automático, e na prática o critério precisa ser escolhido sem saber quantos rótulos estão errados.

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
