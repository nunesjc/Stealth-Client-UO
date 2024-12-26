"""
**********************************************************************************************************
 * Script: Magic Reagent Seed Planter
 * Versao: 1.2
 * Autor: SeuNome [Zehan]
 * Data: 2024-12-21
 *
 * Descricao:
 * Script modular em Python para plantar sementes de reagentes magicos com prioridade.
 * Agora ativamos a opcao de abrir portas automaticamente ao se mover.
 *
 * Fluxo:
 * 1) Verifica se ha pa na mochila; se nao, pega no banco.
 * 2) Para cada tipo de semente em SEEDS_TO_PLANT (ordem de prioridade):
 *    - Garante que tem MIN_SEEDS desse tipo na mochila.
 *    - Ativa a opcao de abrir portas automaticamente: SetMoveOpenDoor(1).
 *    - Move ate a fazenda (FARM_COORDS).
 *    - Planta as sementes em todos os tiles GROUND_TYPE encontrados.
 *    - Se acabar as sementes, volta ao banco para pegar mais do mesmo tipo.
 *    - Quando termina um tipo, passa ao proximo.
 * 3) Ao concluir todas as sementes, finaliza.
 *
 **********************************************************************************************************
"""

from py_stealth import *
from time import sleep

# =============================================================================
# ========================= CONFIGURACOES GERAIS ==============================
# =============================================================================

BANK_COORDS = (3429, 649)
FARM_COORDS = (3413, 662)  # Ajuste conforme a sua fazenda
GROUND_TYPE = 0x31F7
SHOVEL_TYPE = 0x0F39
FARM_RADIUS = 5
MIN_SEEDS = 100

# Lista de sementes em ordem de prioridade: a primeira tem maior prioridade
SEEDS_TO_PLANT = [
    {"name": "SementeNox",     "type": 0x0F7F, "color": 0x00AD},
    {"name": "SementeDragon",  "type": 0x0F7F, "color": 0x00EE},
    {"name": "SementeDaemon",  "type": 0x0F7F, "color": 0x01A2},
]

# =============================================================================
# ========================== FUNCOES AUXILIARES ===============================
# =============================================================================

def safe_move(x, y):
    """ Move-se ate as coordenadas (x,y) de forma segura. """
    NewMoveXY(x, y, True, 1, True)

def open_bank():
    """ Move-se ate o banco e tenta abrir. """
    safe_move(*BANK_COORDS)
    UOSay("bank banker")
    Wait(1500)

def ensure_shovel_in_backpack():
    """
    Verifica se ha uma pa na mochila; se nao, pega no banco.
    """
    if FindType(SHOVEL_TYPE, Backpack()) == 0:
        # Nao encontrou a pa, entao pega no banco
        open_bank()
        if FindType(SHOVEL_TYPE, ObjAtLayer(BankLayer())) > 0:
            shovel = FindItem()
            MoveItem(shovel, 1, Backpack(), 0, 0, 0)
            Wait(600)
        else:
            AddToSystemJournal("Nao encontrei nenhuma pa no banco. Encerrando processo.")
            # Aqui voce pode encerrar o script ou esperar.

def count_seeds_in_backpack(seed_type, seed_color):
    """ Conta quantas sementes do tipo/cor existem na mochila. """
    total = 0
    if FindTypeEx(seed_type, seed_color, Backpack(), False) > 0:
        for seed in GetFindedList():
            total += GetQuantity(seed)
    return total

def get_seeds_from_bank(seed_type, seed_color, needed_qty):
    """
    Abre o banco e tenta mover 'needed_qty' de sementes do type+color desejado
    para a mochila.
    """
    open_bank()
    bank_container = ObjAtLayer(BankLayer())
    if bank_container == 0:
        AddToSystemJournal("Falha ao abrir o banco para pegar sementes.")
        return

    while needed_qty > 0:
        if FindTypeEx(seed_type, seed_color, bank_container, False) > 0:
            seed_stack = FindItem()
            available = GetQuantity(seed_stack)
            to_move = min(available, needed_qty)
            MoveItem(seed_stack, to_move, Backpack(), 0, 0, 0)
            Wait(600)
            needed_qty -= to_move
        else:
            AddToSystemJournal("Nao ha mais sementes deste tipo no banco.")
            break

