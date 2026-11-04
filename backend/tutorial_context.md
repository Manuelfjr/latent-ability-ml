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

Uma população de 24 modelos faz a mesma prova de 90 exemplos, alguns com rótulo trocado de propósito. Em vez de só acerto ou erro, usamos a probabilidade que cada modelo dá à classe correta e ajustamos o β3-IRT (pacote birt-gd), que estima a habilidade de cada modelo e a dificuldade e a discriminação de cada exemplo.

### Tarefa 1 · Leia três itens
Enunciado: No β3-IRT, a resposta de um modelo a um exemplo é contínua: a probabilidade que ele dá à classe correta. A curva característica do item dá a resposta esperada em função da habilidade θ, com θ e a dificuldade δ entre 0 e 1: E[p] = 1 / (1 + (δ / (1 − δ))^a · ((1 − θ) / θ)^a). Quando θ = δ, a resposta esperada é 0,5. A faixa cinza marca modelos com habilidade entre 0,5 e 0,8.
Pergunta: Qual item você usaria para distinguir um modelo com θ = 0,5 de outro com θ = 0,8? E qual usaria para separar modelos fracos? O que há de diferente no formato da curva do item C?
Para explorar: No simulador acima, ponha a entre 0 e 1, e depois abaixo de 0. Que formatos de curva o β3 permite que uma curva logística não permite?
Código:
```python
import numpy as np
import pandas as pd
from utils.handson import beta3_expected_response

theta = np.linspace(0.001, 0.999, 300)   # habilidade latente, entre 0 e 1
itens = {"A": (0.3, 1.0), "B": (0.6, 4.0), "C": (0.6, 0.5)}   # nome: (dificuldade δ, discriminação a)

fig, ax = plt.subplots()
ax.axvspan(0.5, 0.8, color="#B4ADA4", alpha=0.25, label="modelos entre θ = 0,5 e θ = 0,8")
for nome, (d, a) in itens.items():
    ax.plot(theta, beta3_expected_response(theta, d, a), label=f"item {nome}: δ = {d}, a = {a}")
ax.axhline(0.5, color="#B4ADA4", linestyle="--", linewidth=1)
ax.set_xlabel("habilidade θ")
ax.set_ylabel("resposta esperada (prob. da classe correta)")
ax.set_title("Três itens, três comportamentos")
ax.legend(fontsize=8)
plt.show()

pd.DataFrame({nome: beta3_expected_response(np.array([0.2, 0.5, 0.8]), d, a) for nome, (d, a) in itens.items()},
             index=["θ = 0,2", "θ = 0,5", "θ = 0,8"]).round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: o item B (δ = 0,6, a = 4) vai de 0,16 em θ = 0,5 para 0,98 em θ = 0,8: é o melhor para essa comparação, porque sua dificuldade está entre os dois e a curva é íngreme. O item A, mais fácil (δ = 0,3), separa melhor os modelos fracos: 0,37 em θ = 0,2 contra 0,70 em θ = 0,5. O item C (a = 0,5) quase não separa ninguém no meio (0,45 contra 0,62), e sua curva tem forma de S deitado: muda rápido perto de 0 e de 1 e devagar no meio. Essa flexibilidade é uma diferença do β3 para a IRT logística clássica: com 0 < a < 1 a curva deixa de ser um S, e com a < 0 ela desce.

### Tarefa 2 · Uma população de modelos
Enunciado: O mesmo tipo de problema, agora com 8% dos rótulos trocados de propósito (e registrados). Quatro famílias de classificadores, cada uma treinada com 3%, 6%, 12%, 25%, 50% ou 100% do conjunto de treino: 24 respondentes para a mesma prova. Guardamos duas matrizes: `R`, com acerto (1) ou erro (0), e `P`, com a probabilidade que cada modelo dá à classe correta, que é a resposta usada pelo β3.
Pergunta: Quais modelos você esperava no topo e na base? A acurácia separa bem os modelos do meio da tabela? Onde a probabilidade média (pontos) e a acurácia (barras) contam histórias diferentes?
Para explorar: Passe o mouse sobre `correct_class_probability`, `make_model_population` e `flip_labels`. Que família de modelo tem os pontos mais distantes das barras, e por quê?
Código:
```python
from utils.handson import (
    correct_class_probability,
    evaluate_models_on_dataset,
    flip_labels,
    make_model_population,
    make_toy_classification_dataset,
)

