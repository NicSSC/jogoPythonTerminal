# ============================================================
#  JOGO PYTHON TERMINAL
#  Um joguinho estilo "roguelike" feito no terminal com Python.
#
#  Para rodar (no Windows):
#     pip install WConio2
#     python jogo.py
#
#  Arquivos:
#     jogo.py  -> logica do jogo (este arquivo)
#     dados.py -> personagens, inimigos, salas e itens
#     tela.py  -> tudo que desenha na tela
# ============================================================

import random
import time

import WConio2

import tela
from dados import (LARGURA, ALTURA, PERSONAGENS, INIMIGOS, SALAS,
                   CONTEUDO_BAUS, ENERGIA_MAXIMA, VIDA_MAXIMA_LIMITE)

# posicoes importantes do mapa
MEIO = ALTURA // 2          # linha do meio
PORTA_X = LARGURA - 1       # a porta fica na parede da direita
INICIO_X = 2                # onde o jogador nasce em cada sala

DIRECOES = [(1, 0), (-1, 0), (0, 1), (0, -1)]
QUADROS_POR_SEGUNDO = 20


# ============================================================
# TECLADO
# ============================================================
def ler_teclas():
    """Le todas as teclas apertadas desde o ultimo quadro, sem travar o jogo."""
    teclas = []
    while WConio2.kbhit():
        codigo, letra = WConio2.getch()   # o getch devolve (codigo, letra)
        if codigo == 0 or codigo == 224:
            # setas do teclado chegam em duas partes: 224 e depois o codigo da seta
            codigo2, letra2 = WConio2.getch()
            if codigo2 == 72:
                teclas.append("cima")
            elif codigo2 == 80:
                teclas.append("baixo")
            elif codigo2 == 75:
                teclas.append("esquerda")
            elif codigo2 == 77:
                teclas.append("direita")
        else:
            teclas.append(letra.lower())
    return teclas


def esvaziar_teclado():
    while WConio2.kbhit():
        WConio2.getch()


def esperar_tecla():
    """Espera o jogador apertar uma tecla (aqui pode travar, e um menu)."""
    esvaziar_teclado()
    codigo, letra = WConio2.getch()
    if codigo == 0 or codigo == 224:
        WConio2.getch()
        return ""
    if codigo == 13:
        return "enter"
    return letra.lower()


# ============================================================
# CRIACAO DO MAPA
# Codigos do mapa:  "#" parede   "." chao   "O" obstaculo
#                   "~" perigo   "P" porta
# ============================================================
def mapa_vazio():
    mapa = []
    for y in range(ALTURA):
        linha = []
        for x in range(LARGURA):
            if x == 0 or y == 0 or x == LARGURA - 1 or y == ALTURA - 1:
                linha.append("#")
            else:
                linha.append(".")
        mapa.append(linha)
    mapa[MEIO][PORTA_X] = "P"
    return mapa


def area_protegida(x, y):
    """Lugares que precisam ficar livres: onde o jogador nasce e a frente da porta."""
    perto_do_meio = abs(y - MEIO) <= 1
    if perto_do_meio and x <= 4:
        return True
    if perto_do_meio and x >= LARGURA - 5:
        return True
    return False


def colocar(mapa, x, y, codigo):
    """Coloca algo no mapa so se a casa for chao e nao for protegida."""
    if 0 < x < LARGURA - 1 and 0 < y < ALTURA - 1:
        if mapa[y][x] == "." and not area_protegida(x, y):
            mapa[y][x] = codigo


def aplicar_layout(mapa, layout, tem_perigo):
    """Cada layout e um formato fixo que deixa as salas diferentes entre si."""
    if layout == "pilares":
        for x in range(6, LARGURA - 5, 7):
            for y in (3, ALTURA - 4):
                colocar(mapa, x, y, "O")
                colocar(mapa, x + 1, y, "O")

    elif layout == "cantos":
        for x0, y0 in [(3, 2), (LARGURA - 7, 2), (3, ALTURA - 4), (LARGURA - 7, ALTURA - 4)]:
            for dx in range(4):
                for dy in range(2):
                    colocar(mapa, x0 + dx, y0 + dy, "O")

    elif layout == "rio":
        # um rio no meio da sala com uma ponte
        meio_x = LARGURA // 2
        for y in range(1, ALTURA - 1):
            if abs(y - MEIO) > 1:
                colocar(mapa, meio_x, y, "~")
                colocar(mapa, meio_x + 1, y, "~")

    elif layout == "lagoas":
        codigo = "~" if tem_perigo else "O"
        for i in range(4):
            x0 = random.randint(5, LARGURA - 9)
            y0 = random.randint(2, ALTURA - 5)
            for dx in range(random.randint(2, 4)):
                for dy in range(2):
                    colocar(mapa, x0 + dx, y0 + dy, codigo)

    elif layout == "corredor":
        # duas fileiras de estantes com buracos para passar
        for x in range(4, LARGURA - 4):
            if x % 8 != 0:
                colocar(mapa, x, 4, "O")
                colocar(mapa, x, ALTURA - 5, "O")


