# Passo a passo

Este documento tem duas partes:

1. **[Como rodar o jogo](#parte-1-como-rodar-o-jogo)**: do zero, para quem nunca rodou um projeto Python
2. **[Como o jogo foi construído](#parte-2-como-o-jogo-foi-construído)**: etapa por etapa, do primeiro
   boneco andando até o chefe final. Cada etapa acrescenta **uma** ideia nova, como o tutorial recomenda:
   *"Não tente resolver tudo de uma vez. Implemente uma funcionalidade por vez."*

---

## Parte 1: Como rodar o jogo

### 1. Instalar o Python

Baixe em [python.org/downloads](https://www.python.org/downloads/) e, na instalação,
**marque a opção "Add Python to PATH"**.

Para conferir, abra o terminal (tecla Windows → digite `cmd` → Enter) e rode:

```bash
python --version
```

### 2. Baixar o projeto

Pelo GitHub: botão verde **Code** → **Download ZIP**, e depois extraia a pasta.
Ou, se tiver o Git instalado:

```bash
git clone https://github.com/NicSSC/jogoPythonTerminal.git
```

### 3. Instalar a biblioteca WConio2

É a mesma biblioteca usada no tutorial da aula, para ler o teclado sem travar o jogo:

```bash
pip install WConio2
```

### 4. Rodar

Entre na pasta do projeto e execute:

```bash
cd jogoPythonTerminal
python jogo.py
```

### Problemas comuns

| Problema | Solução |
|---|---|
| `ModuleNotFoundError: No module named 'WConio2'` | rode `pip install WConio2` de novo |
| Aparecem `?` ou quadradinhos no lugar dos símbolos | use o **Terminal do Windows**, ou no `cmd` troque a fonte para *Consolas* |
| O mapa aparece cortado ou torto | aumente a largura da janela (pelo menos 70 colunas) |
| Aparecem códigos estranhos tipo `[91m` | use o Terminal do Windows (Windows 10 ou mais novo) |

> O jogo usa `WConio2`, que só funciona no **Windows**.

---

## Parte 2: Como o jogo foi construído

### Etapa 1: O desafio do tutorial (boneco que anda até o objetivo)

Tudo começou com o desafio da seção 13 do tutorial: o jogador controla um personagem
e precisa chegar até o objetivo, sem atravessar as paredes.

```python
import os
import time
import WConio2

largura = 40
altura = 7

x = 2               # posição do jogador
y = 3
estrela_x = 30      # posição do objetivo
estrela_y = 3

while True:
    os.system("cls")

    # desenha o cenário linha por linha
    for linha in range(altura):
        if linha == 0 or linha == altura - 1:
            print(largura * "#")
        else:
            texto = ""
            for coluna in range(largura):
                if coluna == 0 or coluna == largura - 1:
                    texto = texto + "#"
                elif coluna == x and linha == y:
                    texto = texto + "☺"
                elif coluna == estrela_x and linha == estrela_y:
                    texto = texto + "♥"
                else:
                    texto = texto + " "
            print(texto)

    # detecta vitória: mesma posição = colisão
    if x == estrela_x and y == estrela_y:
        print("Você venceu!")
        break

    if WConio2.kbhit():
        comando = WConio2.getch()
        tecla = comando[1].lower()   # o getch devolve (codigo, letra)

        novo_x = x
        novo_y = y
        if tecla == "a": novo_x = x - 1
        if tecla == "d": novo_x = x + 1
        if tecla == "w": novo_y = y - 1
        if tecla == "s": novo_y = y + 1

        # só anda se não for parede
        if 0 < novo_x < largura - 1 and 0 < novo_y < altura - 1:
            x = novo_x
            y = novo_y

    time.sleep(0.05)
```

**Ideias novas:** game loop, estado (`x`, `y`), entrada (`kbhit`/`getch`), colisão com parede, colisão com objetivo.

> **Pegadinha:** o tutorial mostra `comando == "a"`, mas o `WConio2.getch()` devolve uma tupla
> `(codigo, letra)`. Sem pegar o `[1]`, o boneco nunca anda.

---

### Etapa 2: O mapa vira uma matriz

Em vez de calcular as paredes dentro do `for`, guardamos o mapa numa **lista de listas**
(como a seção 10 do tutorial). Assim dá para ter obstáculos em qualquer lugar.

```python
mapa = []
for y in range(ALTURA):
    linha = []
    for x in range(LARGURA):
        if x == 0 or y == 0 or x == LARGURA - 1 or y == ALTURA - 1:
            linha.append("#")
        else:
            linha.append(".")
    mapa.append(linha)

mapa[3][10] = "O"   # um obstáculo na linha 3, coluna 10
```

E a regra de andar fica mais simples: *"só anda se a casa nova não for parede nem obstáculo"*.

```python
if mapa[novo_y][novo_x] not in ("#", "O"):
    x = novo_x
    y = novo_y
```

**Ideia nova:** separar **o que existe** (o mapa) de **como é desenhado**.

---

### Etapa 3: Estado em dicionários

Com muitas variáveis soltas (`x`, `y`, `vida`, `dano`...) o código fica confuso.
Juntamos tudo do jogador num **dicionário**:

```python
jogador = {"x": 2, "y": 7, "vida": 6, "dano": 2}
jogador["x"] += 1
```

O mesmo para a sala: `sala = {"mapa": ..., "inimigos": [], "tiros": []}`.
Agora as funções recebem `jogador` e `sala` e conseguem mudar o estado.

**Ideia nova:** dicionários para agrupar o estado; funções que recebem o estado.

---

### Etapa 4: Cores e tela sem piscar

Duas melhorias visuais:

1. **Cores ANSI**: `"\033[91m"` deixa o texto vermelho, `"\033[0m"` volta ao normal.
   No Windows, é preciso rodar `os.system("")` uma vez para ligar isso.
2. **Sem piscar**: em vez de `os.system("cls")` a cada quadro, voltamos o cursor para o topo
   com `print("\033[H")` e desenhamos por cima. Também montamos o quadro inteiro numa string
   e damos **um único `print`**, que é bem mais rápido.

**Ideia nova:** códigos de escape do terminal.

---

### Etapa 5: Atirar (lágrimas)

Um tiro é só mais um "objeto" com estado: posição, direção e alcance.

```python
tiro = {"x": jogador["x"], "y": jogador["y"], "dx": 1, "dy": 0, "alcance": 8}
sala["tiros"].append(tiro)
```

A cada quadro, todo tiro anda 1 casa (`tiro["x"] += tiro["dx"]`) e some se bater em algo
ou se o alcance acabar. As setas do teclado chegam como dois códigos (`224` e depois `72`, `80`, `75` ou `77`).

Para não metralhar, existe uma **recarga**: depois de atirar, o jogador espera alguns quadros.

**Ideias novas:** listas de objetos que nascem e morrem; contadores de tempo em quadros.

---

### Etapa 6: Inimigos

Cada inimigo é um dicionário com posição e vida, e fica numa lista `sala["inimigos"]`.
Para perseguir o jogador, o inimigo dá um passo na direção dele:

```python
dx = jogador["x"] - inimigo["x"]
passo_x = sinal(dx)     # 1, -1 ou 0
```

Para cada tipo andar numa velocidade, ele tem uma `espera`: só anda a cada N quadros.
Depois vieram os comportamentos diferentes (`ia`): aleatório, perseguir, fantasma, atirador.

**Ideias novas:** vários objetos com o mesmo "molde"; comportamento escolhido por um campo do dicionário.

---

### Etapa 7: Batalha e sistema de vida

- **Tiro acerta inimigo** quando os dois estão na mesma casa → inimigo perde vida
- **Inimigo encosta no jogador** → jogador perde vida
- **Invencibilidade**: depois de levar dano, o jogador fica 25 quadros sem poder levar dano de novo
  (e pisca na tela). Sem isso, um inimigo encostado mataria em menos de 1 segundo
- **Vida em corações** no topo da tela (`♥` vermelho = cheio, `♥` cinza = vazio)
- Quando a vida chega a 0 → **fim de jogo**

**Ideia nova:** regras do mundo do jogo, como o tutorial fala na seção 7.

---

### Etapa 8: Várias salas com cenários diferentes

Os dados de cada sala foram para uma lista `SALAS` no arquivo `dados.py`: nome, caracteres e
cores de parede, chão e obstáculo, quais inimigos aparecem e qual o **layout** (pilares, rio, cantos...).

O mapa guarda só **códigos** (`#`, `.`, `O`), e na hora de desenhar cada sala traduz do seu jeito:
na Floresta a parede é `♣` verde, na Forja é `▓` vermelho.

Quando todos os inimigos morrem, a porta abre. Passando pela porta, vai para a próxima sala:

```python
for numero in range(len(SALAS)):
    sala = criar_sala(numero, jogador)
    resultado = jogar_sala(jogador, sala)
    if resultado == "morreu":
        ...
```

**Ideias novas:** separar dados e lógica em arquivos diferentes; progressão de fases.

---

### Etapa 9: Obstáculos aleatórios (sem prender o jogador)

Sorteamos posições com `random.randint()` e colocamos obstáculos, **exceto** nas áreas protegidas
(onde o jogador nasce e a frente da porta).

Problema: os obstáculos podem fechar o caminho até a porta! A solução foi uma
**busca em largura (BFS)**, que descobre todas as casas que dá para alcançar. Se a porta não estiver
entre elas, a sala é gerada de novo.

```python
for tentativa in range(100):
    mapa = gerar_mapa_com_obstaculos()
    if porta in casas_alcancaveis(mapa, inicio):
        return mapa
```

**Ideias novas:** aleatoriedade com garantia; um algoritmo clássico (BFS) resolvendo um problema real.

---

### Etapa 10: Baús e itens

Quando a sala é limpa, aparece um **baú** num lugar sorteado entre as casas alcançáveis que
**não são onde o jogador está** (e ficam a pelo menos 4 casas dele). Ao pisar no baú, sai um prêmio
sorteado: cura, vida máxima, dano, alcance, velocidade de tiro ou energia.

Os inimigos também têm 15% de chance de deixar cair um coração.

**Ideia nova:** `random.choice()` numa lista de dicionários; usar `min()`/`max()` para limitar valores.

---

### Etapa 11: Personagens e poderes

Três personagens com atributos diferentes, escolhidos no começo. Cada um tem um **poder** (tecla `E`)
que gasta **energia**, e a energia carrega matando inimigos:

- **Cavaleiro**: dano em área (todo inimigo a até 3 casas)
- **Maga**: dano em todos os inimigos da sala
- **Ladino**: invencível e dano dobrado por 4 segundos

**Ideia nova:** o mesmo código funcionando com dados diferentes (é só trocar o dicionário do personagem).

---

### Etapa 12: O chefe final e os menus

O **Devorador** é um inimigo com muita vida que:
- atira em 4 direções (alternando `+` e `x`)
- chama moscas para ajudar
- fica mais rápido com menos da metade da vida
- tem uma barra de vida própria no topo da tela

Por fim vieram as telas de título, escolha de personagem, transição entre salas, pausa e
fim de jogo (com estatísticas).

---

### Etapa 13: Ajustes finais (jogabilidade)

Coisas que só aparecem jogando:

- **Andar rápido demais**: 1 casa por quadro eram 20 casas por segundo. Agora o jogador
  anda a cada 2 quadros
- **Andar e atirar ao mesmo tempo**: no terminal do Windows, segurando duas teclas, só a última repete.
  Solução: depois de apertar uma seta, o personagem continua atirando sozinho por um instante
- **Velocidade igual em qualquer PC**: o loop mede quanto tempo o quadro gastou e só dorme o que falta
  para completar 1/20 de segundo
- **Tiros inimigos mais lentos** (metade da velocidade), para dar para desviar

---

## Ideias para continuar o projeto

- Mapa com várias salas conectadas (cima, baixo, esquerda, direita), como no Isaac de verdade
- Salvar o recorde (menor tempo) num arquivo `.txt`
- Itens passivos que mudam o tiro (tiro triplo, tiro que atravessa)
- Uma loja entre as salas
- Mais chefes, um a cada 5 salas