def ensure_seeds_in_backpack(seed_type, seed_color):
    """
    Garante que ha pelo menos MIN_SEEDS sementes do tipo/cor na mochila.
    Se nao tiver, puxa do banco.
    """
    current_qty = count_seeds_in_backpack(seed_type, seed_color)
    if current_qty < MIN_SEEDS:
        needed = MIN_SEEDS - current_qty
        AddToSystemJournal(f"Buscando {needed} sementes do tipo 0x{seed_type:X}, cor 0x{seed_color:X} no banco.")
        get_seeds_from_bank(seed_type, seed_color, needed)

def plant_seed_on_tile(seed_id, tile_id):
    """
    Planta a semente no tile. Ajuste conforme a dinamica do seu shard.
    """
    UseObject(seed_id)
    WaitTargetObject(tile_id)
    Wait(600)

def plant_seeds_in_area(seed_type, seed_color, radius=FARM_RADIUS):
    """
    Planta sementes em todos os tiles GROUND_TYPE no raio especificado.
    Se acabar as sementes, retorna False.
    Caso conclua sem acabar as sementes, retorna True.
    """
    SetFindDistance(radius)
    SetFindVertical(radius)

    if FindType(GROUND_TYPE, Ground()):
        ground_tiles = GetFindedList()
        AddToSystemJournal(f"Foram encontrados {len(ground_tiles)} tiles de chao para plantar.")
        for tile_id in ground_tiles:
            # Verifica se ainda temos sementes
            if count_seeds_in_backpack(seed_type, seed_color) <= 0:
                AddToSystemJournal("Sementes acabaram durante o plantio. Retornando ao banco.")
                return False

            if FindTypeEx(seed_type, seed_color, Backpack(), False) > 0:
                seed_id = FindItem()
                plant_seed_on_tile(seed_id, tile_id)
            else:
                AddToSystemJournal("Nao encontrei a semente na mochila, voltando ao banco.")
                return False
    else:
        AddToSystemJournal("Nenhum tile de chao encontrado nesta area.")

    return True

# =============================================================================
# =========================== FLUXO PRINCIPAL =================================
# =============================================================================

def main():
    AddToSystemJournal("Iniciando script de plantio de sementes...")

    # Verifica se ha pa
    ensure_shovel_in_backpack()

    # Percorre cada tipo de semente na ordem da lista (prioridade)
    for seed_data in SEEDS_TO_PLANT:
        seed_type = seed_data["type"]
        seed_color = seed_data["color"]
        seed_name = seed_data["name"]

        AddToSystemJournal(f"Iniciando processo com a semente: {seed_name} (type=0x{seed_type:X}, color=0x{seed_color:X})")

        # Garante que temos ao menos MIN_SEEDS desse tipo
        ensure_seeds_in_backpack(seed_type, seed_color)

        # Ativa abertura automatica de portas ao se mover
        SetMoveOpenDoor(1)

        # Vai ate a fazenda antes de iniciar a busca pelo chao
        safe_move(*FARM_COORDS)
        AddToSystemJournal("Chegamos na fazenda, iniciando o plantio.")

        # Tenta plantar, se acabar as sementes volta ao banco e tenta de novo
        while True:
            # Se nao tiver nenhuma semente, tenta pegar mais
            if count_seeds_in_backpack(seed_type, seed_color) < 1:
                AddToSystemJournal("Nao ha sementes na mochila, voltando ao banco para pegar mais.")
                ensure_seeds_in_backpack(seed_type, seed_color)
                safe_move(*FARM_COORDS)

            # Planta
            result = plant_seeds_in_area(seed_type, seed_color, FARM_RADIUS)
            if result:
                # Terminou sem problemas
                AddToSystemJournal(f"Finalizado plantio do tipo {seed_name} nesta area.")
                break
            else:
                # Acabaram as sementes durante o plantio, volta ao banco pegar mais
                ensure_seeds_in_backpack(seed_type, seed_color)
                safe_move(*FARM_COORDS)

    AddToSystemJournal("Plantio concluido de todas as sementes configuradas.")
    # Aqui pode aguardar proxima acao ou encerrar


if __name__ == "__main__":
    main()
