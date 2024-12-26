"""
Script: Deposit Gold in Bank
Author: Azarras [Zehan]
Version: 1.1
Date: 2024-12-15
Description:
- The script organizes gold in the player's backpack into stacks of up to 60,000 before transferring to the bank.
- Uses the configured bank coordinates.
- Continuously checks for gold in the backpack and deposits it in the bank.
- Stops when no more gold is found in the backpack.
"""

from py_stealth import *

# Configurações
BANK_COORDINATES = (2513, 551)
GOLD_TYPE = 0x0EED
MAX_GOLD_STACK = 60000  # Limite de pilha de ouro no UO


def move_to_coordinates(x, y):
    """
    Move o jogador para as coordenadas especificadas.
    """
    NewMoveXY(x, y, True, 1, True)


def organize_gold_in_backpack():
    """
    Organiza o ouro na mochila, juntando os montes até o limite de 60.000 por pilha.
    """
    gold_stacks = FindType(GOLD_TYPE, Backpack())  # Localiza todas as pilhas de ouro na mochila
    if gold_stacks > 1:  # Verifica se há mais de uma pilha
        gold_ids = GetFindedList()  # Lista de IDs de pilhas de ouro
        main_stack = gold_ids[0]  # Primeira pilha como principal

        for gold_id in gold_ids[1:]:
            if GetQuantity(main_stack) < MAX_GOLD_STACK:
                # Calcula quanto ouro pode ser movido para a pilha principal
                space_left = MAX_GOLD_STACK - GetQuantity(main_stack)
                gold_to_move = min(GetQuantity(gold_id), space_left)

                MoveItem(gold_id, gold_to_move, Backpack(), 0, 0, 0)
                Wait(300)
                if GetQuantity(main_stack) == MAX_GOLD_STACK:
                    break  # Sai do loop se a pilha principal estiver cheia

                # Atualiza a lista de pilhas de ouro
                gold_stacks = FindType(GOLD_TYPE, Backpack())
                gold_ids = GetFindedList()
                main_stack = gold_ids[0]


def deposit_gold():
    """
    Move pilhas de ouro da mochila para o banco.
    """
    while FindType(GOLD_TYPE, Backpack()) > 0:
        gold_id = FindItem()  # Obtém o ID da pilha de ouro
        MoveItem(gold_id, GetQuantity(gold_id), ObjAtLayer(BankLayer()), 0, 0, 0)
        Wait(300)  # Aguarda para não sobrecarregar o servidor


def main():
    AddToSystemJournal("Script de Depósito de Ouro Iniciado.")

    while True:
        if FindType(GOLD_TYPE, Backpack()) > 0:
            organize_gold_in_backpack()  # Organiza ouro na mochila
            move_to_coordinates(*BANK_COORDINATES)  # Move para o banco
            UOSay("banker bank guard")  # Chama o bancário
            Wait(1000)
            deposit_gold()  # Deposita ouro no banco
        else:
            AddToSystemJournal("Sem ouro na mochila. Script finalizado.")
            break


if __name__ == "__main__":
    main()
