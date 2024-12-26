"""
**********************************************************************************************************
 * Script: Support Heal (Uso de Bandagens com Re-Equip)
 * Versao: 1.0
 * Data: 2024-12-21
 *
 * Descricao:
 * - Antes de iniciar, verifica se o jogador esta vivo.
 * - Monitora constantemente o HP do jogador.
 * - Se a diferenca entre HP maximo e HP atual for >= HP_MARGIN (ex: 70), usa bandagem em si mesmo.
 * - Ao usar bandagem, remove arma/escudo das maos e depois re-equipa se estiver na mochila.
 * - Para quando acabarem as bandagens na mochila.
 *
 * Funcoes Auxiliares:
 * 1) is_alive() -> bool
 * 2) count_bandages() -> int
 * 3) remove_hands_items()
 * 4) re_equip_items()
 * 5) use_bandage_on_self()
 * 6) check_and_heal()
 * 7) main()
 **********************************************************************************************************
"""

from py_stealth import *
from time import sleep

# =============================================
# CONFIGURACOES
# =============================================

HP_MARGIN = 70      # Se HP estiver 70 ou mais abaixo do maximo, usa bandagem
BANDAGE_ID = 0x0E21 # ID fixo da bandagem (classico no UO)

# Lista de itens que o jogador usara nas maos.
# Cada tupla contem: (id do item, layer de equip)
# Layers possiveis: "LeftHand", "RightHand", ...
# Ajuste IDs e layers conforme necessario
ITEMS_TO_EQUIP = [
    {"Kryss": "MinhaEspada",  "id": 0x1400, "layer": "RightHand"},
    {"Heater Shield": "MeuEscudo",    "id": 0x1B76, "layer": "LeftHand"}
]

# Tempo de espera adicional (ms) para simulacao ou sincronizacao, ajuste conforme necessario
WAIT_AFTER_USE = 600


# =============================================
# FUNCOES AUXILIARES
# =============================================

def is_alive() -> bool:
    """Retorna True se o personagem estiver vivo, False se estiver morto."""
    return not Dead()

def count_bandages() -> int:
    """Conta quantas bandagens existem na mochila."""
    total = 0
    if FindType(BANDAGE_ID, Backpack()):
        for bandage in GetFindedList():
            total += GetQuantity(bandage)
    return total

def remove_hands_items():
    """
    Remove itens das maos do jogador (arma/escudo).
    Move cada item encontrado na mao para a mochila.
    """
    for layer in [RhandLayer(), LhandLayer()]:
        item_in_hand = ObjAtLayer(layer)
        if item_in_hand > 0:
            # Move o item para a mochila
            AddToSystemJournal(f"Removendo item da layer {layer}: {hex(item_in_hand)}")
            MoveItem(item_in_hand, GetQuantity(item_in_hand), Backpack(), 0, 0, 0)
            Wait(WAIT_AFTER_USE)

def re_equip_items():
    """
    Re-equipa os itens definidos em ITEMS_TO_EQUIP,
    caso nao estejam equipados e estejam na mochila.
    """
    for equip_info in ITEMS_TO_EQUIP:
        item_id = equip_info["id"]
        desired_layer = equip_info["layer"]
        # Checa se ja tem algum item equipado na layer
        if desired_layer == "RightHand":
            layer_code = RhandLayer()
        elif desired_layer == "LeftHand":
            layer_code = LhandLayer()
        else:
            # Ajustar se voce usar outro layer (ex: WINGS, SHOES, HEAD, etc.)
            # Camadas personalizadas podem precisar de outro approach
            continue

        # Verifica se a layer esta vazia
        if ObjAtLayer(layer_code) == 0:
            # Tenta encontrar o item na mochila
            if FindType(item_id, Backpack()):
                item_found = FindItem()
                AddToSystemJournal(f"Equipando {equip_info['name']} (ID: {hex(item_id)}) na {desired_layer}.")
                Equip(layer_code, item_found)
                Wait(WAIT_AFTER_USE)
            else:
                AddToSystemJournal(f"Nao encontrei {equip_info['name']} (ID: {hex(item_id)}) na mochila para equipar.")
        else:
            # Ja tem algo equipado nessa layer
            pass

def use_bandage_on_self():
    """
    Usa uma bandagem no proprio jogador:
    1) Verifica se ha bandagem na mochila
    2) Remove arma/escudo das maos
    3) Usa a bandagem
    4) Re-equipa arma e escudo
    """
    # Verifica se tem bandagem
    if count_bandages() <= 0:
        AddToSystemJournal("Sem bandagens na mochila, nao foi possivel curar.")
        return

    # Remove itens das maos
    remove_hands_items()

    # Acha uma bandagem na mochila
    if FindType(BANDAGE_ID, Backpack()):
        bandage_id = FindItem()
        AddToSystemJournal("Usando bandagem em si mesmo...")
        UseObject(bandage_id)
        WaitTargetSelf()
        Wait(WAIT_AFTER_USE)  # Ajuste se necessario
    else:
        AddToSystemJournal("Nao encontrei nenhuma bandagem ao tentar usar.")
        return

    # Re-equipa itens
    re_equip_items()

def check_and_heal():
    """
    Verifica se o HP do jogador esta 70 abaixo do maximo.
    Se sim, usa bandagem. Caso nao tenha bandagem, script encerrara.
    """
    current_hp = HP()
    max_hp = MaxHP()
    if (max_hp - current_hp) >= HP_MARGIN:
        # Tenta curar
        if count_bandages() > 0:
            use_bandage_on_self()
        else:
            AddToSystemJournal("Acabaram as bandagens! Encerrando script.")
            # Pode encerrar script ou ficar em loop
            exit(0)

# =============================================
# FUNCAO PRINCIPAL
# =============================================

def main():
    AddToSystemJournal("Iniciando script de suporte de cura.")

    # Primeiro, verifica se o jogador esta vivo
    if not is_alive():
        AddToSystemJournal("Jogador esta morto. Encerrando script.")
        return  # ou exit(0)

    while True:
        # Se ainda existir bandagem, verifica se precisa curar
        if count_bandages() <= 0:
            AddToSystemJournal("Sem bandagens na mochila. Parando script.")
            break

        check_and_heal()

        # Aguarda um pouco antes de verificar novamente, para nao spammar
        Wait(500)


if __name__ == "__main__":
    main()