dados = make_toy_classification_dataset(n_samples=300, class_sep=1.4, flip_y=0.0, random_state=56)
dados = flip_labels(dados, fraction=0.08, random_state=0)   # 8% dos rótulos trocados, de propósito

populacao = make_model_population()   # 4 famílias × 6 frações do conjunto de treino = 24 modelos
res = evaluate_models_on_dataset(dados, scenario="ita", models=populacao, random_state=56)
res["p_acerto"] = correct_class_probability(res)   # probabilidade que o modelo dá à classe correta

P = res.pivot(index="model", columns="example_id", values="p_acerto")   # respostas contínuas, entre 0 e 1
R = res.pivot(index="model", columns="example_id", values="correct")    # só acerto (1) ou erro (0)
print(P.shape, "→ (modelos, exemplos de teste)")

resumo = pd.DataFrame({"acurácia": R.mean(axis=1), "P média": P.mean(axis=1)}).sort_values("acurácia")
fig, ax = plt.subplots(figsize=(7, 6))
ax.barh(resumo.index, resumo["acurácia"], color="#4392D2", height=0.7, label="acurácia")
ax.scatter(resumo["P média"], resumo.index, color="#F04E44", s=36, zorder=3, label="probabilidade média da classe correta")
ax.set_xlim(0.4, 1.0)
ax.set_title("24 modelos, uma prova de 90 questões")
ax.tick_params(axis="y", labelsize=8)
ax.legend(fontsize=8, loc="lower right")
plt.show()
```
Gabarito (uma leitura possível): Uma leitura possível: os modelos treinados com 3% dos dados ficam na base, perto do acaso. A partir de uns 12% dos dados, quase todos ficam entre 0,85 e 0,90 de acurácia, e ela praticamente não separa os modelos do meio. A probabilidade média conta outra história: nas árvores treinadas com poucos dados, ponto e barra coincidem, porque as folhas dão probabilidade 0 ou 1; as regressões logísticas acertam muito, mas com pouca convicção ("logística · 50%" tem acurácia de 0,90 e probabilidade média de só 0,75). É essa informação a mais que o β3 usa.

### Tarefa 3 · Habilidade não é acurácia
Enunciado: Ajustamos o β3-IRT na matriz `P` (24 × 90) com a classe `Beta3` do pacote [birt-gd](https://github.com/Manuelfjr/birt-gd). Ele estima uma habilidade θ por modelo e uma dificuldade δ e uma discriminação a por exemplo; θ e δ ficam entre 0 e 1. A função `compara` mostra, para dois modelos, a probabilidade média dada à classe correta nos exemplos fáceis e nos difíceis. O ajuste leva cerca de 1 minuto no servidor.
Pergunta: Habilidade e acurácia contam a mesma história? Encontre dois modelos com a mesma acurácia e θ bem diferente: o que explica a diferença?
Para explorar: Use `compara` com outros pares, por exemplo "k-vizinhos · 6% dos dados" e "árvore · 50% dos dados", que também têm a mesma acurácia. A diferença agora está nos exemplos fáceis ou nos difíceis?
Código:
```python
from birt import Beta3

# β3-IRT do pacote birt-gd. O birt espera os exemplos nas linhas e os modelos nas colunas.
beta3 = Beta3(learning_rate=1, epochs=5000, n_respondents=P.shape[0], n_items=P.shape[1],
              n_inits=1000, n_workers=1, random_seed=1, tol=1e-8)
beta3.fit(P.T.to_numpy())   # leva cerca de 1 minuto

habilidade = pd.Series(beta3.abilities, index=P.index, name="habilidade θ")   # entre 0 e 1
itens = pd.DataFrame({"difficulty": beta3.difficulties, "discrimination": beta3.discriminations}, index=P.columns)

comparacao = pd.DataFrame({"acurácia": R.mean(axis=1), "P média": P.mean(axis=1), "habilidade θ": habilidade})
comparacao = comparacao.sort_values("habilidade θ")
print("Spearman com θ: acurácia", round(comparacao.corr(method="spearman").loc["acurácia", "habilidade θ"], 2),
      "· P média", round(comparacao.corr(method="spearman").loc["P média", "habilidade θ"], 2))