def colocar_obstaculos_aleatorios(mapa, quantidade):
    """Obstaculos em lugares aleatorios, nunca onde o jogador esta (area protegida)."""
    colocados = 0
    tentativas = 0
    while colocados < quantidade and tentativas < 500:
        tentativas += 1
        x = random.randint(1, LARGURA - 2)
        y = random.randint(1, ALTURA - 2)
        if mapa[y][x] == "." and not area_protegida(x, y):
            mapa[y][x] = "O"
            colocados += 1


def casas_alcancaveis(mapa, inicio_x, inicio_y):
    """Busca em largura (BFS): descobre todas as casas que o jogador consegue alcancar."""
    visitados = set()
    fila = [(inicio_x, inicio_y)]
    visitados.add((inicio_x, inicio_y))
    while len(fila) > 0:
        x, y = fila.pop(0)
        for dx, dy in DIRECOES:
            nx = x + dx
            ny = y + dy
            if (nx, ny) not in visitados and mapa[ny][nx] in (".", "~"):
                visitados.add((nx, ny))
                fila.append((nx, ny))
    return visitados


def criar_mapa(dados_sala):
    """Gera o mapa e confere se da para chegar na porta. Se nao der, gera de novo."""
    for tentativa in range(100):
        mapa = mapa_vazio()
        aplicar_layout(mapa, dados_sala["layout"], dados_sala["perigo"] is not None)
        colocar_obstaculos_aleatorios(mapa, dados_sala["obstaculos"])
        alcancaveis = casas_alcancaveis(mapa, INICIO_X, MEIO)
        if (PORTA_X - 1, MEIO) in alcancaveis:
            return mapa
    return mapa_vazio()


# ============================================================
# CRIACAO DO JOGADOR E DA SALA
# ============================================================
def criar_jogador(personagem):
    jogador = {
        "nome": personagem["nome"],
        "simbolo": personagem["simbolo"],
        "cor": personagem["cor"],
        "vida": personagem["vida"],
        "vida_max": personagem["vida"],
        "dano": personagem["dano"],
        "alcance": personagem["alcance"],
        "recarga": personagem["recarga"],
        "poder": personagem["poder"],
        "nome_poder": personagem["nome_poder"],
        "custo_poder": personagem["custo_poder"],
        "energia": 2,
        "x": INICIO_X,
        "y": MEIO,
        "espera_tiro": 0,
        "espera_passo": 0,     # quadros ate poder dar o proximo passo
        "passo_pendente": None,
        "tiro_direcao": None,  # ultima direcao de tiro
        "tiro_tempo": 0,       # por quantos quadros ainda continua atirando
        "invencivel": 0,   # quadros sem levar dano depois de ser atingido
        "sombra": 0,       # quadros restantes do poder do Ladino
        "abates": 0,
        "baus": 0,
    }
    return jogador


def criar_inimigo(tipo, x, y):
    dados = INIMIGOS[tipo]
    return {
        "tipo": tipo,
        "x": x,
        "y": y,
        "vida": dados["vida"],
        "vida_max": dados["vida"],
        "contador": random.randint(0, dados["espera"]),   # para nao andarem todos juntos
        "contador_tiro": random.randint(0, 15),
        "piscando": 0,
    }


def casas_livres(sala, jogador, distancia_minima):
    """Casas de chao alcancaveis, longe do jogador e sem nada em cima."""
    livres = []
    alcancaveis = casas_alcancaveis(sala["mapa"], jogador["x"], jogador["y"])
    for x, y in alcancaveis:
        if sala["mapa"][y][x] != ".":
            continue
        if (x, y) == (jogador["x"], jogador["y"]):
            continue
        distancia = abs(x - jogador["x"]) + abs(y - jogador["y"])
        if distancia < distancia_minima:
            continue
        if area_protegida(x, y):
            continue
        if inimigo_em(sala, x, y) is not None or item_em(sala, x, y) is not None:
            continue
        livres.append((x, y))
    return livres


