# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 09:48:28 2021

@author: Guilherme
"""
from random import randint

# TODO: classes devem responder rolagem com tupla (int:valor, str:info)

class SimpleDie(object):
    """
    simple dice with arbitrary number of faces
    """

    def __init__(self, faces):
        """ initialize a die instance, number of faces int, face up int"""
        self.faces = faces

    def getfaces(self):
        """ returns number of faces in the die """
        return self.faces

    def roll(self, dice_ammount=1):
        """ returns a tuple with (int: sum_value , str: roll details)"""
        rolls = []
        if dice_ammount >= 0:
            rolls = [randint(1, self.getfaces()) for i in range(dice_ammount)]
        else:
            rolls = [-randint(1, self.getfaces()) for i in range(abs(dice_ammount))]
        
        details = str(dice_ammount) + 'd' + str(self.getfaces()) + '=' + \
                  str(rolls) + '=' + str(sum(rolls))
        
        return sum(rolls) , details #str(rolls)


class ExplodingDie(SimpleDie):
    """
    die that gets an extra same typed die to it's value if roll value is among
    the \'x' ammount\ higher faces. ex: d10x explodes on the one higher faces
    (so in 10s), d10xx on the two higher faces (so in 10s and 9s), and so on.
    """

    def __init__(self, faces):
        """ ititialize a explodingdie instnace, explode range, fail range"""
        self.faces = int(str(faces).replace("x", ""))
        self.explode = self.getfaces() - (int( str(faces).count("x") ) - 1)
        self.low = 1

    def getexplode(self):
        """ returns minimum exploding int"""
        return self.explode

    def roll(self, dice_ammount=1):
        """ returns a tuple with (int: sum_value , str: roll details)"""
        rolls = []
        print("ExplodingDie||explodes", self.explode, "or higher")
        if self.getexplode() <= 1:
            raise ValueError("Inifinite exploding die")
        for i in range(dice_ammount):
            result = randint(1, self.getfaces())
            rolls.append(result)
            while result >= self.getexplode():
                result = randint(1, self.getfaces())
                rolls[i] += result

        return sum(rolls) , str(rolls)


class L5rDie(ExplodingDie):  # ajeitar essa descendência (passar coisas pro
    # exploding die, ou fazer l5r herdar do simple die)
    """
    As per L5r 4e, d10s that get rolled in pools where only some dice are kept
    as result, explodes 10s (extra range per added 'x') and reroll 1s 
    when emphases roll (extra range per added 'e').
    """

    def __init__(self, parameters="", faces="10"):
        """ initialize a L5r style exploding dice """
        #self.faces = int(faces.replace("x", "").replace("e", ""))
        self.faces = int(faces)
        self.explode = self.getfaces() - (int(parameters.count("x"))) #faces->parameters
        self.reroll_range = parameters.count("e") #faces->parameters
        self.adjust_modifier = 0
        self.is_viable_roll()

    def is_viable_roll(self):
        """ Raise error if theres no reroll nor exploding die value """
        if self.explode <= self.reroll_range + 1:
            raise ValueError("Inifinite rerolling die!")

    def get_adjust_modifier(self):
        return self.adjust_modifier

    def adjustpool(self, rolled, kept):
        """ adjust pool as per L5R max 10 dice pool rules """
        modifier = 0
        #pre_adjust = f"{rolled}k{kept}" # variável pra printar info de ajuste
        while rolled > 11 and kept < 10:
            rolled -= 2
            kept += 1

        if rolled > 10:
            modifier += 2 * (rolled - 10)
            rolled = 10
        if kept > 10:
            modifier += 2 * (kept - 10)
            kept = 10

        self.adjust_modifier = modifier
        #print(f"{pre_adjust} adjusted to: {rolled}k{kept}+{modifier}")
        return (rolled, kept)

    def roll(self, to_roll, to_keep):  # dice_ammount=1 precisa?
        """ returns list of results of dice_ammount rolls + exploded"""
        # print('b4 adjust')
        to_roll, to_keep = self.adjustpool(int(to_roll), int(to_keep))
        # print('after adjust')

        rolls = []
        # print('explodes',self.explode,'or higher')
        for i in range(to_roll):
            result = randint(1 + self.reroll_range, self.getfaces())
            rolls.append(result)
            while result >= self.getexplode():
                result = randint(1 + self.reroll_range, self.getfaces())
                rolls[i] += result
        rolls.sort()
        rolls.reverse()

        total = sum(rolls[:to_keep]) + self.get_adjust_modifier()
        #return total, str((rolls, self.get_adjust_modifier()))

        details = str(to_roll) + 'k' + str(to_keep) + '+' + \
                  str(self.adjust_modifier) + '=' + str(total) + str(rolls)

        return total, details


class SuccessDie(SimpleDie):
    """
    Rolls die and counts 'Successes', those over arbitrary difficulty
    """  # trocar ordem faces-difficulty, pra caso 1 parâmetro, este == diff?

    def __init__(self, faces=10, difficulty=6, is_max_double=False):
        """ initialize a die wich rolls over or under success threshold"""
        self.faces = faces  # int(faces.replace('x',''))
        self.difficulty = difficulty
        self.is_max_double = is_max_double
        self.low = 1

    def roll(self, pool_size=1):
        """ returns successes:int, rolls:list and veredit:string """
        rolls = []
        success_list = []
        success_die = 0
        one_count = 0

        for i in range(pool_size):
            roll = randint(1, self.getfaces())

            if roll >= self.difficulty:
                success_die += 1
                if roll >= self.faces and self.is_max_double:
                    success_list.append(2)
                else:
                    success_list.append(1)

            elif roll == 1:
                one_count += 1
                success_list.append(-1)
            else:
                success_list.append(0)

            rolls.append(roll)

        rolls.sort(), rolls.reverse()
        success_list.sort(), success_list.reverse()

        if success_die == 0 and one_count > 0:
            print("BOTCH!")

        if one_count == 0:
            successes = sum(success_list)
        elif one_count > success_die:
            successes = success_die - one_count
        else:
            successes = sum(success_list[rolls.count(1) : -rolls.count(1)])

        details = str(pool_size) + 's' + str(self.difficulty) + str(rolls) + \
                  '=' + str(successes)
        #print("<SuccDie.roll>success list:",success_list)
        return successes, details


class PercentDie(SimpleDie):
    """ Rolls a d100 / d%, if difficulty provided, classifies success as per
    Call of Cthulhu 7ed rules (fumble, normal, hard, extreme, critical), acepts
    bonus/penalty die
    """

    def __init__(self):#, success_chance=None, bonus_die=0):
        """ initialize a die wich rolls over or under success threshold"""
        #self.success_chance = int(success_chance)
        #self.bonus_die = bonus_die

    def classify_success(self, result, chance):
        if chance == 0 or chance is None: 
            return "(Unknown success level)."
        if result == 1:
            success = "Critical Success!!!"
        elif result <= chance // 5:
            success = "Extreme Success!"
        elif result <= chance // 2:
            success = "Hard Success!"
        elif result <= chance:
            success = "Normal Success."
        elif result <= 95:
            success = "Fail."
        elif result <= 99 and chance >= 50:
            success = "Fail."
        else:
            success = "Fumble!!!"

        return success

    def roll(self, chance=None, bonus_die=0):
        unit_die = str(randint(0, 9))
        is_penalty = False
        rolls = []

        if int(bonus_die) < 0:
            is_penalty = True

        for die in range(1 + abs(int(bonus_die))):
            tens_die = str(randint(0, 9))
            if tens_die == "0" and unit_die == "0":
                rolls.append(100)
            else:
                rolls.append(int(tens_die + unit_die))

        rolls.sort()
        if is_penalty:
            rolls.reverse()

        success_status = self.classify_success(rolls[0], int(chance))

        result = str(rolls[0]) + ", " + success_status
        if chance == '0':#or chance is None:
            details = str(rolls) + " in " + '(Unknown)' + ' skill'
        else:
            details = str(rolls) + " in " + str(chance) + ' skill'

        return result, details


# --------------old approach (edited/butchered)---------------------------
def hidding_old_approach_in_this_function():
# =============================================================================
# def dice_thrower(string_list):
#     ####falta implementar solicitar SuccessDie e solicitar PercentDie####
#     print("string_list", string_list)
#     rolled_dice = []
#     modifiers = 0
# 
#     def howManyDie(die_notation):
#         """given a die_notation type:string, retrieves number_of_dice tpy:int"""
#         try:
#             number_of_dice = int(item.split(die_notation)[0])
#             print("number_of_dice", number_of_dice)
#         except ValueError:
#             print("Value Error na dice_thrower", item.split(die_notation)[0])  ##debugging##
#             if item.split(die_notation)[0] == '-':
#                 number_of_dice = -1
#             else:
#                 number_of_dice = 1
# 
#         return number_of_dice
# 
#     for item in string_list:
# 
#         if "d" in item and "k" in item:
#             raise ValueError("Conflicted notations used in a die (d and k)")
# 
#         elif "d" in item:  # notação 'd' -> SimpleDie, ExplodingDie
#             number_of_dice = howManyDie("d")
#             # print('d_throw(item, number_of_dice, rolled_dice), param:',item, number_of_dice, rolled_dice)
#             rolled_dice = d_throw(item, number_of_dice, rolled_dice)
# 
#         elif "k" in item:  # notação 'k' -> L5rDie
#             number_of_dice = howManyDie("k")
#             print(
#                 "k_throw(item, number_of_dice, rolled_dice), param:",
#                 item,
#                 number_of_dice,
#                 rolled_dice,
#             )
#             rolled_dice = k_throw(item, number_of_dice, rolled_dice)
# 
#         else:
#             modifiers += int(item)
#             # print('modifiers',modifiers)
# 
#     # print('b4 print rolled_dice',rolled_dice)
#     # print('b4 print append',rolled_dice.append(modifiers))
#     rolled_dice.append(modifiers)
# 
#     return rolled_dice
# 
# 
# def d_throw(item, number_of_dice, rolled_dice):
#     """ 'd' notation: arbitrary faces dice roll. item:string, number_of_dice:
#         int, rolled_dice:list
#     """
#     # print('number_of_dice',number_of_dice)
#     die_type = item.split("d")[1]
#     # print('die_type',die_type)
#     if "x" in die_type:
#         rolled_dice.append(ExplodingDie(die_type).roll(number_of_dice))
#     else:
#         rolled_dice.append(SimpleDie(int(die_type)).roll(number_of_dice))
# 
#     print('rolled_dice',rolled_dice)
#     return rolled_dice
# 
# 
# def k_throw(item, rolled_pool, rolled_dice):
#     """ 'k' notation: d10 rolled/kept dice roll (L5r style). item:string,
#     rolled_pool:int, rolled_dice:list
#     """
#     kept_pool = ""
#     die_specs = ""
#     # print('k_throw||rolled_pool',rolled_pool)
#     after_k = item.split("k")[1]
#     # print('kept_pool',kept_pool)
# 
#     for char in after_k:
#         if char in "0123456789":
#             kept_pool += kept_pool + char
#         else:
#             die_specs += die_specs + char
# 
#     l5rDie = L5rDie(die_specs)
# 
#     rolled_dice.append(l5rDie.roll(rolled_pool, kept_pool))
# 
#     print("rolled_dice", rolled_dice)
#     return rolled_dice
# 
# 
# def result_presenter(rolled_dice):
#     print("result_pres||rolled_dice", rolled_dice, type(rolled_dice))
#     total = 0
#     for elem in rolled_dice:
#         if type(elem) is list:
#             total += sum(elem)
#         elif type(elem) is int:
#             total += elem
#         else:
#             print(type(elem))
#             raise TypeError
# 
#     return print("RESULT:", total, "| Details:", rolled_dice)
# 
# 
# def roll():  # keep string part before ':' as roll describer -> Attack:1d20+5 -> Attack:17 , [12],+5
#     roll_me = input("What's to be rolled? ")
#     if "help" in roll_me.lower():
#         print("provisory_help_message")
#     else:
#         return result_presenter(dice_thrower(interpret(clean_input(roll_me))))
# =============================================================================
    return None