fig, ax = plt.subplots()
ax.scatter(comparacao["acurácia"], comparacao["habilidade θ"], s=40, color="#4392D2", edgecolor="#1C2127", linewidth=0.5)
ax.set_xlabel("acurácia")
ax.set_ylabel("habilidade θ")
ax.set_title("Mesma prova, duas réguas")
plt.show()


def compara(a, b):
    """Acurácia, probabilidade média da classe correta nos exemplos fáceis e difíceis, e θ de dois modelos."""
    facil = itens["difficulty"] < 0.5
    print(pd.DataFrame({m: {"acurácia": R.loc[m].mean(),
                            "P média nos fáceis (δ < 0,5)": P.loc[m, facil].mean(),
                            "P média nos difíceis (δ ≥ 0,5)": P.loc[m, ~facil].mean(),
                            "θ": habilidade[m]} for m in (a, b)}).T.round(2).to_string())


compara("logística · 50% dos dados", "árvore · 12% dos dados")   # <- troque os nomes
comparacao.round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: a correlação de Spearman entre acurácia e θ é só 0,68, enquanto entre a probabilidade média e θ é 0,94: o β3 mede quanto o modelo aposta na classe correta, não só se ele passa de 50%. "logística · 50% dos dados" e "árvore · 12% dos dados" acertam ambos 90% da prova, mas θ vale 0,78 e 0,96. A árvore dá, em média, probabilidade 1,00 à classe correta nos exemplos fáceis e 0,82 nos difíceis; a logística, só 0,77 e 0,73, hesitando até no óbvio. Já no par "k-vizinhos · 6%" e "árvore · 50%" (acurácia de 0,87 nos dois, θ de 0,73 e 0,86), a diferença está em *quais* exemplos: o k-vizinhos é confiante nos fáceis (0,98) e fraco nos difíceis (0,59). Se convicção deve contar como habilidade é uma escolha de modelagem, e vale discutir.

### Tarefa 4 · O que torna um exemplo difícil?
Enunciado: A dificuldade δ estimada de cada exemplo de teste, no plano das features. Os × marcam os rótulos que trocamos de propósito, uma informação que a IRT *não* viu.
Pergunta: Onde ficam os exemplos mais difíceis? Quantos dos mais difíceis são rótulos trocados, e o que explica os demais? Que uso prático você vê nisso?
Para explorar: Seis rótulos de teste foram trocados. Quantos aparecem na tabela? Procure o que falta na tarefa seguinte.
Código:
```python
teste = dados.set_index("example_id").loc[P.columns].assign(
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
Gabarito (uma leitura possível): Uma leitura possível: os cinco exemplos mais difíceis (δ ≈ 0,98, em que quase todo modelo dá probabilidade baixa à classe "correta") são todos rótulos trocados; a IRT os encontrou sem saber disso. O sexto rótulo trocado não está entre eles: ele aparece na tarefa seguinte, com discriminação negativa. Os seguintes da lista (δ entre 0,8 e 0,9) ficam na região de sobreposição: são difíceis por ambiguidade real, não por erro de anotação. Na prática, ordenar exemplos por dificuldade é uma forma barata de priorizar a revisão de rótulos, mas ela não distingue sozinha "rótulo errado" de "exemplo ambíguo"; para isso é preciso olhar a geometria, ou a discriminação.

### Tarefa 5 · Que exemplos realmente medem algo?
Enunciado: Dificuldade e discriminação de todos os exemplos, separando os que todos os modelos acertam (probabilidade da classe correta acima de 0,5), os que todos erram e os demais. A tabela lista os exemplos de menor discriminação.
Pergunta: Na IRT clássica, um exemplo que todos acertam não informa nada. E aqui? Se você só pudesse aplicar 15 exemplos para ranquear novos modelos, quais escolheria, e o que faria com os de discriminação negativa?
Para explorar: Nos exemplos de discriminação negativa, os modelos fracos dão mais probabilidade à classe correta do que os fortes. Quantos deles são rótulos trocados?
Código:
```python
todos_acertam = P.columns[P.min(axis=0) > 0.5]   # todo modelo dá mais de 50% à classe correta
todos_erram = P.columns[P.max(axis=0) < 0.5]
print("todos acertam:", len(todos_acertam), "· todos erram:", len(todos_erram), "· demais:", P.shape[1] - len(todos_acertam) - len(todos_erram))

