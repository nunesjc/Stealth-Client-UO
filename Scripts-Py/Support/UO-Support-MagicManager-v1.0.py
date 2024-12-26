"""
**********************************************************************************************************
 * Script: Support Magic Manager
 * Versao: 1.0
 * Data: 2024-12-21
 *
 * Descricao:
 * Gera magias de suporte periodicamente (Reactive Armor, Protection, Magic Reflection, Bless)
 * Cada uma tem um tempo de duracao (em segundos). O script:
 *  1) Monitora se a duracao expirou e recasta a magia.
 *  2) Verifica se ha mana suficiente para lancar (>= 90% do maximo).
 *  3) Se a mana estiver baixa, inicia meditação. Caso apos 3 minutos nao atinja o maximo,
 *     tenta usar uma pocao de mana (ID e color definidos). Se nao houver, segue meditando.
 *  4) Funciona em loop, recastando cada magia conforme o tempo de duracao.
 *
 * Configuracoes principais:
 *  - SUPPORT_SPELLS: lista de magias, cada uma com:
 *      name, spell_id, duration (segundos), mana_cost, last_cast (registrado em runtime)
 *  - MANA_THRESHOLD: fracao de mana maxima em que podemos lancar a magia (ex: 0.90 -> 90%)
 *  - MEDITATION_START: mana minima para comecar a meditar (ex: 30)
 *  - MANA_POTION_TYPE, MANA_POTION_COLOR: definicoes da pocao de mana
 *  - WAIT_MAX_MANA: tempo (em segundos) aguardando meditacao para tentar max mana antes de usar pocao
 **********************************************************************************************************
"""

from py_stealth import *
from datetime import datetime

# --------------------------------------------------------------------------
# CONFIGURACOES
# --------------------------------------------------------------------------

# Lista de magias de suporte com duracao em segundos:
# Ajuste os spell_id e mana_cost conforme seu shard.
SUPPORT_SPELLS = [
    {
        "name": "Reactive Armor",
        "spell_id": 1,  # ID de exemplo
        "duration": 5 * 60,  # 5 minutos
        "mana_cost": 11,  # valor de exemplo
        "last_cast": 0  # vai armazenar o horario do ultimo cast
    },
    {
        "name": "Protection",
        "spell_id": 5,
        "duration": 5 * 60,  # 5 minutos
        "mana_cost": 11,
        "last_cast": 0
    },
    {
        "name": "Magic Reflection",
        "spell_id": 25,
        "duration": 8 * 60,  # 8 minutos
        "mana_cost": 14,
        "last_cast": 0
    },
    {
        "name": "Bless",
        "spell_id": 11,
        "duration": 3 * 60,  # 3 minutos
        "mana_cost": 9,
        "last_cast": 0
    }
]

MANA_THRESHOLD = 0.90  # Precisamos de pelo menos 90% da mana maxima para lancar a magia
MEDITATION_START = 30  # Se a mana estiver abaixo de 30, inicia meditacao
WAIT_MAX_MANA = 180  # Tempo (segundos) aguardando meditacao antes de tentar usar pocao
MANA_POTION_TYPE = 0x0F09  # Type da pocao de mana
MANA_POTION_COLOR = 0x0388  # Cor da pocao de mana

# Tempo de espera entre verificacoes do loop principal (em ms)
MAIN_LOOP_DELAY = 1000


# --------------------------------------------------------------------------
# FUNCOES AUXILIARES
# --------------------------------------------------------------------------

def is_alive() -> bool:
    """Retorna True se o personagem esta vivo."""
    return not Dead()


def current_mana() -> int:
    """Retorna a mana atual do jogador."""
    return Mana()


def max_mana() -> int:
    """Retorna a mana maxima do jogador."""
    return MaxMana()


def need_mana_for_spell(spell: dict) -> bool:
    """
    Verifica se temos mana suficiente para lancar esta magia,
    considerando a fracao MANA_THRESHOLD do max_mana e o custo da magia.
    """
    mana_atual = current_mana()
    mana_max = max_mana()
    # Precisamos que a mana atual seja >= do maior entre
    #   - custo de mana do spell
    #   - MANA_THRESHOLD * mana maxima
    required_mana = max(spell["mana_cost"], MANA_THRESHOLD * mana_max)
    return (mana_atual >= required_mana)