# ---------------------ALTERNATE APPROACH--------------------

def bot():  # keep string part before ':' as roll describer -> Attack:1d20+5 -> Attack:17 , [12],+5
    """ coleta input do usuário para chamar rolagens ou ajuda, sai com 'exit'"""
    while True:
        brute_string = input("What's to be rolled? ")
        if "help" == brute_string.lower()[0:4]:
                print("provisory_help_message: type a roll after a prefix",\
                      "and optional parameters <param>: sr (3d6+1d4+3),",\
                      "wr (10s6<w><x>), lr (13k9<e><x><x>), cr (70<b><b><p>)")
        elif "exit" in brute_string.lower()[0:4]:
                return 
        else:
            check_for_die(brute_string)


def check_for_die(brute_string): #TODO mensagem de ajuda e acertar a interface
    """checks input(str) for specific die roll"""
    #is_specific_roll = False
    specific_die = {'sr': simple_roll,
                    'lr': l5r_roll,
                    'wr': wod_roll,
                    'cr': cthulhu_roll}
    if brute_string[:2] not in specific_die:
        #is_specific_roll = True
        print('No specific roll command detected')
        #interpret(clean_input(brute_string))
        cleaned_string, parameters = clean_input(brute_string, None)
        string_list, parameters_list = interpret(cleaned_string), \
                                       interpret(parameters)
        return

    #print('brute',brute_string[2:], brute_string[:2])

    cleaned_string, parameters = clean_input(brute_string[2:], brute_string[:2])
    string_list,parameters_list = interpret(cleaned_string),interpret(parameters)
    #print("cfd sending to specific roll:", '+'.join(parameters_list))

    specific_die[brute_string[:2]](string_list, parameters_list) #chamando a função pertinente

    return