fig, ax = plt.subplots()
for grupo, cor, nome in [(todos_acertam, "#B4ADA4", "todos acertam"), (todos_erram, "#1C2127", "todos erram")]:
    ax.scatter(itens.loc[grupo, "difficulty"], itens.loc[grupo, "discrimination"], s=40, color=cor,
               edgecolor="#1C2127", linewidth=0.5, label=nome)
demais = P.columns.difference(todos_acertam.union(todos_erram))
ax.scatter(itens.loc[demais, "difficulty"], itens.loc[demais, "discrimination"], s=40, color="#4392D2",
           edgecolor="#1C2127", linewidth=0.5, label="alguém acerta, alguém erra")
ax.axhline(0, color="#B4ADA4", linewidth=1)
ax.set_xlabel("dificuldade δ")
ax.set_ylabel("discriminação a")
ax.set_title("Dificuldade e discriminação de cada exemplo")
ax.legend(fontsize=8)
plt.show()

itens.assign(rotulo_trocado=teste["label_flipped"]).sort_values("discrimination").head(8).round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: 27 exemplos são acertados por todos e 4 errados por todos, mas no β3 isso não os torna inúteis: os 27 fáceis (δ ≈ 0,1) ainda têm discriminação entre 0,5 e 1,1, porque os modelos fortes os acertam com mais convicção. É a vantagem de usar respostas contínuas. Os mais discriminativos (a acima de 2) têm δ entre 0,54 e 0,71; para um teste curto, escolheria entre eles, evitando duplicatas e espalhando δ. Três exemplos têm discriminação negativa: um é o sexto rótulo trocado (o 75, com a = −2,29, o menor de todos); os outros dois (295 e 34) não foram trocados por nós, mas merecem revisão. Rótulo trocado aparece, portanto, de duas formas: dificuldade extrema ou discriminação negativa.

### Livre: sua análise
Enunciado: Todos os objetos das tarefas anteriores continuam disponíveis (`P`, `R`, `habilidade`, `itens`, `teste`). Para reajustar muitas vezes, use `fit_beta3`: a mesma formulação do `Beta3` do birt, em numpy, que roda em menos de um segundo. O código abaixo é só um ponto de partida: tira da prova os exemplos suspeitos e reajusta o modelo.
Pergunta: Que pergunta você investigou, como, e o que concluiu? O ranking dos modelos mudou ao limpar a prova?
Para explorar: Outras ideias: monte uma prova curta com os k melhores itens e compare o ranking com o da prova completa; aumente a fração de rótulos trocados e veja quantos a IRT ainda acha; troque o critério de suspeito.
Código:
```python
from utils.handson import fit_beta3

# Um ponto de partida: o ranking dos modelos muda se tirarmos da prova os exemplos suspeitos?
# fit_beta3 é a mesma formulação do birt, em numpy: reajusta em menos de um segundo.
suspeitos = itens.index[(itens.discrimination < 0) | (itens.difficulty > itens.difficulty.quantile(0.95))]
habilidade_com, _ = fit_beta3(P)
habilidade_sem, _ = fit_beta3(P.drop(columns=suspeitos))

print(len(suspeitos), "exemplos removidos; deles,", int(teste.loc[suspeitos, "label_flipped"].sum()), "tinham rótulo trocado")
pd.DataFrame({
    "posição antes": habilidade_com.rank(ascending=False, method="min").astype(int),
    "posição depois": habilidade_sem.rank(ascending=False, method="min").astype(int),
}).sort_values("posição depois")
```
Gabarito (uma leitura possível): Não há resposta única. No ponto de partida, saem 8 exemplos, 6 deles com rótulo trocado (todos os do teste), e o ranking quase não muda: só há trocas entre vizinhos, como o 2º e o 3º lugares. Com respostas contínuas, alguns exemplos ruins pesam pouco diante de 90. Isso não quer dizer que os suspeitos não importam: eles distorcem a dificuldade e a discriminação estimadas e, num benchmark real, apontam exatamente onde revisar. Mensagem geral: a IRT dá ferramentas para auditar a prova junto com os modelos.