def criar_sala(numero, jogador):
    dados_sala = SALAS[numero]
    sala = {
        "numero": numero,
        "dados": dados_sala,
        "mapa": criar_mapa(dados_sala),
        "inimigos": [],
        "tiros": [],
        "itens": [],
        "efeitos": [],
        "porta_aberta": False,
        "mensagem": "",
        "tempo_mensagem": 0,
        "quadro": 0,
    }

    # o jogador sempre entra pela esquerda
    jogador["x"] = INICIO_X
    jogador["y"] = MEIO
    jogador["invencivel"] = 20   # um tempinho de protecao ao entrar
    jogador["sombra"] = 0
    jogador["tiro_tempo"] = 0
    jogador["passo_pendente"] = None

    # inimigos nascem longe do jogador
    for tipo in dados_sala["inimigos"]:
        if tipo == "chefe":
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    sala["mapa"][MEIO + dy][LARGURA - 10 + dx] = "."
            sala["inimigos"].append(criar_inimigo("chefe", LARGURA - 10, MEIO))
            continue
        livres = casas_livres(sala, jogador, 12)
        if len(livres) == 0:
            livres = casas_livres(sala, jogador, 4)
        x, y = random.choice(livres)
        sala["inimigos"].append(criar_inimigo(tipo, x, y))

    mostrar_mensagem(sala, "Derrote todos os inimigos para abrir a porta!")
    return sala


# ============================================================
# FUNCOES DE AJUDA
# ============================================================
def mostrar_mensagem(sala, texto, segundos=3):
    sala["mensagem"] = texto
    sala["tempo_mensagem"] = segundos * QUADROS_POR_SEGUNDO


def inimigo_em(sala, x, y):
    for inimigo in sala["inimigos"]:
        if inimigo["x"] == x and inimigo["y"] == y:
            return inimigo
    return None


def item_em(sala, x, y):
    for item in sala["itens"]:
        if item["x"] == x and item["y"] == y:
            return item
    return None


def sinal(numero):
    if numero > 0:
        return 1
    if numero < 0:
        return -1
    return 0


def adicionar_efeito(sala, x, y, simbolo, cor, quadros):
    if 0 < x < LARGURA - 1 and 0 < y < ALTURA - 1:
        sala["efeitos"].append({"x": x, "y": y, "simbolo": simbolo, "cor": cor, "tempo": quadros})


# ============================================================
# BATALHA: DANO NO JOGADOR E NOS INIMIGOS
# ============================================================
def jogador_leva_dano(jogador, sala, quantidade, motivo):
    if jogador["invencivel"] > 0:
        return
    jogador["vida"] -= quantidade
    jogador["invencivel"] = 25   # pisca por pouco mais de 1 segundo
    if jogador["vida"] > 0:
        mostrar_mensagem(sala, motivo + " -" + str(quantidade) + " de vida", 2)


def ferir_inimigo(jogador, sala, inimigo, dano):
    if inimigo not in sala["inimigos"]:
        return
    inimigo["vida"] -= dano
    inimigo["piscando"] = 3
    if inimigo["vida"] <= 0:
        matar_inimigo(jogador, sala, inimigo)


def matar_inimigo(jogador, sala, inimigo):
    sala["inimigos"].remove(inimigo)
    jogador["abates"] += 1
    jogador["energia"] = min(ENERGIA_MAXIMA, jogador["energia"] + 1)
    adicionar_efeito(sala, inimigo["x"], inimigo["y"], "*", "93", 4)

    if inimigo["tipo"] == "chefe":
        # quando o chefe morre, os ajudantes morrem junto
        for ajudante in list(sala["inimigos"]):
            adicionar_efeito(sala, ajudante["x"], ajudante["y"], "*", "93", 6)
            sala["inimigos"].remove(ajudante)
        mostrar_mensagem(sala, "O DEVORADOR FOI DERROTADO!", 4)
    elif random.random() < 0.15:
        # as vezes o inimigo deixa cair um coracao
        sala["itens"].append({"x": inimigo["x"], "y": inimigo["y"], "tipo": "coracao"})