def clean_input(brute_string, specific_die=None):
    """ padronizing input string """
    # string.punctuarion -> '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    punctuation = " !\"#$%&'()*,./:;<=>?@[\\]^_`{|}~"  # +,- |#TODO implement * (multiroladas -> 5*1d20+1 -> [14,11,21,2,6])
    # string.ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    parameters_string = ''
    die_idiosyncrasies = {'sr': ['abcefghijklmnopqrstuvwxyz', ''], # d
                          'lr': ['abcdfghijlmnopqrstuvwyz', 'xe'], # k,x,e
                          'wr': ['abcdefghijklmnopqrtuvyz', 'xw'], # s,w,x
                          'cr': ['acdefghijklmnoqrstuvwxyz', 'bp'], # b,p
                          None: ['abcefghijklmnopqrstuvwxyz', '']} # d
    
    string_blicklisted = punctuation + die_idiosyncrasies[specific_die][0]
    cleaned_string = brute_string.lower()
    #print(f'clning_input: brute lowercase {cleaned_string}')

    for char in cleaned_string:
        if char in string_blicklisted:
            cleaned_string = cleaned_string.replace(char, "")
        elif char in die_idiosyncrasies[specific_die][1]:
            parameters_string += char
            cleaned_string = cleaned_string.replace(char, "")
        else:
            parameters_string += char

    return cleaned_string, parameters_string


