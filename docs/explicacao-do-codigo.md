# Explicação do código

Este documento explica **todo** o código do jogo, arquivo por arquivo e função por função.
A ideia é que qualquer pessoa que já viu o básico de Python (variáveis, `if`, `for`, `while`,
listas, dicionários e funções) consiga entender como o jogo funciona.

## Sumário

1. [A ideia geral](#1-a-ideia-geral)
2. [Por que 3 arquivos?](#2-por-que-3-arquivos)
3. [dados.py: os dados do jogo](#3-dadospy-os-dados-do-jogo)
4. [tela.py: o desenho](#4-telapy-o-desenho)
5. [jogo.py: a lógica](#5-jogopy-a-lógica)
   - [Teclado](#51-teclado)
   - [Criação do mapa](#52-criação-do-mapa)
   - [Criação do jogador e da sala](#53-criação-do-jogador-e-da-sala)
   - [Funções de ajuda](#54-funções-de-ajuda)
   - [Batalha: dano](#55-batalha-dano)
   - [Jogador: andar, atirar, poder, itens](#56-jogador-andar-atirar-poder-itens)
   - [Tiros (lágrimas)](#57-tiros-lágrimas)
   - [Inteligência dos inimigos](#58-inteligência-dos-inimigos)
   - [Sala limpa e baú](#59-sala-limpa-e-baú)
   - [O game loop](#510-o-game-loop)
   - [Programa principal](#511-programa-principal)
6. [Respondendo as perguntas do tutorial](#6-respondendo-as-perguntas-do-tutorial)

---

## 1. A ideia geral

O tutorial da aula resume um jogo em quatro partes:

```
ESTADO  ->  ENTRADA  ->  ATUALIZAÇÃO  ->  DESENHO  ->  (repete)
```

Este jogo segue exatamente essa ideia, só que com mais coisas no estado:

| Parte | No tutorial | Neste jogo |
|---|---|---|
| **Estado** | `x`, `y` do `@` | dicionários `jogador` e `sala` (vida, posição, inimigos, tiros, baús...) |
| **Entrada** | `WConio2.kbhit()` e `getch()` | função `ler_teclas()` |
| **Atualização** | `x += 1` | `mover_jogador()`, `atualizar_inimigos()`, `atualizar_tiros()`... |
| **Desenho** | `print()` do cenário | `tela.desenhar_jogo()` |

Tudo isso roda dentro de um `while True` na função `jogar_sala()`, umas 20 vezes por segundo.
Cada volta do `while` é chamada de **quadro** (*frame*).

---

## 2. Por que 3 arquivos?

Se tudo ficasse num arquivo só, seriam mais de 1300 linhas misturadas. Separando:

- **`dados.py`**: só valores (quanto de vida tem o zumbi, quais salas existem...).
  Para deixar o jogo mais fácil ou mais difícil, só mexe aqui.
- **`tela.py`**: só desenho. Não decide nada, só mostra o estado na tela.
- **`jogo.py`**: só regras. Decide o que acontece.

Para usar um arquivo dentro do outro, usamos `import`:

```python
import tela                       # usa como tela.desenhar_jogo(...)
from dados import LARGURA, SALAS  # usa direto: LARGURA, SALAS
```

---

## 3. dados.py: os dados do jogo

### Tamanho do mapa

```python
LARGURA = 41
ALTURA = 15
```

O mapa de cada sala tem 41 colunas e 15 linhas, contando as paredes. Variáveis em
MAIÚSCULO são uma convenção do Python para dizer "isso é uma constante, não muda".

### Cores

```python
VERMELHO = "91"
VERDE = "92"
...
```

São **códigos de cor ANSI**. O terminal entende que, se você escrever `"\033[91m"`, o texto
seguinte fica vermelho, e `"\033[0m"` volta ao normal. A função `cor()` do `tela.py` usa esses códigos.

### Personagens

```python
PERSONAGENS = [
    {
        "nome": "Cavaleiro",
        "simbolo": "♂",
        "vida": 6,
        "dano": 2,
        "alcance": 5,
        "recarga": 8,
        "poder": "giro",
        ...
    },
    ...
]
```

É uma **lista de dicionários**. Cada dicionário é um personagem. Os campos importantes:

- `vida`: quantos corações começa
- `dano`: dano de cada lágrima
- `alcance`: quantas casas a lágrima anda antes de sumir
- `recarga`: quantos quadros espera entre um tiro e outro (**menor = atira mais rápido**)
- `poder` / `custo_poder`: qual poder usa e quanta energia gasta

### Inimigos

```python
INIMIGOS = {
    "mosca":  {"simbolo": "¤", "vida": 1, "dano": 1, "espera": 5, "ia": "aleatorio"},
    "zumbi":  {"simbolo": "Z", "vida": 4, "dano": 1, "espera": 8, "ia": "perseguir"},
    ...
}
```

Aqui é um **dicionário de dicionários**: a chave é o tipo (`"mosca"`) e o valor são os dados.
Assim dá para fazer `INIMIGOS["zumbi"]["vida"]`.

- `espera`: quantos quadros o inimigo espera entre um passo e outro (menor = mais rápido)
- `ia`: o "jeito de pensar" do inimigo (veja a [seção 5.8](#58-inteligência-dos-inimigos))
- `espera_tiro`: só existe nos inimigos que atiram (olho e chefe)

### Salas

```python
SALAS = [
    {
        "nome": "Porão Úmido",
        "parede": ("█", CINZA),
        "chao": (" ", CINZA),
        "obstaculo": ("○", BRANCO),
        "perigo": None,
        "layout": "livre",
        "obstaculos": 6,
        "inimigos": ["mosca", "mosca", "mosca"],
    },
    ...
]
```

São 10 salas. O que deixa cada uma **diferente**:

- `parede`, `chao`, `obstaculo`, `perigo`: **tuplas** `(caractere, cor)`, ou seja, o visual
- `perigo`: chão que machuca (água tóxica, lava). `None` = a sala não tem
- `layout`: o formato fixo da sala (pilares, cantos, rio, lagoas, corredor ou livre)
- `obstaculos`: quantos obstáculos **aleatórios** aparecem além do layout
- `inimigos`: lista com os tipos de inimigos daquela sala

### Conteúdo dos baús

```python
CONTEUDO_BAUS = [
    {"nome": "Poção Vermelha", "efeito": "cura", "texto": "+2 de vida"},
    ...
]
```

Quando o jogador abre um baú, o jogo sorteia um desses com `random.choice()`.

---

## 4. tela.py: o desenho

### `cor(texto, codigo)`

```python
def cor(texto, codigo):
    return "\033[" + codigo + "m" + texto + "\033[0m"
```

Coloca o código de cor antes do texto e o código de "voltar ao normal" depois.
`cor("♥", "91")` vira um coração vermelho.

### `preparar_terminal()` e `restaurar_terminal()`

```python
os.system("")                # liga as cores ANSI no terminal do Windows
print("\033[?25l", end="")   # esconde o cursor piscando
```

No final, `restaurar_terminal()` mostra o cursor de novo.

### `limpar()` e `ir_para_o_topo()`

`limpar()` é o mesmo `os.system("cls")` do tutorial. O problema: se apagar a tela 20 vezes
por segundo, ela **pisca** muito. Por isso, durante o jogo, usamos `ir_para_o_topo()`:

```python
print("\033[H", end="")
```

Esse código só **volta o cursor para o canto de cima** e o próximo quadro é desenhado
**por cima** do anterior. Não pisca, porque a tela nunca fica vazia. O `cls` só é usado
quando troca de tela (menu, transição de sala).

### `desenhar_celula(sala, x, y)`

O mapa guarda **códigos** (`"#"`, `"."`, `"O"`, `"~"`, `"P"`), não o desenho final.
Essa função traduz o código para o caractere colorido **daquela sala**:

```python
if celula == "#":
    simbolo, c = dados["parede"]   # na Floresta vira ♣ verde, no Porão vira █ cinza
    return cor(simbolo, c)
```

Por isso o mesmo código de mapa fica com cara diferente em cada sala.
O perigo (`"~"`) às vezes vira `°` para parecer que está borbulhando.

### `desenhar_mapa(jogador, sala)`

Monta o mapa linha por linha, igual o tutorial faz com os `print`, mas decidindo
**o que aparece em cada casa** numa ordem de prioridade:

```
efeito > jogador > inimigo > tiro > item (baú/coração) > mapa
```

Para não ter que procurar em todas as listas a cada casa, antes do `for` a função monta
**dicionários de posição**:

```python
pos_inimigos = {}
for inimigo in sala["inimigos"]:
    pos_inimigos[(inimigo["x"], inimigo["y"])] = inimigo
```

Depois, para saber se tem inimigo na casa `(x, y)`, basta `if (x, y) in pos_inimigos`.

Detalhes visuais:
- o jogador **pisca** quando está invencível (só aparece em metade dos quadros: `quadro % 4 < 2`)
- no poder Sombra, o jogador fica **cinza**
- o inimigo fica com **fundo vermelho** por 3 quadros quando leva dano (`piscando`)

### `barra_de_vida`, `barra_de_energia`, `barra_do_chefe`

Desenham o HUD (*heads-up display*, as informações em volta do jogo):

```python
for i in range(jogador["vida_max"]):
    if i < jogador["vida"]:
        texto += cor("♥", "91")   # coração cheio (vermelho)
    else:
        texto += cor("♥", "90")   # coração vazio (cinza)
```

A barra do chefe calcula quantos blocos pintar com uma regra de três:
`cheio = int(30 * vida / vida_max)`.

### `desenhar_jogo(jogador, sala)`

Junta tudo: título da sala, vida, energia, poder, mapa, mensagem e controles.
No final:

```python
ir_para_o_topo()
print("\n".join(linha + "\033[K" for linha in linhas) + "\033[J", end="", flush=True)
```

- `"\n".join(linhas)` junta todas as linhas num texto só (um `print` só é bem mais rápido que vários)
- `\033[K` apaga o resto da linha, para não sobrar letra do quadro anterior
- `flush=True` manda o texto para a tela na hora

### Telas de menu

`tela_titulo()`, `tela_escolha_personagem()`, `tela_transicao()`, `tela_pausa()` e `tela_fim()`
são só um monte de `print` com cores. A `tela_transicao()` mostra o nome da próxima sala
e espera 1,8 segundo com `time.sleep(1.8)`.

---

## 5. jogo.py: a lógica

### 5.1 Teclado

#### `ler_teclas()`

```python
def ler_teclas():
    teclas = []
    while WConio2.kbhit():
        codigo, letra = WConio2.getch()
        ...
        teclas.append(letra.lower())
    return teclas
```

- `WConio2.kbhit()` diz se tem tecla esperando, **sem travar** o jogo (diferente do `input()`)
- `WConio2.getch()` devolve uma **tupla** `(codigo, letra)`, e não só a letra.
  Por isso fazemos `codigo, letra = WConio2.getch()` (isso se chama *desempacotar*)
- o `while` lê **todas** as teclas apertadas desde o último quadro

**As setas** chegam em duas partes: primeiro o código `224` (ou `0`), depois o código da seta:

| Código | Seta |
|---|---|
| 72 | cima |
| 80 | baixo |
| 75 | esquerda |
| 77 | direita |

#### `esvaziar_teclado()` e `esperar_tecla()`

`esperar_tecla()` é usada nos menus: lá **pode** travar esperando o jogador.
Antes, ela chama `esvaziar_teclado()` para jogar fora teclas antigas
(senão uma tecla apertada durante o jogo poderia escolher algo no menu sem querer).
O `Enter` tem código `13`.

### 5.2 Criação do mapa

O mapa é uma **lista de listas** (uma matriz, como a seção 10 do tutorial):
`mapa[y][x]`, ou seja, primeiro a linha, depois a coluna.

| Código | Significa |
|---|---|
| `"#"` | parede |
| `"."` | chão |
| `"O"` | obstáculo (bloqueia) |
| `"~"` | perigo (dá para pisar, mas machuca) |
| `"P"` | porta |

#### `mapa_vazio()`

Cria a sala só com paredes nas bordas e chão no meio. A porta fica no meio da parede da direita:
`mapa[MEIO][PORTA_X] = "P"`.

#### `area_protegida(x, y)`

Devolve `True` para as casas que **nunca** podem ter obstáculo:
- perto de onde o jogador nasce (lado esquerdo, no meio)
- na frente da porta (lado direito, no meio)

É assim que garantimos que **obstáculos não nascem onde o jogador está**.

#### `colocar(mapa, x, y, codigo)`

Coloca algo no mapa **só se** a casa for chão e não for protegida. Todo layout usa ela,
assim nenhum layout consegue tampar o jogador ou a porta sem querer.

#### `aplicar_layout(mapa, layout, tem_perigo)`

Cada layout desenha um formato fixo:

- **pilares**: pares de obstáculos espalhados em duas fileiras
- **cantos**: blocos 4x2 nos quatro cantos
- **rio**: uma faixa de perigo no meio da sala, com uma "ponte" livre no meio
- **lagoas**: 4 poças em lugares sorteados (de perigo se a sala tiver perigo, senão de obstáculo)
- **corredor**: duas fileiras de estantes com buracos a cada 8 casas
- **livre**: não faz nada (só os obstáculos aleatórios)

#### `colocar_obstaculos_aleatorios(mapa, quantidade)`

```python
while colocados < quantidade and tentativas < 500:
    x = random.randint(1, LARGURA - 2)
    y = random.randint(1, ALTURA - 2)
    if mapa[y][x] == "." and not area_protegida(x, y):
        mapa[y][x] = "O"
        colocados += 1
```

Sorteia posições até colocar a quantidade pedida. O limite de 500 tentativas evita
um loop infinito se a sala ficar cheia.

#### `casas_alcancaveis(mapa, inicio_x, inicio_y)` (busca em largura, BFS)

Essa é a função mais "esperta" do jogo. Ela descobre **todas as casas que dá para alcançar**
andando a partir de um ponto. Funciona assim:

1. coloca a casa inicial numa **fila**
2. tira a primeira casa da fila
3. olha os 4 vizinhos (cima, baixo, esquerda, direita)
4. todo vizinho que for andável e ainda não foi visitado entra na fila
5. repete até a fila acabar

```python
while len(fila) > 0:
    x, y = fila.pop(0)
    for dx, dy in DIRECOES:
        nx = x + dx
        ny = y + dy
        if (nx, ny) not in visitados and mapa[ny][nx] in (".", "~"):
            visitados.add((nx, ny))
            fila.append((nx, ny))
```

É como jogar tinta no chão e ver até onde ela escorre. `visitados` é um `set` (conjunto),
que é bem rápido para perguntar "isso já está aqui?".

#### `criar_mapa(dados_sala)`

```python
for tentativa in range(100):
    mapa = mapa_vazio()
    aplicar_layout(...)
    colocar_obstaculos_aleatorios(...)
    alcancaveis = casas_alcancaveis(mapa, INICIO_X, MEIO)
    if (PORTA_X - 1, MEIO) in alcancaveis:
        return mapa
```

Gera uma sala e **confere com a BFS se dá para chegar na porta**. Se os obstáculos
aleatórios fecharam o caminho, joga fora e gera de novo. Assim o jogador nunca fica preso.

### 5.3 Criação do jogador e da sala

#### `criar_jogador(personagem)`

Copia os dados do personagem escolhido para um dicionário novo, e adiciona os campos que
**mudam durante o jogo**:

| Campo | Para que serve |
|---|---|
| `x`, `y` | posição |
| `energia` | energia dos poderes |
| `espera_tiro` | contador até poder atirar de novo |
| `espera_passo` / `passo_pendente` | controla a velocidade de andar |
| `tiro_direcao` / `tiro_tempo` | tiro contínuo (veja o game loop) |
| `invencivel` | quadros sem levar dano depois de ser atingido |
| `sombra` | quadros restantes do poder do Ladino |
| `abates`, `baus` | estatísticas para a tela final |

Por que copiar? Porque se mexêssemos direto em `PERSONAGENS[0]`, os baús alterariam
os dados originais, e na próxima partida o personagem já começaria mais forte.

#### `criar_inimigo(tipo, x, y)`

Cria o dicionário de um inimigo. O `contador` começa com um número sorteado para os
inimigos **não andarem todos ao mesmo tempo** (fica mais natural).

#### `casas_livres(sala, jogador, distancia_minima)`

Usa a BFS a partir do jogador e filtra só as casas que:
- são chão (`"."`)
- **não são onde o jogador está**
- estão a pelo menos `distancia_minima` casas do jogador
- não têm inimigo nem item

É usada para escolher onde nascem os **inimigos** (longe do jogador) e os **baús**
(onde o jogador não está). Como vem da BFS, sempre é um lugar que dá para alcançar.

A distância usada é a **distância de Manhattan**: `abs(x1 - x2) + abs(y1 - y2)`,
ou seja, quantos passos andando só na horizontal e na vertical.

#### `criar_sala(numero, jogador)`

Monta o dicionário `sala` com tudo que acontece nela (mapa, inimigos, tiros, itens, efeitos,
mensagem, quadro). Coloca o jogador na entrada, dá um tempinho de invencibilidade e
espalha os inimigos. O chefe nasce sempre no mesmo lugar, e a função limpa as casas em volta
dele para garantir que ele consiga se mexer.

### 5.4 Funções de ajuda

- `mostrar_mensagem(sala, texto, segundos)`: mostra uma mensagem embaixo do mapa por alguns segundos
- `inimigo_em(sala, x, y)`: devolve o inimigo naquela casa, ou `None`
- `item_em(sala, x, y)`: mesma coisa para itens
- `sinal(numero)`: devolve `1`, `-1` ou `0`. Serve para saber a direção: se o jogador está
  à direita, `sinal(jogador_x - inimigo_x)` dá `1`
- `adicionar_efeito(...)`: adiciona um efeito visual (`*`, `!`, `+`) que some depois de alguns quadros

### 5.5 Batalha: dano

#### `jogador_leva_dano(jogador, sala, quantidade, motivo)`

```python
if jogador["invencivel"] > 0:
    return
jogador["vida"] -= quantidade
jogador["invencivel"] = 25
```

Depois de levar dano, o jogador fica **25 quadros (~1 segundo) invencível**.
Sem isso, um inimigo encostado tiraria toda a vida em menos de um segundo.

#### `ferir_inimigo(...)` e `matar_inimigo(...)`

Tira vida do inimigo e faz ele piscar. Se a vida chegar a zero:
- remove o inimigo da lista
- o jogador ganha **+1 de energia**
- tem **15% de chance** de cair um coração (`random.random() < 0.15`)
- se for o chefe, todos os ajudantes morrem junto

### 5.6 Jogador: andar, atirar, poder, itens

#### `mover_jogador(jogador, sala, dx, dy)`

Calcula a casa nova (`nx = x + dx`) e verifica, em ordem:

1. é a **porta**? Se estiver aberta, devolve `"porta"` (vai para a próxima sala).
   Se estiver fechada, mostra "A porta está trancada!"
2. é **parede ou obstáculo**? Não anda (é o "impedir de atravessar a parede" do tutorial)
3. tem **inimigo**? Leva dano e não anda
4. senão, anda e verifica se pisou num **item**

#### `pegar_item(...)` e `abrir_bau(...)`

O coração recupera 1 de vida. O baú sorteia um prêmio de `CONTEUDO_BAUS` e aplica o efeito
com uma sequência de `if/elif`. Os `min()` e `max()` servem para não passar dos limites:

```python
jogador["vida"] = min(jogador["vida_max"], jogador["vida"] + 2)   # não passa da vida máxima
jogador["recarga"] = max(2, jogador["recarga"] - 1)               # não fica rápido demais
```

#### `atirar(jogador, sala, dx, dy)`

Se a recarga já zerou, cria um tiro (um dicionário com posição, direção, alcance e dano) e
coloca na lista `sala["tiros"]`. No poder Sombra o dano é dobrado.

#### `usar_poder(jogador, sala)`

Confere se tem energia, desconta e faz o efeito do personagem:

- **giro**: todo inimigo com `abs(dx) <= 3 and abs(dy) <= 3` leva 4 de dano (um quadrado 7x7 em volta)
- **tempestade**: todo inimigo da sala leva 3 de dano, e caem "raios" (`!`) em lugares sorteados
- **sombra**: liga `sombra` e `invencivel` por 4 segundos (`4 * QUADROS_POR_SEGUNDO`)

Repare no `for inimigo in list(sala["inimigos"])`: usamos `list(...)` para fazer uma **cópia**,
porque inimigos podem ser removidos da lista dentro do `for`, e remover itens da lista que
você está percorrendo dá problema.

#### `atualizar_jogador(jogador, sala)`

Diminui todos os contadores em 1 a cada quadro (recarga, passo, invencibilidade, sombra...)
e, se o jogador estiver em cima de chão perigoso (`"~"`), aplica dano.

### 5.7 Tiros (lágrimas)

#### `atualizar_tiros(jogador, sala)`

Cada tiro anda **1 casa por quadro** na sua direção:

```python
tiro["x"] += tiro["dx"]
tiro["y"] += tiro["dy"]
tiro["alcance"] -= 1
```

- se bateu em parede, obstáculo ou porta, some (e deixa um `°` de efeito)
- se o alcance acabou, some
- os tiros dos inimigos só andam nos quadros pares (`quadro % 2`), ou seja,
  na **metade da velocidade**, para dar tempo de desviar

A função monta uma lista nova `restantes` só com os tiros que continuam existindo,
em vez de apagar da lista original (mesmo motivo do `list(...)` acima).

#### `checar_acertos(jogador, sala)`

Para cada tiro: se é do jogador e tem inimigo na mesma casa, fere o inimigo.
Se é do inimigo e está na casa do jogador, o jogador leva dano. Essa é a **detecção de colisão**
do tutorial ("descobrir se `@` chegou à mesma posição de `*`"): duas coisas colidem quando
têm o mesmo `x` **e** o mesmo `y`.

### 5.8 Inteligência dos inimigos

#### `inimigo_pode_ir(...)`

O inimigo não pode entrar em parede, porta, outro inimigo ou item.
Obstáculo só se ele atravessar (fantasma).

#### `passos_ate_jogador(inimigo, jogador)`

Devolve os passos que aproximam o inimigo do jogador, do melhor para o pior:

```python
dx = jogador["x"] - inimigo["x"]
dy = jogador["y"] - inimigo["y"]
if abs(dx) >= abs(dy):
    passos = [passo_x, passo_y]   # está mais longe na horizontal: anda na horizontal primeiro
else:
    passos = [passo_y, passo_x]
```

Se o melhor passo estiver bloqueado, o inimigo tenta o segundo. É uma perseguição simples,
mas funciona bem.

#### `atualizar_inimigos(jogador, sala)`

Para cada inimigo, a cada quadro:

1. **Tiro** (só olho e chefe): soma 1 no `contador_tiro`. Quando chega no `espera_tiro`:
   - o **olho** atira se estiver na mesma linha ou coluna do jogador (ou com 30% de chance)
   - o **chefe** atira em 4 direções, alternando entre `+` e `x`, e às vezes chama uma mosca
2. **Movimento**: soma 1 no `contador`. Só anda quando chega na `espera` do tipo
   (é assim que cada inimigo tem uma velocidade diferente). Aí escolhe os passos pela `ia`:

| IA | Comportamento |
|---|---|
| `perseguir` | sempre vem na direção do jogador (zumbi, golem) |
| `aleatorio` | 50% persegue, 50% anda para um lado sorteado (mosca, aranha) |
| `fantasma` | persegue e atravessa obstáculos |
| `atirador` | quase não anda (30% de chance), prefere atirar (olho) |
| `chefe` | persegue, e com menos da metade da vida fica bem mais rápido (`espera = 3`) |

Se o passo cair exatamente na casa do jogador, o inimigo **ataca** em vez de andar.

### 5.9 Sala limpa e baú

#### `checar_sala_limpa(jogador, sala)`

Quando a lista de inimigos fica vazia (e a porta ainda está fechada):
- abre a porta (`porta_aberta = True`)
- apaga os tiros que sobraram
- sorteia uma casa com `casas_livres(sala, jogador, 4)`, que **nunca é onde o jogador está**
  e fica a pelo menos 4 casas dele, e coloca o **baú** lá

#### `atualizar_efeitos(sala)`

Diminui o tempo de cada efeito visual e remove os que acabaram. Também conta o tempo da mensagem.

### 5.10 O game loop

A função `jogar_sala(jogador, sala)` é o coração do jogo. É o `while True` do tutorial,
dividido nas 4 etapas:

```python
while True:
    inicio = time.time()

    # 1. ENTRADA: lê as teclas e decide o que o jogador quer fazer
    for tecla in ler_teclas():
        ...

    # 2. ATUALIZAÇÃO: muda o estado do jogo
    mover_jogador(...)
    atirar(...)
    atualizar_jogador(...)
    atualizar_tiros(...)
    atualizar_inimigos(...)
    checar_acertos(...)
    checar_sala_limpa(...)

    # 3. DESENHO: mostra o estado na tela
    tela.desenhar_jogo(jogador, sala)

    # 4. ESPERA: mantém a velocidade constante
    tempo_gasto = time.time() - inicio
    espera = 1 / QUADROS_POR_SEGUNDO - tempo_gasto
    if espera > 0:
        time.sleep(espera)
```

Três detalhes importantes:

**a) Velocidade constante.** Cada quadro deve durar 1/20 de segundo (0,05 s). Medimos quanto
tempo o quadro gastou e dormimos só o que falta. Assim o jogo roda na mesma velocidade
num PC rápido ou lento.

**b) Passo a cada 2 quadros.** Se o jogador andasse 1 casa por quadro, seriam 20 casas por segundo,
rápido demais para controlar. Então a tecla fica guardada em `passo_pendente` e só é usada quando
`espera_passo` zera.

**c) Tiro contínuo.** No terminal do Windows, se você segura duas teclas, **só a última repete**.
Então seria impossível andar e atirar ao mesmo tempo, como no Isaac. A solução:
quando você aperta uma seta, o personagem continua atirando sozinho por 15 quadros
(`tiro_tempo = 15`). Assim dá para apertar a seta e logo depois andar.

A função termina devolvendo `"proxima"` (passou pela porta), `"morreu"` ou `"sair"`.

### 5.11 Programa principal

- `escolher_personagem()`: mostra a tela de escolha e espera `1`, `2` ou `3`
- `jogar_partida()`: cria o jogador e passa pelas 10 salas com um `for`. Para cada uma: tela de
  transição, cria a sala, joga. Se morrer, mostra a tela de fim de jogo. Se passar da última, venceu
- `main()`: tela de título e "jogar de novo?". O `try/finally` garante que o terminal volta
  ao normal (cursor visível, cor normal) **mesmo se der erro** no meio do jogo

```python
if __name__ == "__main__":
    main()
```

Essa linha diz: "só rode o `main()` se este arquivo for executado diretamente"
(e não se for importado por outro arquivo).

---

## 6. Respondendo as perguntas do tutorial

**Qual é a diferença entre uma animação e um jogo?**
Na animação, o estado muda sozinho e sempre do mesmo jeito (o `i += 0.2` do exemplo).
No jogo, o estado muda de acordo com a **entrada do jogador**: o que aparece na tela depende das
decisões dele. Aqui, o jogador decide para onde anda, para onde atira e quando usa o poder.

**Por que precisamos redesenhar a tela várias vezes para criar a sensação de movimento?**
Porque o terminal não "move" caracteres: ele só mostra texto. Para parecer que algo andou,
desenhamos de novo com o caractere em outra posição. Fazendo isso 20 vezes por segundo,
o olho enxerga movimento. Neste jogo usamos `\033[H` para redesenhar por cima, sem piscar.

**Quais informações precisam ser armazenadas para representar o estado de um personagem?**
Posição (`x`, `y`), vida e vida máxima, atributos de combate (dano, alcance, recarga),
energia e contadores de tempo (invencibilidade, recarga do tiro, duração do poder).
Tudo isso está no dicionário `jogador`.

**Como transformar uma tecla pressionada em uma ação dentro do jogo?**
`kbhit()` avisa que tem tecla, `getch()` diz qual é, e uma sequência de `if/elif` traduz
a tecla para uma ação (`"w"` → `movimento = (0, -1)`). Depois, a função da ação
(`mover_jogador`) altera o estado.

**Que estruturas básicas da programação aparecem nesse pequeno exemplo?**
Variáveis, condicionais (`if/elif/else`), laços (`while`, `for`), funções, listas, dicionários,
tuplas, conjuntos (`set`), módulos (`import`), números aleatórios (`random`) e o tratamento
de erros com `try/finally`.
