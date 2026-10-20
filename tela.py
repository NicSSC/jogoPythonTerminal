# ============================================================
#  tela.py
#  Tudo que DESENHA alguma coisa no terminal fica aqui:
#  o mapa da sala, a barra de vida (HUD), os menus e as telas finais.
# ============================================================

import os
import time

from dados import LARGURA, ALTURA, ENERGIA_MAXIMA, INIMIGOS, PERSONAGENS, SALAS


def cor(texto, codigo):
    """Pinta um texto com uma cor ANSI."""
    return "\033[" + codigo + "m" + texto + "\033[0m"


def preparar_terminal():
    # No Windows, os.system("") liga o suporte a cores ANSI no terminal
    os.system("")
    print("\033[?25l", end="")  # esconde o cursor piscando


def restaurar_terminal():
    print("\033[0m\033[?25h")  # volta a cor normal e mostra o cursor


def limpar():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def ir_para_o_topo():
    # Em vez de apagar a tela toda (que faz piscar), so volta o cursor
    # para o canto de cima e desenha por cima do quadro anterior.
    print("\033[H", end="")


# ------------------------------------------------------------
# DESENHO DA SALA
# ------------------------------------------------------------
def desenhar_celula(sala, x, y):
    """Devolve o caractere (ja colorido) do mapa em x, y."""
    dados = sala["dados"]
    celula = sala["mapa"][y][x]

    if celula == "#":
        simbolo, c = dados["parede"]
        return cor(simbolo, c)
    if celula == "O":
        simbolo, c = dados["obstaculo"]
        return cor(simbolo, c)
    if celula == "~":
        simbolo, c = dados["perigo"]
        # o perigo "pisca" para parecer que esta borbulhando
        if (sala["quadro"] // 6 + x + y) % 5 == 0:
            simbolo = "°"
        return cor(simbolo, c)
    if celula == "P":
        if sala["porta_aberta"]:
            return cor("░", "92")
        return cor("█", "31")
    simbolo, c = dados["chao"]
    return cor(simbolo, c)


def desenhar_mapa(jogador, sala):
    linhas = []

    # Para nao procurar em listas a cada casa, monto "dicionarios de posicao"
    pos_inimigos = {}
    for inimigo in sala["inimigos"]:
        pos_inimigos[(inimigo["x"], inimigo["y"])] = inimigo

    pos_tiros = {}
    for tiro in sala["tiros"]:
        pos_tiros[(tiro["x"], tiro["y"])] = tiro

    pos_itens = {}
    for item in sala["itens"]:
        pos_itens[(item["x"], item["y"])] = item

    pos_efeitos = {}
    for efeito in sala["efeitos"]:
        pos_efeitos[(efeito["x"], efeito["y"])] = efeito

    # o jogador pisca quando acabou de levar dano
    mostrar_jogador = True
    if jogador["invencivel"] > 0 and jogador["sombra"] == 0:
        if sala["quadro"] % 4 < 2:
            mostrar_jogador = False

    for y in range(ALTURA):
        texto = ""
        for x in range(LARGURA):
            pos = (x, y)
            if pos in pos_efeitos:
                efeito = pos_efeitos[pos]
                texto += cor(efeito["simbolo"], efeito["cor"])
            elif pos == (jogador["x"], jogador["y"]) and mostrar_jogador:
                if jogador["sombra"] > 0:
                    texto += cor(jogador["simbolo"], "90")
                else:
                    texto += cor(jogador["simbolo"], jogador["cor"])
            elif pos in pos_inimigos:
                inimigo = pos_inimigos[pos]
                tipo = INIMIGOS[inimigo["tipo"]]
                if inimigo["piscando"] > 0:
                    texto += cor(tipo["simbolo"], "97;41")  # fundo vermelho = levou dano
                else:
                    texto += cor(tipo["simbolo"], tipo["cor"])
            elif pos in pos_tiros:
                tiro = pos_tiros[pos]
                if tiro["do_jogador"]:
                    simbolo = jogador["tiro"]
                    if simbolo == "direcional":
                        # a adaga aponta para onde esta indo
                        if tiro["dy"] == 0:
                            simbolo = "-"
                        else:
                            simbolo = "|"
                    texto += cor(simbolo, jogador["cor"])
                else:
                    texto += cor("•", "91")
            elif pos in pos_itens:
                item = pos_itens[pos]
                if item["tipo"] == "bau":
                    texto += cor("■", "93")
                else:
                    texto += cor("♥", "91")
            else:
                texto += desenhar_celula(sala, x, y)
        linhas.append("  " + texto)
    return linhas


# ------------------------------------------------------------
# HUD (as informacoes em cima e embaixo do mapa)
# ------------------------------------------------------------
def barra_de_vida(jogador):
    texto = ""
    for i in range(jogador["vida_max"]):
        if i < jogador["vida"]:
            texto += cor("♥", "91")
        else:
            texto += cor("♥", "90")
    return texto


def barra_de_energia(jogador):
    texto = ""
    for i in range(ENERGIA_MAXIMA):
        if i < jogador["energia"]:
            texto += cor("■", "96")
        else:
            texto += cor("·", "90")
    return texto


def barra_do_chefe(sala):
    for inimigo in sala["inimigos"]:
        if inimigo["tipo"] == "chefe":
            tamanho = 30
            cheio = int(tamanho * inimigo["vida"] / inimigo["vida_max"])
            barra = cor("█" * cheio, "91") + cor("░" * (tamanho - cheio), "90")
            return cor("  O REI SOMBRIO ", "91;1") + barra
    return None


def desenhar_jogo(jogador, sala):
    dados = sala["dados"]
    linhas = []

    titulo = "  Andar " + str(sala["numero"] + 1) + "/" + str(len(SALAS)) + " - " + dados["nome"]
    linhas.append(cor(titulo, "97;1") + "   " + cor(jogador["nome"] + " " + jogador["simbolo"], jogador["cor"]))

    poder = "[E] " + jogador["nome_poder"] + " (" + str(jogador["custo_poder"]) + ")"
    if jogador["energia"] >= jogador["custo_poder"]:
        poder = cor(poder, "96")
    else:
        poder = cor(poder, "90")
    linhas.append("  Vida " + barra_de_vida(jogador) + "   Energia " + barra_de_energia(jogador) + "  " + poder)

    chefe = barra_do_chefe(sala)
    if chefe:
        linhas.append(chefe)
    else:
        info = "  Dano " + str(jogador["dano"]) + "   Alcance " + str(jogador["alcance"])
        info += "   Inimigos: " + str(len(sala["inimigos"]))
        if sala["porta_aberta"]:
            info += cor("   Escada aberta! →", "92")
        linhas.append(cor(info, "37"))

    linhas.extend(desenhar_mapa(jogador, sala))

    if sala["tempo_mensagem"] > 0:
        linhas.append("  " + cor(sala["mensagem"], "93"))
    else:
        linhas.append("")
    linhas.append(cor("  WASD andar | Setas ou IJKL atirar | E poder | P pausa | Q sair", "90"))

    ir_para_o_topo()
    # \033[K apaga o resto da linha (para nao sobrar lixo do quadro anterior)
    print("\n".join(linha + "\033[K" for linha in linhas) + "\033[J", end="", flush=True)


# ------------------------------------------------------------
# MENUS E TELAS
# ------------------------------------------------------------
def tela_titulo():
    limpar()
    print()
    print(cor("    ╔══════════════════════════════════════════╗", "91"))
    print(cor("    ║                                          ║", "91"))
    print(cor("    ║", "91") + cor("                J  O  G  O                ", "97;1") + cor("║", "91"))
    print(cor("    ║", "91") + cor("      P Y T H O N   T E R M I N A L       ", "93;1") + cor("║", "91"))
    print(cor("    ║                                          ║", "91"))
    print(cor("    ╚══════════════════════════════════════════╝", "91"))
    print()
    print("        " + cor("█████████████████████", "90"))
    print("        " + cor("█", "90") + "  " + cor("¤", "93") + "      " + cor("x", "94") + "  " + cor("ж", "97") + "       " + cor("█", "90"))
    print("        " + cor("█", "90") + "    " + cor("♂", "94") + cor("x", "94") + "     " + cor("■", "93") + "     " + cor("░", "92"))
    print("        " + cor("█", "90") + "  " + cor("○", "97") + "      " + cor("Z", "32") + "       " + cor("█", "90"))
    print("        " + cor("█████████████████████", "90"))
    print()
    print("    Suba os 10 andares da Torre Amaldiçoada e derrote")
    print("    " + cor("O Rei Sombrio", "91") + " que governa lá do topo.")
    print()
    print(cor("    COMO JOGAR", "97;1"))
    print("    " + cor("W A S D", "96") + "       andar")
    print("    " + cor("Setas / IJKL", "96") + "  atacar")
    print("    " + cor("E", "96") + "             usar poder (gasta energia)")
    print("    " + cor("■", "93") + "             baú: aparece quando o andar é limpo")
    print("    " + cor("♥", "91") + "             coração: recupera vida")
    print("    Mate todos os inimigos para abrir a escada " + cor("░", "92"))
    print()
    print(cor("    Aperte ENTER para começar  (Q para sair)", "93"))


def tela_escolha_personagem():
    limpar()
    print()
    print(cor("    ESCOLHA SEU PERSONAGEM", "97;1"))
    print()
    for i in range(len(PERSONAGENS)):
        p = PERSONAGENS[i]
        print("    " + cor("[" + str(i + 1) + "]", "93") + " " + cor(p["simbolo"] + " " + p["nome"], p["cor"] + ";1"))
        print("        " + p["descricao"])
        print("        Vida " + cor("♥" * p["vida"], "91") +
              "   Dano " + cor("■" * p["dano"], "97") +
              "   Alcance " + cor("■" * (p["alcance"] // 2), "97") +
              "   Velocidade " + cor("■" * (10 - p["recarga"]), "97"))
        print("        Ataque: " + p["nome_tiro"])
        print("        Poder: " + cor(p["nome_poder"], "96") + " - " + p["descricao_poder"])
        print()
    print(cor("    Aperte 1, 2 ou 3", "93"))


def tela_transicao(numero):
    sala = SALAS[numero]
    limpar()
    print("\n" * 6)
    if numero == len(SALAS) - 1:
        print(cor("              !!! TOPO DA TORRE !!!", "91;1"))
    else:
        print(cor("                 Andar " + str(numero + 1) + " de " + str(len(SALAS)), "90"))
    print()
    print(cor("              ~ " + sala["nome"] + " ~", "97;1"))
    print()
    print("              " + cor(sala["descricao"], "37"))
    time.sleep(1.8)
    limpar()


def tela_pausa():
    print()
    print(cor("  ===  JOGO PAUSADO - aperte qualquer tecla para voltar  ===", "93;1"))


def tela_fim(jogador, venceu, numero_sala, tempo):
    limpar()
    print("\n" * 3)
    if venceu:
        print(cor("        ♦  VOCÊ VENCEU!  ♦", "93;1"))
        print()
        print("    O Rei Sombrio caiu e a torre está livre da maldição.")
    else:
        print(cor("        †  FIM DE JOGO  †", "91;1"))
        print()
        print("    Você caiu no andar " + str(numero_sala + 1) + " - " + SALAS[numero_sala]["nome"] + ".")
    print()
    print(cor("    ESTATÍSTICAS", "97;1"))
    print("    Personagem ........ " + cor(jogador["nome"] + " " + jogador["simbolo"], jogador["cor"]))
    print("    Inimigos derrotados " + str(jogador["abates"]))
    print("    Baús abertos ...... " + str(jogador["baus"]))
    print("    Tempo ............. " + str(int(tempo // 60)) + "min " + str(int(tempo % 60)) + "s")
    print()
    print(cor("    Jogar de novo? (S/N)", "93"))
