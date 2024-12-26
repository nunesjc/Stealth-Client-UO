# UO-Looting-LootMore-v1.0.py

"""
UO-Looting-LootMore-v1.0.py

Automatiza o saque de itens específicos de corpos no chão em Ultima Online.

Autor: Azarras Zehan
Revisão: v1.0
Data: 27/04/2024
"""

import time
import logging
from py_stealth import *

# Configurações de Logging
logging.basicConfig(
    filename='UO-Looting-LootMore.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# IDs de Itens a Saquear
ITEM_IDS = [
    0x26B7, 0x0EED, 0x0FBF, 0x0FC0, 0x0FC1, 0x0FC3, 0x0FC4, 0x0FC5,
    0x0FC6, 0x0F09, 0x0F0E, 0x175D, 0x0F0C, 0x0F09, 0x3155, 0x0E75,
    0x1BFB, 0x0F3F, 0x1412, 0x1415, 0x13B9, 0x1414, 0x1413, 0x1411,
    0x1410, 0x1B76, 0x1B76, 0x1B76, 0x1F31
]

CORPSE_ID = 0x2006  # ID do Corpo no Chão
SEARCH_DISTANCE = 3  # Distância para buscar corpos


def initialize_looting():
    """
  Inicializa as configurações de saque.
  """
    SetFindDistance(SEARCH_DISTANCE)
    logging.info("Inicialização do Looting configurada com distância de busca de %d.", SEARCH_DISTANCE)


def find_corpse():
    """
  Procura por um corpo no chão.

  Retorna:
      int: ID do corpo encontrado ou 0 se não encontrado.
  """
    if FindType(CORPSE_ID, Ground()) > 0:
        corpse_id = FindItem()
        logging.info("Corpo encontrado! ID: %d", corpse_id)
        return corpse_id
    return 0


def open_corpse(corpse_id):
    """
  Interage com o corpo para abrir seu inventário.

  Args:
      corpse_id (int): ID do corpo a ser aberto.
  """
    UseObject(corpse_id)
    logging.info("Interagiu com o corpo ID: %d para abrir inventário.", corpse_id)
    time.sleep(0.2)  # Aguarda 200 milissegundos


def loot_items(corpse_id):
    """
  Varre os itens dentro do corpo e move os desejados para a mochila do jogador.

  Args:
      corpse_id (int): ID do corpo do qual saquear itens.
  """
    for item_id in ITEM_IDS:
        if FindType(item_id, corpse_id) > 0:
            item = FindItem()
            quantity = FindQuantity()
            logging.info("Item encontrado! ID: %d | Quantidade: %d | Saqueando...", item_id, quantity)
            MoveItem(item, quantity, Backpack(), 1, 1, 0)
            time.sleep(0.2)  # Aguarda 200 milissegundos


def ignore_corpse(corpse_id):
    """
  Ignora o corpo para não verificar novamente.

  Args:
      corpse_id (int): ID do corpo a ser ignorado.
  """
    Ignore(corpse_id)
    logging.info("Corpo ID: %d ignorado para evitar verificações futuras.", corpse_id)


def loot():
    """
  Função principal de saque que coordena todas as operações.
  """
    corpse_id = find_corpse()
    if corpse_id != 0:
        open_corpse(corpse_id)
        loot_items(corpse_id)
        ignore_corpse(corpse_id)
    else:
        logging.info("Nenhum corpo encontrado no momento.")


def main():
    """
  Loop principal que executa a função de saque indefinidamente.
  """
    logging.info("Iniciando UO-Looting-LootMore-v1.0.py")
    initialize_looting()

    while True:
        if Dead():
            logging.warning("O personagem está morto. Aguardando ressuscitação.")
            time.sleep(1)
            continue  # Pula para a próxima iteração do loop

        loot()
        time.sleep(0.2)  # Aguarda 200 milissegundos antes da próxima iteração


if __name__ == "__main__":
    main()