# ============================================================
# JOGADOR: ANDAR, ATIRAR, PODER, PEGAR ITENS
# ============================================================
def mover_jogador(jogador, sala, dx, dy):
    nx = jogador["x"] + dx
    ny = jogador["y"] + dy
    celula = sala["mapa"][ny][nx]

    if celula == "P":
        if sala["porta_aberta"]:
            return "porta"
        mostrar_mensagem(sala, "A porta está trancada! Derrote todos os inimigos.", 2)
        return None
    if celula == "#" or celula == "O":
        return None

    inimigo = inimigo_em(sala, nx, ny)
    if inimigo is not None:
        # encostou no inimigo: leva dano e nao anda
        jogador_leva_dano(jogador, sala, INIMIGOS[inimigo["tipo"]]["dano"], "Você esbarrou em um inimigo!")
        return None

    jogador["x"] = nx
    jogador["y"] = ny

    item = item_em(sala, nx, ny)
    if item is not None:
        pegar_item(jogador, sala, item)
    return None


def pegar_item(jogador, sala, item):
    sala["itens"].remove(item)
    if item["tipo"] == "coracao":
        if jogador["vida"] < jogador["vida_max"]:
            jogador["vida"] += 1
        mostrar_mensagem(sala, "Você pegou um coração! ♥", 2)
    elif item["tipo"] == "bau":
        abrir_bau(jogador, sala)


def abrir_bau(jogador, sala):
    jogador["baus"] += 1
    premio = random.choice(CONTEUDO_BAUS)
    efeito = premio["efeito"]

    if efeito == "cura":
        jogador["vida"] = min(jogador["vida_max"], jogador["vida"] + 2)
    elif efeito == "vida_max":
        if jogador["vida_max"] < VIDA_MAXIMA_LIMITE:
            jogador["vida_max"] += 1
        jogador["vida"] = min(jogador["vida_max"], jogador["vida"] + 1)
    elif efeito == "dano":
        jogador["dano"] += 1
    elif efeito == "alcance":
        jogador["alcance"] += 2
    elif efeito == "recarga":
        jogador["recarga"] = max(2, jogador["recarga"] - 1)
    elif efeito == "energia":
        jogador["energia"] = ENERGIA_MAXIMA

    for dx, dy in DIRECOES:
        adicionar_efeito(sala, jogador["x"] + dx, jogador["y"] + dy, "+", "93", 6)
    mostrar_mensagem(sala, "Baú aberto: " + premio["nome"] + "! (" + premio["texto"] + ")", 4)


def atirar(jogador, sala, dx, dy):
    if jogador["espera_tiro"] > 0:
        return
    dano = jogador["dano"]
    if jogador["sombra"] > 0:
        dano = dano * 2
    sala["tiros"].append({
        "x": jogador["x"], "y": jogador["y"],
        "dx": dx, "dy": dy,
        "alcance": jogador["alcance"],
        "dano": dano,
        "do_jogador": True,
    })
    jogador["espera_tiro"] = jogador["recarga"]


def usar_poder(jogador, sala):
    if jogador["energia"] < jogador["custo_poder"]:
        mostrar_mensagem(sala, "Energia insuficiente! Derrote inimigos para carregar.", 2)
        return
    jogador["energia"] -= jogador["custo_poder"]

    if jogador["poder"] == "giro":
        # ataque em area em volta do jogador
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                x = jogador["x"] + dx
                y = jogador["y"] + dy
                if dx == 0 and dy == 0:
                    continue
                if 0 < x < LARGURA - 1 and 0 < y < ALTURA - 1 and sala["mapa"][y][x] != "O":
                    adicionar_efeito(sala, x, y, "*", "94", 5)
        for inimigo in list(sala["inimigos"]):
            if abs(inimigo["x"] - jogador["x"]) <= 3 and abs(inimigo["y"] - jogador["y"]) <= 3:
                ferir_inimigo(jogador, sala, inimigo, 4)
        mostrar_mensagem(sala, "GIRO DE ESPADA!", 2)

    elif jogador["poder"] == "tempestade":
        # raios caem em todos os inimigos
        for inimigo in list(sala["inimigos"]):
            adicionar_efeito(sala, inimigo["x"], inimigo["y"] - 1, "!", "93", 6)
            ferir_inimigo(jogador, sala, inimigo, 3)
        for i in range(15):
            adicionar_efeito(sala, random.randint(1, LARGURA - 2), random.randint(1, ALTURA - 2), "!", "95", 6)
        mostrar_mensagem(sala, "TEMPESTADE ARCANA!", 2)

    elif jogador["poder"] == "sombra":
        jogador["sombra"] = 4 * QUADROS_POR_SEGUNDO
        jogador["invencivel"] = 4 * QUADROS_POR_SEGUNDO
        mostrar_mensagem(sala, "MANTO DE SOMBRA! Invencível e dano dobrado.", 3)


