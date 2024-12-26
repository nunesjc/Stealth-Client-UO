"""
**********************************************************************************************************
 * Script: Organizador de Mochila
 * Versão: 1.5
 * Autor: Azarras [Zehan]
 * Data: 2024-12-15
 *
 * Descrição:
 * Organiza pilhas de itens na mochila do jogador, juntando itens configurados por ID.
 * Suporta empilhamento para reagentes, poções e ouro, respeitando limites de empilhamento do jogo.
 * Ajustado para verificar a mochila a cada 1 minuto, mesmo que não haja itens a organizar.
 *
 * Controle de Revisão:
 * --------------------------------------------------------------------------------------------------------
 * Versão |   Data    |                  Alterações                     |      Autor
 * --------------------------------------------------------------------------------------------------------
 *  1.0   | 2024-12-15| Criação inicial do script.                      | Azarras [Zehan]
 *  1.1   | 2024-12-15| Revisão da lógica de movimentação.              | Azarras [Zehan]
 *  1.2   | 2024-12-15| Adicionado suporte a múltiplos IDs.             | Azarras [Zehan]
 *  1.3   | 2024-12-15| Ajuste para alinhamento com script de depósito. | Azarras [Zehan]
 *  1.4   | 2024-12-15| Adicionada pausa de 5 minutos após organizar.   | Azarras [Zehan]
 *  1.5   | 2024-12-15| Intervalo reduzido para 1 minuto, loop infinito.| Azarras [Zehan]
 **********************************************************************************************************
"""

from py_stealth import *
from time import sleep

# Configuração de IDs e Limites
ITEM_IDS = [0x0EED, 0x0F0C, 0x0F09, 0x175D, 0x0F3F, 0x0F8C, 0x0F86, 0x0F7A, 0x0F8D, 0x0F88, 0x0F84,
            0x175D]  # IDs de itens a organizar: ouro, poções, etc.
MAX_STACK_SIZE = 60000  # Limite de empilhamento
PAUSE_DURATION = 30  # Intervalo de 1/2 minuto (em segundos)
MAX_ATTEMPTS = 5  # Limite de tentativas para mover itens


def organize_items_in_backpack():
    """
    Organiza os itens configurados na mochila, juntando pilhas dispersas.
    Retorna True se organizou algo, False se não houve organização.
    """
    organized = False
    for item_id in ITEM_IDS:  # Itera sobre cada tipo de item configurado
        while FindType(item_id, Backpack()) > 1:  # Enquanto houver mais de uma pilha
            item_ids = GetFindedList()  # Obtém lista de IDs das pilhas
            main_stack = item_ids[0]  # Define a primeira pilha como principal

            for item in item_ids[1:]:  # Itera pelas pilhas restantes
                if GetQuantity(main_stack) < MAX_STACK_SIZE:
                    space_left = MAX_STACK_SIZE - GetQuantity(main_stack)
                    amount_to_move = min(GetQuantity(item), space_left)

                    attempts = 0
                    while attempts < MAX_ATTEMPTS:
                        MoveItem(item, amount_to_move, main_stack, 0, 0, 0)  # Move os itens para a pilha principal
                        Wait(300)  # Espera para sincronização com o servidor
                        if GetQuantity(main_stack) >= space_left:  # Verifica se a movimentação foi bem-sucedida
                            organized = True
                            break
                        attempts += 1
                    else:
                        AddToSystemJournal(f"Falha ao mover item ID {item}. Tentativas esgotadas.")
                        continue

                    if GetQuantity(main_stack) == MAX_STACK_SIZE:
                        break  # Sai do loop se a pilha principal estiver cheia
                else:
                    break  # Sai do loop se a pilha principal estiver cheia
    return organized


if __name__ == "__main__":
    AddToSystemJournal("Iniciando script: Organizador de Mochila")

    try:
        while True:
            organized = organize_items_in_backpack()  # Organiza os itens na mochila
            if organized:
                AddToSystemJournal("Organização concluída. Próxima verificação em 1 minuto.")
            else:
                AddToSystemJournal("Nenhuma organização necessária no momento. Próxima verificação em 1 minuto.")

            sleep(PAUSE_DURATION)  # Pausa de 1/2 minuto antes da próxima execução
    except KeyboardInterrupt:
        AddToSystemJournal("Script interrompido pelo usuário.")