### Extra 1 · O que a confiança acrescenta?
Enunciado: A IRT clássica (2PL) só vê acerto ou erro. Ajustamos um 2PL na matriz `R` e comparamos o ranking dele com o do β3, que vê a probabilidade dada à classe correta. As linhas vermelhas são os modelos que mudam 4 posições ou mais.
Pergunta: Quem sobe e quem desce quando a confiança passa a contar? Qual dos dois rankings você usaria para escolher um modelo, e de que depende essa escolha?
Para explorar: Volte à tarefa extra 1 da Parte 1, sobre a confiança nos erros. Um modelo que erra com convicção deveria ser punido mais do que um que erra hesitando?
Código:
```python
from utils.handson import fit_binary_2pl

# A IRT clássica (2PL) só vê acerto ou erro; o β3 vê quanto o modelo apostou na classe correta.
habilidade_2pl, _ = fit_binary_2pl(R)
posicoes = pd.DataFrame({
    "acurácia": R.mean(axis=1),
    "P média": P.mean(axis=1),
    "posição 2PL (acerto/erro)": habilidade_2pl.rank(ascending=False, method="min").astype(int),
    "posição β3 (probabilidade)": habilidade.rank(ascending=False, method="min").astype(int),
})
posicoes["subiu"] = posicoes["posição 2PL (acerto/erro)"] - posicoes["posição β3 (probabilidade)"]

fig, ax = plt.subplots(figsize=(6, 6))
for modelo, linha in posicoes.iterrows():
    destaque = abs(linha["subiu"]) >= 4
    ax.plot([0, 1], [linha["posição 2PL (acerto/erro)"], linha["posição β3 (probabilidade)"]],
            color="#F04E44" if destaque else "#B4ADA4", linewidth=2.6 if destaque else 1.2, marker="o", markersize=5)
    if destaque:
        ax.text(1.04, linha["posição β3 (probabilidade)"], modelo, va="center", fontsize=8)
ax.set_xticks([0, 1], ["2PL\n(acerto/erro)", "β3\n(probabilidade)"])
ax.set_xlim(-0.2, 1.9)
ax.invert_yaxis()
ax.set_ylabel("posição no ranking (1 = melhor)")
ax.set_title("O ranking muda quando a confiança conta")
plt.show()

posicoes.sort_values("subiu").round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: as regressões logísticas são as que mais descem. "logística · 50% dos dados" cai do 3º para o 15º lugar: tem a maior acurácia da população (0,90), mas probabilidade média de só 0,75. A árvore e o k-vizinhos treinados com 25% dos dados sobem 5 e 7 posições: acertam um pouco menos, porém com mais convicção. Nenhum dos dois rankings é "o certo". Se a aplicação usa só a classe prevista, o 2PL descreve melhor o que importa; se usa a probabilidade (triagem, abstenção, decisões com custo), o β3 é mais fiel. O β3 também tem um preço: recompensa convicção, mesmo quando o modelo é mal calibrado.

### Extra 2 · Uma prova de 15 questões
Enunciado: Uma prova menor ranqueia os modelos tão bem quanto a completa? Comparamos os 15 exemplos mais discriminativos com 30 provas de 15 exemplos sorteados, medindo a concordância (Spearman) com o ranking da prova de 90. Para reajustar 32 vezes, usamos `fit_beta3`.
Pergunta: Quanto se perde com uma prova curta bem escolhida, e quanto com uma sorteada? Na tabela, o que os 15 escolhidos têm em comum?
Para explorar: Mude `k` (5, 10, 30). Tente outro critério, por exemplo espalhar δ pela faixa das habilidades em vez de pegar só a maior discriminação.
Código:
```python
k = 15   # tamanho da prova curta

# Ajuste rápido (fit_beta3, mesma formulação do birt) na prova completa, como referência
habilidade_completa, itens_completa = fit_beta3(P)

# Os k exemplos mais discriminativos (a > 0)
melhores = itens_completa.query("discrimination > 0").nlargest(k, "discrimination").index
habilidade_curta, _ = fit_beta3(P[melhores])
concordancia = habilidade_curta.corr(habilidade_completa, method="spearman")

