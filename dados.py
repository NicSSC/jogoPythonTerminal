# ============================================================
#  dados.py
#  Aqui ficam so os DADOS do jogo: personagens, inimigos,
#  salas e itens dos baus. Nenhuma logica fica aqui.
#  Para mudar o balanceamento do jogo, e so mexer neste arquivo.
# ============================================================

# Tamanho do mapa de cada sala (contando as paredes)
LARGURA = 41
ALTURA = 15

# Cores do terminal (codigos ANSI)
CINZA = "90"
VERMELHO = "91"
VERDE = "92"
AMARELO = "93"
AZUL = "94"
ROSA = "95"
CIANO = "96"
BRANCO = "97"
VERMELHO_ESCURO = "31"
VERDE_ESCURO = "32"
MARROM = "33"
AZUL_ESCURO = "34"
ROXO = "35"
CIANO_ESCURO = "36"


# ------------------------------------------------------------
# PERSONAGENS JOGAVEIS
# vida      -> quantos coracoes comeca
# dano      -> dano de cada lagrima
# alcance   -> quantas casas a lagrima anda
# recarga   -> quadros de espera entre um tiro e outro (menor = mais rapido)
# poder     -> poder especial (tecla E), gasta energia
# ------------------------------------------------------------
PERSONAGENS = [
    {
        "nome": "Cavaleiro",
        "simbolo": "♂",
        "cor": AZUL,
        "vida": 6,
        "dano": 2,
        "alcance": 5,
        "recarga": 8,
        "poder": "giro",
        "nome_poder": "Giro de Espada",
        "custo_poder": 3,
        "descricao": "Muita vida e dano alto, mas atira perto.",
        "descricao_poder": "Causa 4 de dano em todos os inimigos a ate 3 casas.",
    },
    {
        "nome": "Maga",
        "simbolo": "♀",
        "cor": ROSA,
        "vida": 4,
        "dano": 1,
        "alcance": 11,
        "recarga": 6,
        "poder": "tempestade",
        "nome_poder": "Tempestade Arcana",
        "custo_poder": 4,
        "descricao": "Pouca vida, mas atira bem longe.",
        "descricao_poder": "Causa 3 de dano em TODOS os inimigos da sala.",
    },
    {
        "nome": "Ladino",
        "simbolo": "☻",
        "cor": VERDE,
        "vida": 5,
        "dano": 1,
        "alcance": 8,
        "recarga": 4,
        "poder": "sombra",
        "nome_poder": "Manto de Sombra",
        "custo_poder": 3,
        "descricao": "Equilibrado e atira muito rapido.",
        "descricao_poder": "Fica invencivel por 4s e causa dano dobrado.",
    },
]

ENERGIA_MAXIMA = 6


# ------------------------------------------------------------
# INIMIGOS
# espera -> quantos quadros espera entre um passo e outro (menor = mais rapido)
# ia     -> jeito de se mover:
#           "aleatorio"  anda meio sem rumo, as vezes vem em voce
#           "perseguir"  vem direto em voce
#           "fantasma"   persegue e atravessa obstaculos
#           "atirador"   anda pouco e atira quando esta alinhado com voce
#           "chefe"      persegue, atira em varias direcoes e chama ajudantes
# ------------------------------------------------------------
INIMIGOS = {
    "mosca":    {"nome": "Mosca",    "simbolo": "¤", "cor": AMARELO, "vida": 1,  "dano": 1, "espera": 5,  "ia": "aleatorio"},
    "aranha":   {"nome": "Aranha",   "simbolo": "ж", "cor": BRANCO,  "vida": 2,  "dano": 1, "espera": 3,  "ia": "aleatorio"},
    "zumbi":    {"nome": "Zumbi",    "simbolo": "Z", "cor": VERDE_ESCURO, "vida": 4, "dano": 1, "espera": 8, "ia": "perseguir"},
    "fantasma": {"nome": "Fantasma", "simbolo": "&", "cor": CIANO,   "vida": 3,  "dano": 1, "espera": 7,  "ia": "fantasma"},
    "olho":     {"nome": "Olho",     "simbolo": "Θ", "cor": ROXO,    "vida": 3,  "dano": 1, "espera": 14, "ia": "atirador", "espera_tiro": 30},
    "golem":    {"nome": "Golem",    "simbolo": "G", "cor": MARROM,  "vida": 8,  "dano": 2, "espera": 10, "ia": "perseguir"},
    "chefe":    {"nome": "O Devorador", "simbolo": "Ω", "cor": VERMELHO, "vida": 60, "dano": 2, "espera": 6, "ia": "chefe", "espera_tiro": 28},
}