def cast_support_spell(spell: dict):
    """
    Lanca a magia de suporte.
    Exemplo com CastSpell(spell_id), WaitTargetSelf() se necessario.
    Armazena o horario (em segundos) em spell["last_cast"].
    """
    AddToSystemJournal(f"Lancando magia: {spell['name']}")
    CastSpell(spell["spell_id"])

    # Se for magia de alvo no proprio jogador (ex: self buffs):
    WaitTargetSelf()

    # Espera um pouco para garantir que a magia foi aplicada
    Wait(1000)

    # Registra o horario do cast
    spell["last_cast"] = datetime.now().timestamp()


def is_spell_expired(spell: dict) -> bool:
    """
    Verifica se ja passou o tempo de duracao desde o last_cast.
    Se last_cast == 0, significa que ainda nao foi castado e precisa.
    """
    current_time = datetime.now().timestamp()
    if spell["last_cast"] == 0:
        return True
    elapsed = current_time - spell["last_cast"]
    return (elapsed >= spell["duration"])


def count_mana_potions() -> int:
    """
    Conta quantas potes de mana (type + color) temos na mochila.
    """
    total = 0
    if FindTypeEx(MANA_POTION_TYPE, MANA_POTION_COLOR, Backpack(), False):
        for pot in GetFindedList():
            total += GetQuantity(pot)
    return total


def use_mana_potion():
    """
    Usa uma pocao de mana, se existir na mochila.
    """
    if FindTypeEx(MANA_POTION_TYPE, MANA_POTION_COLOR, Backpack(), False):
        pot_id = FindItem()
        AddToSystemJournal("Usando pocao de mana...")
        UseObject(pot_id)
        Wait(1500)  # Tempo para beber a pocao
    else:
        AddToSystemJournal("Nao ha potes de mana na mochila.")


def do_meditation():
    """
    Tenta usar a skill Meditation, se estiver abaixo de MEDITATION_START mana.
    Mesmo acima disso pode meditar, se precisar mais mana.
    Ajuste se necessario.
    """
    if current_mana() < MEDITATION_START:
        AddToSystemJournal("Mana baixa. Iniciando meditacao...")
        UseSkill("Meditation")
        Wait(2000)  # Tempo inicial para entrar em meditacao


def ensure_mana_to_cast(spell: dict):
    """
    Garante que haja mana suficiente para lancar a magia.
    Regra:
      - Precisamos de 'spell["mana_cost"]' e idealmente >= (MANA_THRESHOLD * max_mana).
      - Se nao tivermos, meditamos.
      - Aguardamos ate 3 minutos (WAIT_MAX_MANA). Se nao atingirmos, usamos pocao (se houver).
      - Caso nao haja pocao, continuamos meditando ate conseguir 90% (ou custo do spell).
    """
    start_time = datetime.now().timestamp()
    while not need_mana_for_spell(spell):
        do_meditation()
        Wait(2000)

        # Checa se ja passou WAIT_MAX_MANA segundos meditando
        if (datetime.now().timestamp() - start_time) >= WAIT_MAX_MANA:
            # Tenta usar pocao
            if count_mana_potions() > 0:
                use_mana_potion()
            else:
                AddToSystemJournal("Sem pocao de mana. Continuando a meditar...")
            # Reseta tempo para esperar novamente
            start_time = datetime.now().timestamp()

        # Se ja temos mana necessaria, sai
        if need_mana_for_spell(spell):
            break


# --------------------------------------------------------------------------
# FUNCAO PRINCIPAL
# --------------------------------------------------------------------------

def main():
    AddToSystemJournal("Iniciando script de magias de suporte.")

    # Verifica se jogador esta vivo
    if not is_alive():
        AddToSystemJournal("O jogador esta morto. Encerrando script.")
        return

    while True:
        # Loop infinito monitorando as magias
        for spell in SUPPORT_SPELLS:
            if is_spell_expired(spell):
                # Precisamos recastar a magia
                AddToSystemJournal(f"Magia expirada ou nao usada: {spell['name']}. Precisamos recastar.")

                # Garante mana
                ensure_mana_to_cast(spell)

                # Recast
                cast_support_spell(spell)

        # Espera antes de verificar novamente
        Wait(MAIN_LOOP_DELAY)


if __name__ == "__main__":
    main()