def interpret(string):
    """
    splits a string with sums of rolls and numbers into a list of strings
    each a roll or number. I.E.: '3d6+5+1d4' -> ['3d6', '5', '1d4']
    
    """
    try:
        if string[0] == "-":
            string = "0" + string
    except IndexError:
        #print('interpret() index error') #debug
        string = "0"
    string = string.replace("+-", "-").replace("-", "+-")
    #print("Calculating:", string)
    string_list = string.split("+")

    return string_list


def howManyDie(item, die_notation):
    """given a die_notation type:string, retrieves number_of_dice tpy:int"""
    try:
        number_of_dice = int(item.split(die_notation)[0])
        #print("number_of_dice", number_of_dice)
    except ValueError:
        #print("Value Error na dice_thrower", item.split(die_notation)[0])  ##debugging##
        if item.split(die_notation)[0] == '-':
            number_of_dice = -1
        else:
            number_of_dice = 1
    return number_of_dice


def simple_roll(string_list, parameters=None):
    modifier = 0
    results = [] # list of tuples from simpledie.roll()
    
    for item in string_list:
        if 'd' in item:
            try:
                #number_of_dice = int(item.split('d')[0])
                number_of_dice = howManyDie(item, 'd')
                die_faces = int(item.split('d')[1])
                die = SimpleDie(die_faces)
                results += die.roll(number_of_dice)
            except ValueError:
                raise ValueError(f'Oops! Could not understand this: "{item}"')
        else:
            try:
                modifier += int(item)
            except ValueError:
                raise ValueError(f'Oops! Could not understand this: "{item}"')

    total = sum(results[::2])+modifier
    details = ' ; '.join(results[1::2]) + ' ; modifier: ' + str(modifier)
    print(f'RESULT: {total} <sr roll details: {details}>')
    return