def atualizar_jogador(jogador, sala):
    if jogador["espera_tiro"] > 0:
        jogador["espera_tiro"] -= 1
    if jogador["espera_passo"] > 0:
        jogador["espera_passo"] -= 1
    if jogador["tiro_tempo"] > 0:
        jogador["tiro_tempo"] -= 1
    if jogador["invencivel"] > 0:
        jogador["invencivel"] -= 1
    if jogador["sombra"] > 0:
        jogador["sombra"] -= 1

    # pisando no chao perigoso (agua toxica, lava...)
    if sala["mapa"][jogador["y"]][jogador["x"]] == "~":
        jogador_leva_dano(jogador, sala, 1, "Ai! Isso queima!")


# ============================================================
# TIROS (LAGRIMAS)
# ============================================================
def atualizar_tiros(jogador, sala):
    restantes = []
    for tiro in sala["tiros"]:
        # tiros dos inimigos andam na metade da velocidade (da para desviar)
        if not tiro["do_jogador"] and sala["quadro"] % 2 == 1:
            restantes.append(tiro)
            continue

        tiro["x"] += tiro["dx"]
        tiro["y"] += tiro["dy"]
        tiro["alcance"] -= 1

        celula = sala["mapa"][tiro["y"]][tiro["x"]]
        if celula == "O" and tiro["do_jogador"] and inimigo_em(sala, tiro["x"], tiro["y"]) is not None:
            restantes.append(tiro)   # fantasma escondido no obstaculo tambem leva dano
            continue
        if celula in ("#", "O", "P"):
            adicionar_efeito(sala, tiro["x"], tiro["y"], "°", "37", 2)
            continue
        if tiro["alcance"] <= 0:
            continue
        restantes.append(tiro)
    sala["tiros"] = restantes


def checar_acertos(jogador, sala):
    """Ve se alguma lagrima encostou em alguem."""
    restantes = []
    for tiro in sala["tiros"]:
        acertou = False
        if tiro["do_jogador"]:
            inimigo = inimigo_em(sala, tiro["x"], tiro["y"])
            if inimigo is not None:
                ferir_inimigo(jogador, sala, inimigo, tiro["dano"])
                acertou = True
        else:
            if tiro["x"] == jogador["x"] and tiro["y"] == jogador["y"]:
                jogador_leva_dano(jogador, sala, tiro["dano"], "Você foi atingido!")
                acertou = True
        if not acertou:
            restantes.append(tiro)
    sala["tiros"] = restantes


# ============================================================
# INIMIGOS: INTELIGENCIA ARTIFICIAL
# ============================================================
def inimigo_pode_ir(sala, inimigo, x, y, atravessa):
    celula = sala["mapa"][y][x]
    if celula == "#" or celula == "P":
        return False
    if celula == "O" and not atravessa:
        return False
    if inimigo_em(sala, x, y) is not None:
        return False
    if item_em(sala, x, y) is not None:
        return False
    return True


def passos_ate_jogador(inimigo, jogador):
    """Lista de passos, do melhor para o pior, para chegar perto do jogador."""
    dx = jogador["x"] - inimigo["x"]
    dy = jogador["y"] - inimigo["y"]
    passo_x = (sinal(dx), 0)
    passo_y = (0, sinal(dy))
    if abs(dx) >= abs(dy):
        passos = [passo_x, passo_y]
    else:
        passos = [passo_y, passo_x]
    # tira os passos "parados" (0, 0)
    resultado = []
    for passo in passos:
        if passo != (0, 0):
            resultado.append(passo)
    return resultado


def inimigo_atira(sala, inimigo, dx, dy):
    sala["tiros"].append({
        "x": inimigo["x"], "y": inimigo["y"],
        "dx": dx, "dy": dy,
        "alcance": 30,
        "dano": 1,
        "do_jogador": False,
    })


