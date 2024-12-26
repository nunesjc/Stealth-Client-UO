from py_stealth import *
from datetime import *
import timeit

# ======================================================================================================================
# Check States
# ======================================================================================================================

# Nota: Configure Tink p/ Picareta ser o primerio item da lista rápida!
# Crie uma picareta antes de iniciar a Macro, assim ela será o primeiro item da Lista!
# Deixe no Bau da Casa (Madeira, Ferro e Tinker Tools), ele irá usar pra criar picaretas!
# Aproveite a Macro - Azarras Zehan


home_bau: int = 0x4003C209  # ID do Bau do chão você pega no Stealth em World (Ground)
movebank_x: int = 2357  # coordenada X do Banco
movebank_y: int = 867  # coordenada y do Banco

movemina_x: int = 2349  # coordenada x da Mina
movemina_y: int = 809  # coordenada y da Mina

moveress_x: int = 2357  # coordenada x de Reviver
moveress_y: int = 867  # coordenada y de Reviver

movesmelt_x: int = 2358  # coordenada x de Smelt
movesmelt_y: int = 867  # coordenada y de Smelt

numbertiles: int = 20  # Área total a ser explorada para miner


#
#
#

def bank():
    starttime = datetime.now()
    # while (InJournalBetweenTimes("stones in your Bank Box", starttime, datetime.now())) < 1:
    NewMoveXY(movebank_x, movebank_y, True, 1, True)  # Banco
    UOSay("Banker Bank Guard")
    CheckLag(10000)


def GoMina():
    NewMoveXY(movemina_x, movemina_y, True, 1, True)  # Ir para a mina
    CheckLag(10000)


def TypeQuantity(type, color, container):
    if FindTypeEx(type, color, container, True):
        return FindFullQuantity()
    return 0


def Hungry(food=0x103B):  # 0103B comida padrão "fish steaks", procurar na mochila
    while True:
        if Dead() or not Connected() or not CheckLag(15000):
            print("Hungry: You dead, or not connected or hard lags!")
            return False
        FindType(food, Backpack())
        if FindCount() <= 0:
            print("Hungry: not food!")
            return
        ct = datetime.now()
        UOSay(".hungry")
        if not WaitJournalLine(ct, 'stuffed', 5000):
            UseObject(FindItem())
            Wait(1500)
        else:
            return True


def ressurect():
    NewMoveXY(moveress_x, moveress_y, True, 1, True)  # Ank
    UOSay("Reviver")
    Wait(1500)
    UseFromGround(0x0005, 0xFFFF)


def smelt():
    while FindTypesArrayEx([0x19B9, 0x19B8, 0x19BA, 0x19B7], [0xFFFF], [Backpack()], False):
        NewMoveXY(movesmelt_x, movesmelt_y, True, 1, True)  # Forge
        UseObject(FindItem())
        Wait(500)


def unload():
    UseObject(home_bau)
    while FindTypesArrayEx([0x1BEF, 0x0F26, 0x1BDD, 0x1EBC, 0x1BE3, 0x1BF5, 0x1BE9, 0x19BA, 0x19B7, 0x19B8], [0xFFFF],
                           [Backpack()], False):
        item_to_move = FindItem()
        quantity_to_move = FindFullQuantity()
        MoveItem(item_to_move, quantity_to_move, home_bau, 0, 0, 0)
        Wait(500)


