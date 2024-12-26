"""
**********************************************************************************************************
 * Script: Auto Healing with Potion and Disconnect
 * Versão: 2.0
 * Autor: Azarras [Zehan]
 * Data: 2024-12-15
 *
 * Descrição:
 * - Monitora o HP do jogador e usa poções de cura automaticamente quando necessário.
 * - Emite alertas quando as poções restantes são iguais ou menores que o limite.
 * - Desconecta o jogador do jogo se a quantidade de poções for crítica (≤ 5).
 * - Espera o cooldown antes de usar outra poção.
 *
 * Controle de Revisão:
 * --------------------------------------------------------------------------------------------------------
 * Versão |   Data    |                  Alterações                     |      Autor
 * --------------------------------------------------------------------------------------------------------
 *  1.0   | 2024-12-15| Criação inicial do script em Python.            | Azarras [Zehan]
 *  1.1   | 2024-12-15| Adicionada desconexão ao atingir limite crítico.| Azarras [Zehan]
 *  2.0   | 2024-12-15| Código modularizado e documentação melhorada.   | Azarras [Zehan]
 **********************************************************************************************************
"""

from py_stealth import *
from time import sleep

# Configurações
POTION_TYPE = 0x0F0C  # ID da poção de cura
HP_THRESHOLD = 30     # HP perdido para iniciar a cura
MIN_POTIONS = 5       # Número crítico de poções para desconectar
CHECK_INTERVAL = 1    # Intervalo em segundos entre verificações
POTION_COOLDOWN = 5   # Cooldown para beber outra poção (em segundos)

def get_current_hp():
    """
    Retorna o HP atual do jogador.
    """
    return GetHP(Self())

def get_max_hp():
    """
    Retorna o HP máximo do jogador.
    """
    return GetMaxHP(Self())

def count_potions():
    """
    Retorna a quantidade de poções de cura no inventário.
    """
    return Count(POTION_TYPE)

def use_healing_potion():
    """
    Usa uma poção de cura no jogador.
    """
    WaitTargetObject(Self())  # Seleciona o próprio jogador como alvo
    UseType(POTION_TYPE, 0x0000)  # Usa a poção
    Wait(POTION_COOLDOWN * 1000)  # Aguarda o cooldown (em milissegundos)

def alert_low_potions():
    """
    Emite um alerta informando o número de poções restantes.
    """
    UOSay(f"Atenção: Apenas {count_potions()} poções restantes!")

def check_and_disconnect():
    """
    Verifica a quantidade de poções e desconecta o jogador se o número for crítico.
    """
    if count_potions() <= MIN_POTIONS:
        alert_low_potions()
        UOSay("Número crítico de poções! Desconectando do jogo...")
        Disconnect()
        exit()

def healing_loop():
    """
    Loop principal: monitora HP, usa poções e verifica a quantidade crítica.
    """
    AddToSystemJournal("Script de cura iniciado.")

    while True:
        current_hp = get_current_hp()
        max_hp = get_max_hp()

        # Se o HP estiver abaixo do limite configurado, usa poção
        if current_hp < (max_hp - HP_THRESHOLD):
            UOSay("HP baixo! Usando poção de cura...")
            use_healing_potion()

            # Verifica se a poção curou com sucesso
            new_hp = get_current_hp()
            if new_hp > current_hp:
                UOSay(f"Cura realizada com sucesso! HP Atual: {new_hp}")
            else:
                UOSay("A cura falhou ou foi interrompida!")

        # Verifica a quantidade de poções e desconecta se necessário
        check_and_disconnect()

        # Aguarda um pouco antes de repetir o loop
        sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    healing_loop()