def l5r_roll(string_list, parameters):

    modifier = 0
    results = [] # list of tuples from l5rdie.roll()
    #print('strg_lst',string_list,'| parmtrs', parameters,'l5roll')
    
    for (itemS, itemP) in zip(string_list, parameters):
        #print('item: ',itemS,itemP)
        if 'k' in itemS:
            try:
                number_of_dice = howManyDie(itemS, 'k')
                dice_kept = int(itemS.split('k')[1])
            except ValueError:
                raise ValueError(f'Oops! Could not understand this die roll(?): "{itemS}/{itemP}"')
            else:
                die = L5rDie(itemP)
                results += die.roll(number_of_dice, dice_kept)
        else:
            try:
                modifier += int(itemS)
            except ValueError:
                raise ValueError(f'Oops! Could not understand this modifier(?): "{itemS}/{itemP}"')

    total = sum(results[::2])+modifier
    #print(f'l5r_roll results: {results}')
    
    if modifier == 0:
        print(str(modifier),'if str(modifier) == 0:')
        details = ' ; '.join(results[1::2])
    else:
        print(str(modifier),'if str(modifier) == 0:ELSE:')
        details = ' ; '.join(results[1::2]) + ' ; other mods: ' + str(modifier)

    print(f'RESULT: {total} <lr roll details: {details}>')
    return


def wod_roll(string_list, parameters):
    modifier = 0
    results = [] # list of tuples from successdie.roll()
    #print('wodroll parameters:',parameters)
    is_max_double = False
    will = ''

    for (itemS, itemP) in zip(string_list, parameters):

        if 'x' in itemP:
            is_max_double = True

        if 'w' in itemP:
            will = '+Will'

        if 's' in itemS:
            try:
                number_of_dice = howManyDie(itemS, 's')
                difficulty = int(itemS.split('s')[1])
            except ValueError:
                raise ValueError(f'Oops! Could not understand this: "{itemP}"')
            else:
                die = SuccessDie(10,difficulty,is_max_double)
                results += die.roll(number_of_dice)
        else:
            try:
                modifier += int(itemS)
            except ValueError:
                raise ValueError(f'Oops! Could not understand this: "{itemP}"')

    if modifier == 0:
        mod = ''
    else:
        mod = '+' + str(modifier)
        
    total = sum(results[::2]) #+modifier
    details = ' ; '.join(results[1::2]) + ' ; modifier: ' + str(modifier)
    print(f'{total}{mod}{will} Successes. <wr roll details: {details}>')
    return

def cthulhu_roll(string_list, parameters):# TODO
    results = [] # list of tuples from successdie.roll()
    #print('xuluroll parameters:',parameters)
    
    for (itemS, itemP) in zip(string_list, parameters):
        bonus_die = itemP.count('b') - itemP.count('p')

        die = PercentDie()
        results += die.roll(itemS, bonus_die)

    total = ' <and> '.join(results[::2]) #+modifier
    details = ' ; '.join(results[1::2]) #+ ' ; modifier: ' + str(modifier)
    print(f'{total} <cr roll details: {details}>')
    return


#------instâncias de dados------
simpledie=SimpleDie(6)   # self,faces / roll(self,dice_ammount=0)
explodingdie=ExplodingDie(6)   # self,faces / roll(self,dice_ammount=0) /getexplode
l5rdie=L5rDie()   # (self, parameters="", faces="10") / (self, to_roll, to_keep)
successdie=SuccessDie()   # (self, faces=10, difficulty=6, is_max_double=False) / (self, pool_size=1)
percentdie=PercentDie()   # (self) / (self, chance=None, bonus_die=0)

#roll()