def atualizar_inimigos(jogador, sala):
    for inimigo in list(sala["inimigos"]):
        tipo = INIMIGOS[inimigo["tipo"]]
        ia = tipo["ia"]

        if inimigo["piscando"] > 0:
            inimigo["piscando"] -= 1

        # ---- tiros dos inimigos que atiram ----
        if "espera_tiro" in tipo:
            inimigo["contador_tiro"] += 1
            if inimigo["contador_tiro"] >= tipo["espera_tiro"]:
                if ia == "chefe":
                    inimigo["contador_tiro"] = 0
                    # alterna entre atirar em + e em x
                    if random.random() < 0.5:
                        direcoes = DIRECOES
                    else:
                        direcoes = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                    for dx, dy in direcoes:
                        inimigo_atira(sala, inimigo, dx, dy)
                    # o chefe chama moscas para ajudar
                    if len(sala["inimigos"]) < 4 and random.random() < 0.5:
                        for dx, dy in DIRECOES:
                            x = inimigo["x"] + dx
                            y = inimigo["y"] + dy
                            if inimigo_pode_ir(sala, inimigo, x, y, False) and (x, y) != (jogador["x"], jogador["y"]):
                                sala["inimigos"].append(criar_inimigo("mosca", x, y))
                                break
                else:
                    mesma_linha = inimigo["y"] == jogador["y"]
                    mesma_coluna = inimigo["x"] == jogador["x"]
                    if mesma_linha or mesma_coluna or random.random() < 0.3:
                        inimigo["contador_tiro"] = 0
                        passos = passos_ate_jogador(inimigo, jogador)
                        if len(passos) > 0:
                            inimigo_atira(sala, inimigo, passos[0][0], passos[0][1])

        # ---- movimento ----
        espera = tipo["espera"]
        if ia == "chefe" and inimigo["vida"] < inimigo["vida_max"] // 2:
            espera = 3   # chefe fica furioso com metade da vida
        inimigo["contador"] += 1
        if inimigo["contador"] < espera:
            continue
        inimigo["contador"] = 0

        if ia == "perseguir" or ia == "chefe" or ia == "fantasma":
            passos = passos_ate_jogador(inimigo, jogador)
        elif ia == "aleatorio":
            if random.random() < 0.5:
                passos = passos_ate_jogador(inimigo, jogador)
            else:
                passos = list(DIRECOES)
                random.shuffle(passos)
        elif ia == "atirador":
            if random.random() < 0.3:
                passos = list(DIRECOES)
                random.shuffle(passos)
            else:
                passos = []
        else:
            passos = []

        atravessa = (ia == "fantasma")
        for dx, dy in passos:
            nx = inimigo["x"] + dx
            ny = inimigo["y"] + dy
            if (nx, ny) == (jogador["x"], jogador["y"]):
                # chegou no jogador: ataca!
                jogador_leva_dano(jogador, sala, tipo["dano"], tipo["nome"] + " te atacou!")
                break
            if inimigo_pode_ir(sala, inimigo, nx, ny, atravessa):
                inimigo["x"] = nx
                inimigo["y"] = ny
                break


# ============================================================
# SALA LIMPA: ABRE A PORTA E APARECE O BAU
# ============================================================
def checar_sala_limpa(jogador, sala):
    if len(sala["inimigos"]) > 0 or sala["porta_aberta"]:
        return
    sala["porta_aberta"] = True
    sala["tiros"] = []

    # o bau aparece num lugar aleatorio onde o jogador NAO esta
    livres = casas_livres(sala, jogador, 4)
    if len(livres) == 0:
        livres = casas_livres(sala, jogador, 1)
    if len(livres) > 0:
        x, y = random.choice(livres)
        sala["itens"].append({"x": x, "y": y, "tipo": "bau"})
        adicionar_efeito(sala, x, y - 1, "+", "93", 10)
        mostrar_mensagem(sala, "Sala limpa! Um baú ■ apareceu e a porta abriu →", 4)
    else:
        mostrar_mensagem(sala, "Sala limpa! A porta abriu →", 4)


def atualizar_efeitos(sala):
    restantes = []
    for efeito in sala["efeitos"]:
        efeito["tempo"] -= 1
        if efeito["tempo"] > 0:
            restantes.append(efeito)
    sala["efeitos"] = restantes
    if sala["tempo_mensagem"] > 0:
        sala["tempo_mensagem"] -= 1


