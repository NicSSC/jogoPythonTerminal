# Jogo Python Terminal

Um jogo estilo *roguelike* feito inteiro no terminal com Python.
Você escolhe um herói e sobe os **10 andares da Torre Amaldiçoada**, cheios de inimigos,
abrindo baús, usando poderes, até enfrentar o chefe que governa lá do topo: **o Rei Sombrio**.

O projeto nasceu do tutorial *"Jogos Digitais ASCII"* da disciplina de Linguagens de Programação:
a ideia de **estado + entrada + atualização + desenho** dentro de um `while True`, só que bem expandida.

```
  Andar 6/10 - Salão de Gelo   Ladino ☻
  Vida ♥♥♥♥♥   Energia ■■····  [E] Manto de Sombra (3)
  Dano 1   Alcance 8   Inimigos: 4
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
  ▓.................ж.≈≈..................▓
  ▓...................≈≈.Θ.ж..............▓
  ▓.........■.........≈≈..................▓
  ▓...................≈≈..................▓
  ▓.♦.................≈≈.Θ................▓
  ▓.......................................▓
  ▓.☻..-..................................█
  ▓.......................................▓
  ▓...................≈≈..................▓
  ▓...................≈≈...............♦..▓
  ▓...................≈≈.................♦▓
  ▓......♦...♦........≈≈..................▓
  ▓...................≈≈..................▓
  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

## Como rodar (Windows)

```bash
pip install WConio2
python jogo.py
```

> Use o **Terminal do Windows** (ou o `cmd` com a fonte *Consolas*) com a janela
> de pelo menos 70 colunas, para os símbolos e as cores aparecerem certinho.

## Controles

| Tecla | Ação |
|---|---|
| `W` `A` `S` `D` | andar |
| Setas ou `I` `J` `K` `L` | atacar |
| `E` | usar o poder especial (gasta energia) |
| `P` | pausar |
| `Q` | sair |

## O que tem no jogo

- **3 personagens**, cada um com vida, dano, alcance, velocidade, ataque e poder próprios
  - ♂ **Cavaleiro**: arremessa machadinhas `x` · poder *Giro de Espada* (dano em área em volta dele)
  - ♀ **Maga**: lança bolas de fogo `o` · poder *Tempestade Arcana* (acerta todos os inimigos do andar)
  - ☻ **Ladino**: atira adagas `-` `|` · poder *Manto de Sombra* (fica invencível e causa dano dobrado por 4s)
- **Sistema de batalha em tempo real**: ataques do jogador, tiros dos inimigos, dano por contato
- **Sistema de vida** em corações, com invencibilidade rápida depois de levar dano
- **Sistema de energia** para os poderes (carrega matando inimigos)
- **7 inimigos** com comportamentos diferentes + **1 chefe final**
- **10 andares** em sequência, cada um com tema, cores e formato diferentes
- **Obstáculos aleatórios** que nunca nascem onde o jogador está
- **Baús** que aparecem quando o andar é limpo, sempre num lugar onde o jogador não está
- **Chão perigoso** (água tóxica, lava) e **corações** que caem dos inimigos

## Estrutura do projeto

```
jogoPythonTerminal/
├── jogo.py      # lógica do jogo e o game loop (é o arquivo que você executa)
├── dados.py     # personagens, inimigos, salas e itens dos baús
├── tela.py      # tudo que desenha na tela: mapa, HUD, menus
└── docs/
    ├── explicacao-do-codigo.md   # explicação de cada parte do código
    └── passo-a-passo.md          # como o jogo foi construído, etapa por etapa
```

## Documentação

- [Explicação do código](docs/explicacao-do-codigo.md): o que cada arquivo e cada função faz
- [Passo a passo](docs/passo-a-passo.md): como o jogo foi construído, do `☺` andando até o chefe final