# ------------------------------------------------------------
# SALAS (sao 10, uma depois da outra)
# parede / chao / obstaculo / perigo -> (caractere, cor)
# perigo   -> chao que machuca quando voce pisa (None = sala sem perigo)
# layout   -> formato fixo da sala: livre, pilares, cantos, rio, lagoas, corredor
# obstaculos -> quantos obstaculos ALEATORIOS a mais aparecem
# ------------------------------------------------------------
SALAS = [
    {
        "nome": "Porão Úmido",
        "descricao": "Cheira a mofo... algo zumbe no escuro.",
        "parede": ("█", CINZA), "chao": (" ", CINZA),
        "obstaculo": ("○", BRANCO), "perigo": None,
        "layout": "livre", "obstaculos": 6,
        "inimigos": ["mosca", "mosca", "mosca"],
    },
    {
        "nome": "Esgoto",
        "descricao": "Cuidado com a água tóxica!",
        "parede": ("▓", VERDE_ESCURO), "chao": (".", CINZA),
        "obstaculo": ("▒", VERDE_ESCURO), "perigo": ("≈", VERDE),
        "layout": "lagoas", "obstaculos": 5,
        "inimigos": ["mosca", "mosca", "aranha", "aranha"],
    },
    {
        "nome": "Caverna dos Ecos",
        "descricao": "Patinhas correm pelas pedras...",
        "parede": ("█", MARROM), "chao": (",", CINZA),
        "obstaculo": ("▲", MARROM), "perigo": None,
        "layout": "cantos", "obstaculos": 8,
        "inimigos": ["aranha", "aranha", "aranha", "zumbi"],
    },
    {
        "nome": "Floresta Sombria",
        "descricao": "As árvores parecem te observar.",
        "parede": ("♣", VERDE_ESCURO), "chao": ("'", VERDE_ESCURO),
        "obstaculo": ("♠", VERDE), "perigo": None,
        "layout": "livre", "obstaculos": 14,
        "inimigos": ["zumbi", "zumbi", "mosca", "mosca", "mosca"],
    },
    {
        "nome": "Cripta Antiga",
        "descricao": "Os mortos não descansam aqui.",
        "parede": ("█", ROXO), "chao": (" ", CINZA),
        "obstaculo": ("†", BRANCO), "perigo": None,
        "layout": "pilares", "obstaculos": 4,
        "inimigos": ["fantasma", "fantasma", "fantasma", "zumbi"],
    },
    {
        "nome": "Lago Congelado",
        "descricao": "A água gelada queima a pele.",
        "parede": ("▓", CIANO_ESCURO), "chao": (".", AZUL_ESCURO),
        "obstaculo": ("♦", CIANO), "perigo": ("≈", AZUL),
        "layout": "rio", "obstaculos": 5,
        "inimigos": ["olho", "olho", "aranha", "aranha"],
    },
    {
        "nome": "Biblioteca Esquecida",
        "descricao": "Olhos brilham entre as estantes.",
        "parede": ("█", MARROM), "chao": (" ", CINZA),
        "obstaculo": ("≡", AMARELO), "perigo": None,
        "layout": "corredor", "obstaculos": 4,
        "inimigos": ["olho", "olho", "fantasma", "fantasma", "mosca"],
    },
    {
        "nome": "Forja de Lava",
        "descricao": "O calor é insuportável. Não pise na lava!",
        "parede": ("▓", VERMELHO_ESCURO), "chao": (".", VERMELHO_ESCURO),
        "obstaculo": ("█", CINZA), "perigo": ("~", VERMELHO),
        "layout": "lagoas", "obstaculos": 5,
        "inimigos": ["golem", "golem", "mosca", "mosca", "olho"],
    },
    {
        "nome": "Catedral Profana",
        "descricao": "Um silêncio pesado... antes da tempestade.",
        "parede": ("█", BRANCO), "chao": ("·", CINZA),
        "obstaculo": ("‡", BRANCO), "perigo": None,
        "layout": "pilares", "obstaculos": 3,
        "inimigos": ["golem", "olho", "olho", "fantasma", "fantasma", "zumbi"],
    },
    {
        "nome": "Covil do Devorador",
        "descricao": "Ele está com fome. MUITA fome.",
        "parede": ("█", VERMELHO), "chao": (" ", CINZA),
        "obstaculo": ("○", CINZA), "perigo": ("~", VERMELHO),
        "layout": "cantos", "obstaculos": 3,
        "inimigos": ["chefe"],
    },
]


# ------------------------------------------------------------
# O QUE PODE SAIR DOS BAUS
# ------------------------------------------------------------
CONTEUDO_BAUS = [
    {"nome": "Poção Vermelha",     "efeito": "cura",     "texto": "+2 de vida"},
    {"nome": "Coração Dourado",    "efeito": "vida_max", "texto": "+1 coração máximo"},
    {"nome": "Pedra de Afiar",     "efeito": "dano",     "texto": "+1 de dano"},
    {"nome": "Luneta",             "efeito": "alcance",  "texto": "+2 de alcance"},
    {"nome": "Luva Ligeira",       "efeito": "recarga",  "texto": "atira mais rápido"},
    {"nome": "Cristal de Energia", "efeito": "energia",  "texto": "energia cheia"},
]

VIDA_MAXIMA_LIMITE = 12