# ============================================================
# LOOP DE UMA SALA (o "game loop")
#   1. ler teclado  2. atualizar o estado  3. desenhar  4. esperar
# ============================================================
def jogar_sala(jogador, sala):
    tela.limpar()
    while True:
        inicio = time.time()
        sala["quadro"] += 1

        # 1. ENTRADA
        movimento = None
        direcao_tiro = None
        quer_poder = False
        for tecla in ler_teclas():
            if tecla == "w":
                movimento = (0, -1)
            elif tecla == "s":
                movimento = (0, 1)
            elif tecla == "a":
                movimento = (-1, 0)
            elif tecla == "d":
                movimento = (1, 0)
            elif tecla == "cima" or tecla == "i":
                direcao_tiro = (0, -1)
            elif tecla == "baixo" or tecla == "k":
                direcao_tiro = (0, 1)
            elif tecla == "esquerda" or tecla == "j":
                direcao_tiro = (-1, 0)
            elif tecla == "direita" or tecla == "l":
                direcao_tiro = (1, 0)
            elif tecla == "e":
                quer_poder = True
            elif tecla == "p":
                tela.tela_pausa()
                esperar_tecla()
                tela.limpar()
            elif tecla == "q":
                return "sair"

        # 2. ATUALIZACAO
        # o jogador da no maximo 1 passo a cada 2 quadros (fica mais controlavel)
        if movimento is not None:
            jogador["passo_pendente"] = movimento
        if jogador["passo_pendente"] is not None and jogador["espera_passo"] == 0:
            dx, dy = jogador["passo_pendente"]
            jogador["passo_pendente"] = None
            jogador["espera_passo"] = 2
            if mover_jogador(jogador, sala, dx, dy) == "porta":
                return "proxima"

        # No terminal do Windows, se voce segura duas teclas, so a ultima repete.
        # Entao, depois de apertar uma seta, o personagem continua atirando
        # sozinho por um tempinho. Assim da para andar e atirar ao mesmo tempo!
        if direcao_tiro is not None:
            jogador["tiro_direcao"] = direcao_tiro
            jogador["tiro_tempo"] = 15
        if jogador["tiro_tempo"] > 0:
            atirar(jogador, sala, jogador["tiro_direcao"][0], jogador["tiro_direcao"][1])
        if quer_poder:
            usar_poder(jogador, sala)

        atualizar_jogador(jogador, sala)
        atualizar_tiros(jogador, sala)
        checar_acertos(jogador, sala)
        atualizar_inimigos(jogador, sala)
        checar_acertos(jogador, sala)
        atualizar_efeitos(sala)
        checar_sala_limpa(jogador, sala)

        # 3. DESENHO
        tela.desenhar_jogo(jogador, sala)

        if jogador["vida"] <= 0:
            time.sleep(1.5)
            return "morreu"

        # 4. ESPERA (para o jogo rodar na mesma velocidade em qualquer PC)
        tempo_gasto = time.time() - inicio
        espera = 1 / QUADROS_POR_SEGUNDO - tempo_gasto
        if espera > 0:
            time.sleep(espera)


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================
def escolher_personagem():
    tela.tela_escolha_personagem()
    while True:
        tecla = esperar_tecla()
        if tecla in ("1", "2", "3"):
            return PERSONAGENS[int(tecla) - 1]


def jogar_partida():
    personagem = escolher_personagem()
    jogador = criar_jogador(personagem)
    comeco = time.time()

    for numero in range(len(SALAS)):
        tela.tela_transicao(numero)
        esvaziar_teclado()
        sala = criar_sala(numero, jogador)
        resultado = jogar_sala(jogador, sala)

        if resultado == "morreu":
            tela.tela_fim(jogador, False, numero, time.time() - comeco)
            return "fim"
        if resultado == "sair":
            return "sair"

    tela.tela_fim(jogador, True, len(SALAS) - 1, time.time() - comeco)
    return "fim"


def main():
    tela.preparar_terminal()
    try:
        while True:
            tela.tela_titulo()
            tecla = esperar_tecla()
            if tecla == "q":
                break
            if jogar_partida() == "sair":
                break
            # a tela de fim pergunta "Jogar de novo? (S/N)"
            if esperar_tecla() != "s":
                break
    finally:
        tela.restaurar_terminal()
        tela.limpar()
        print("Obrigado por jogar Jogo Python Terminal!")


if __name__ == "__main__":
    main()