def make_tool():
    while Count(0x0E85) < 2:
        while Count(0x1EBC) < 1:  # pega tinker tool
            UseObject(home_bau)
            Wait(1500)
            if FindType(0x1EBC, home_bau):
                MoveItem(FindItem(), 1, Backpack(), 0, 0, 0)
                Wait(500)
            else:
                return

        while TypeQuantity(0x1BEF, 0x0000, Backpack()) < 4:  # pega iron ingots
            UseObject(home_bau)
            Wait(1500)
            if FindTypeEx(0x1BEF, 0x0000, home_bau, False):
                MoveItem(FindItem(), 20, Backpack(), 0, 0, 0)
                Wait(500)
            else:
                return

        while TypeQuantity(0x1BDD, 0x0000, Backpack()) < 4:  # pega log
            UseObject(home_bau)
            Wait(1500)
            if FindTypeEx(0x1BDD, 0x0000, home_bau, False):
                MoveItem(FindItem(), 10, Backpack(), 0, 0, 0)
                Wait(500)
            else:
                return

        starttime = datetime.now()
        UseType2(0x1EBC)
        Wait(2000)
        NumGumpButton(GetGumpsCount() - 1, 406)
        Wait(2000)
        NumGumpButton(GetGumpsCount() - 1, 601)
        Wait(3000)
        if IsGumpCanBeClosed(GetGumpsCount() - 1):
            CloseSimpleGump(GetGumpsCount() - 1)
        WaitJournalLine(starttime, "You put|failed", 5000)

    unload()


def gettiles(radius):
    minable = range(1339, 1359)
    found = []
    tempx, tempy = GetX(Self()), GetY(Self())
    for ix in range(tempx - radius, tempx + radius):
        for iy in range(tempy - radius, tempy + radius):
            tile = ReadStaticsXY(ix, iy, WorldNum())
            if tile:
                if tile[0]['Tile'] in minable:
                    found.append((tile[0]['Tile'], tile[0]['X'], tile[0]['Y'], tile[0]['Z']))
    AddToSystemJournal(found)
    return found


def mine(list):
    message_end = "Can't|" \
                  "Try mining elsewhere|" \
                  "There is nothing|" \
                  "so close|" \
                  "That is too far away|" \
                  "is attacking you|" \
                  "pickaxe is destroyed|" \
                  "fatigued|" \
                  "line of sight"
    message_attack = "is attacking you"

    for tile, x, y, z in list:
        NewMoveXY(x, y, True, 2, True)
        if Count(0x0E85) > 0:
            UseType2(0x0E85)
            starttime = datetime.now()
            WaitTargetTile(tile, x, y, z)
            WaitJournalLine(starttime, message_end, 120000)
            if ((InJournalBetweenTimes(message_attack, starttime, datetime.now())) > 0):
                UOSay("Guards")
                Wait(500)
                UOSay("Guards")
                Wait(500)

        elif Dead():
            ressurect()
            bank()
            make_tool()

        else:
            smelt()
            bank()
            unload()
            make_tool()
            # Hungry()

        if Weight() > MaxWeight() - 100:
            smelt()
            bank()
            make_tool()
            unload()
            # Hungry()


def SortTrees(trees):
    """ @param trees List of tuples(tile,x,y,z) """
    trees_by_distance = {}
    ordered_trees_list = []
    prev_last_tree = (0, start_cordinates[0], start_cordinates[1])

    def TreeDist(tree1, tree2):
        return Dist(tree1[1], tree1[2], tree2[1], tree2[2])

    for tree in trees:
        td = TreeDist(tree, prev_last_tree)
        if td % 2 == 0:
            td -= 1
        trees_group = trees_by_distance.get(td, [])
        trees_group.append(tree)
        trees_by_distance[td] = trees_group

    for current_distance in trees_by_distance:
        trees = trees_by_distance[current_distance]
        first_tree = last_tree = trees[0]
        for tree1 in trees:
            for tree2 in trees:
                if (TreeDist(tree1, tree2) > TreeDist(first_tree, last_tree)):
                    first_tree, last_tree = tree1, tree2
        if (TreeDist(prev_last_tree, last_tree) < TreeDist(prev_last_tree, first_tree)):
            first_tree, last_tree = last_tree, first_tree
        trees.sort(key=lambda tree: TreeDist(tree, first_tree))
        ordered_trees_list += trees
        prev_last_tree = last_tree

    return ordered_trees_list


if __name__ == '__main__':
    start_cordinates = (GetX(Self()), GetX(Self()))
    while (True):
        start = timeit.timeit()
        GoMina()
        mine(SortTrees(gettiles(numbertiles)))  # Obter lista dinamica de tiles
        end = timeit.timeit()
        print(f"It took to mine all area {end - start}")