# Comparação: 30 provas de k exemplos sorteados ao acaso
rng = np.random.default_rng(0)
sorteadas = []
for _ in range(30):
    sorteio = rng.choice(P.columns, size=k, replace=False)
    h, _ = fit_beta3(P[sorteio])
    sorteadas.append(h.corr(habilidade_completa, method="spearman"))

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
itens_completa.loc[melhores].sort_values("difficulty").round(2)
```
Gabarito (uma leitura possível): Uma leitura possível: os 15 mais discriminativos reproduzem o ranking com Spearman de 0,96, e a mediana das provas sorteadas também é alta (0,95): com respostas contínuas, cada exemplo carrega mais informação do que um simples acerto. Mas o sorteio tem cauda: a pior prova sorteada cai a 0,19, e a seleção pela discriminação elimina esse risco. Os 15 escolhidos são quase clones (a ≈ 2,1 e δ entre 0,38 e 0,56, abaixo da habilidade da maioria dos modelos): medem bem uma faixa estreita da escala. Um critério melhor evitaria duplicatas e espalharia δ pela faixa de interesse. É essa ideia que permite avaliar modelos novos com uma fração do custo, por exemplo em benchmarks de modelos de linguagem.

### Extra 3 · Quanto ruído a IRT aguenta?
Enunciado: Repetimos todo o processo com 0%, 4%, 8%, 15% e 25% de rótulos trocados, ajustando o β3 com `fit_beta3`. Em cada caso, os suspeitos são os n exemplos mais difíceis (n = número real de trocados no teste) mais os de discriminação negativa. Leva alguns segundos.
Pergunta: Até que nível de ruído a IRT ainda encontra os rótulos trocados? O que acontece com os falsos alarmes? E por que aparecem suspeitos mesmo com 0% de ruído?
Para explorar: Aqui usamos o número real de trocados, que na prática ninguém sabe. Troque por um critério que não depende disso (por exemplo, `itens_f.difficulty > 0.9`) e compare.
Código:
```python
# Mesma população, cada vez mais rótulos trocados. A IRT continua achando os trocados?
base = make_toy_classification_dataset(n_samples=300, class_sep=1.4, flip_y=0.0, random_state=56)
linhas = []
for fracao in [0.0, 0.04, 0.08, 0.15, 0.25]:
    d = flip_labels(base, fraction=fracao, random_state=0)
    r = evaluate_models_on_dataset(d, scenario="ruido", models=populacao, random_state=56)
    r["p_acerto"] = correct_class_probability(r)
    Pf = r.pivot(index="model", columns="example_id", values="p_acerto")
    _, itens_f = fit_beta3(Pf)
    trocado = d.set_index("example_id").loc[Pf.columns, "label_flipped"]
    n = int(trocado.sum())
    # suspeitos: os n mais difíceis, mais os de discriminação negativa
    suspeitos = itens_f.nlargest(n, "difficulty").index.union(itens_f.index[itens_f.discrimination < 0])
    linhas.append({
        "fração trocada": fracao,
        "P média": Pf.to_numpy().mean(),
        "trocados no teste": n,
        "suspeitos": len(suspeitos),
        "trocados entre os suspeitos": int(trocado[suspeitos].sum()),
    })

ruido = pd.DataFrame(linhas).set_index("fração trocada")
ruido.round(3)
```
Gabarito (uma leitura possível): Uma leitura possível: a busca encontra praticamente todos os rótulos trocados até 25% (24 de 25), mas o preço cresce: de 4 suspeitos (com 3 trocados) para 38 (com 25 trocados), ou seja, 14 falsos alarmes. Com 0% de ruído ainda aparecem 3 suspeitos, todos de discriminação negativa: exemplos ambíguos em que os modelos fracos dão mais probabilidade à classe correta que os fortes. Conforme o ruído cresce, a própria prova fica menos confiável (a probabilidade média da classe correta cai de 0,88 para 0,56), e fica mais difícil distinguir rótulo errado de exemplo difícil. A IRT é uma boa ferramenta de triagem para revisão humana, não um detector automático.

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
- `beta3_expected_response(theta, difficulty, discrimination)`: Compute the Beta3-IRT expected response E[p | theta, difficulty, discrimination].
- `correct_class_probability(results)`: Probability each model gives to the true class of each test example.
- `fit_beta3(responses, n_iter, learning_rate)`: Fit a Beta3-IRT model to a matrix of responses in ``[0, 1]``.
