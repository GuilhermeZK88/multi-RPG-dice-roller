# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 09:48:28 2021

@author: Guilherme
"""
from random import randint
#import string

class RollRequest(object):
    pass

class SimpleDie(RollRequest):    
    """
    simple dice with arbitrary number of faces
    """
    def __init__(self, faces):
        """ initialize a die instance, number of faces int, face up int"""
        self.faces = faces
        self.face_up = randint(1, faces) # remover esse conceito de face up?
        
    def getfaces(self):
        """ returns number of faces in the die """
        return self.faces
        
    def getroll(self): # remover esse conceito de face up?
        """ returns what face is currently up """
        return self.face_up
    
    def roll(self, dice_ammount=1):
        """ returns list of results of dice_ammount rolls """
        if dice_ammount >= 0:
            return [randint(1, self.getfaces()) for i \
                    in range(dice_ammount)]
        else:    
            return [-randint(1, self.getfaces()) for i \
                    in range(abs(dice_ammount))]
        

    
    def __str__(self):
        return 'simple d' + str(self.getfaces())


class ExplodingDie(SimpleDie):
    """
    dies that gets an extra same typed die to it's value if rolled within one
    of the 'x' ammount higher faces. ex: d10x explodes on 10s, d10xx on 10s
    and 9s, and so on.
    """
    def __init__(self, faces):
        """ ititialize a explodingdie instnace, explode range, fail range"""
        self.faces = int(faces.replace('x',''))
        self.explode = self.getfaces() - (int(faces.count('x')) - 1)
        self.low = 1
        
    def getexplode(self):
        """ returns minimum exploding int"""
        return self.explode
    
    def roll(self, dice_ammount=1):
        """ returns list of results of dice_ammount rolls + exploded"""
        rolls = []
        #print('explodes',self.explode,'or higher')
        if self.getexplode() <= 1:
            raise ValueError('Inifinite exploding die')
        for i in range(dice_ammount):
            result = randint(1, self.getfaces())
            rolls.append(result)
            while result >= self.getexplode():
                result = randint(1, self.getfaces())
                rolls[i] += result
        return rolls
    
    
class L5rDie(ExplodingDie): # ajeitar essa descendência (passar coisas pro
#exploding die, ou fazer l5r herdar do simple die)
    """
    As per L5r 4e, d10s that get rolled in pools where only some dice are kept
    as result, explodes 10s (extra range per added 'x') and reroll 1s 
    when emphases roll (extra range per added 'e').
    """
    def __init__(self, faces='10'):
        """ initialize a L5r style exploding dice """
        self.faces = int(faces.replace('x','').replace('e',''))
        self.explode = self.getfaces() - (int(faces.count('x')))
        self.reroll_range = faces.count('e')
        self.adjust_modifier = 0
        self.is_viable_roll()
    
    def is_viable_roll(self):
        """ Raise error if theres no reroll nor exploding die value """
        if self.explode <= self.reroll_range+1:
            raise ValueError ('Inifinite rerolling die!')
        print('viable roll')

    def get_adjust_modifier(self):
        return self.adjust_modifier
    
    def adjustpool(self, rolled, kept):
        """ adjust pool as per L5R max 10 dice pool rules """
        modifier = 0
        
        while rolled > 11 and kept < 10:
            rolled -= 2
            kept += 1
        
        if rolled > 10:
            modifier += 2 * (rolled-10)
            rolled = 10
        if kept > 10:
            modifier += 2 * (kept-10)
            kept = 10
        
        self.adjust_modifier = modifier
        
        print('rolled',rolled,'kept',kept)
        return (rolled, kept)


    def roll(self, to_roll, to_keep): #dice_ammount=1 precisa?
        """ returns list of results of dice_ammount rolls + exploded"""
        #print('b4 adjust')
        to_roll, to_keep = self.adjustpool(to_roll, int(to_keep))
        #print('after adjust')
        
        rolls = []
        #print('explodes',self.explode,'or higher')
        for i in range(to_roll):
            result = randint(1+self.reroll_range, self.getfaces())
            rolls.append(result)
            while result >= self.getexplode():
                result = randint(1+self.reroll_range, self.getfaces())
                rolls[i] += result
        rolls.sort()
        rolls.reverse()
        print('roll do l5r')
        
        total = sum(rolls[:to_keep])+self.get_adjust_modifier()
        return [total, rolls, self.get_adjust_modifier()]


class SuccessDie(SimpleDie):
    """
    Rolls die and counts 'Successes', those over arbitrary difficulty
    """
    def __init__(self, faces=10, difficulty=6, is_max_double=False):
        """ initialize a die wich rolls over or under success threshold"""
        self.faces = faces #int(faces.replace('x',''))
        self.difficulty = difficulty
        self.max = self.faces
        self.is_max_double = is_max_double
        self.low = 1
        
    def roll(self, pool_size):
        """ returns successes:int, rolls:list and veredit:string """
        rolls = []
        success_list = []
        success_die = 0
        one_count = 0

        for i in range(pool_size):
            roll = randint(1, self.getfaces())
            
            if roll >= self.difficulty:
                success_die += 1
                if roll >= self.max and self.is_max_double:
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
            print('Botch!')

        if one_count == 0:
            successes = sum(success_list)
        elif one_count > success_die:
            successes = success_die - one_count
        else:
            successes = sum( success_list[rolls.count(1):-rolls.count(1)] )         

        #print('successes:',successes,'|rolls/success_list:',rolls,success_list,\
              #'|succDie/1s:',success_die,one_count,'|2succOnMáx:',self.is_max_double)

        print(success_list)
        
        return 'Successes:', successes, 'Rolls:', rolls, 


class PercentDie(SimpleDie):
    """ Rolls a d100 / d%, if difficulty provided, classifies success as per
    Call of Cthulhu 7ed rules (fumble, normal, hard, extreme, critical), acepts
    bonus/penalty die
    """    
    def __init__(self, success_chance=None, bonus_die=0):
     """ initialize a die wich rolls over or under success threshold"""
     self.success_chance = success_chance
     self.bonus_die = bonus_die
    
    def set_chance(self, chance):
         self.success_chance = chance
    def get_chance(self):
        return self.success_chance
     
    def classify_success(self, result):
        if self.get_chance() is None:
            return None
        if result == 1:
            success = 'Critical Success!!!'
        elif result <= self.get_chance()//5:
            success = 'Extreme Success!'
        elif result <= self.get_chance()//2:
            success = 'Hard Success!'
        elif result <= self.get_chance():
            success = 'Normal Success'
        elif result <= 95:
            success = 'Fail'
        elif result <= 99 and self.get_chance() >= 50:
            success = 'Fail'
        else:
            success = 'Fumble!'

        return success
    
    def roll(self, chance=None, bonus_die=0):
        tens_die = 0
        unit_die = str(randint(0,9))
        is_penalty = False
        rolls = []
        
        if chance is None:
            pass
        else:
            self.set_chance(chance)
        
        if bonus_die < 0:
            is_penalty = True
        
        for die in range(1+abs(bonus_die)):
            tens_die = (str(randint(0,9)))
            if tens_die == '0' and unit_die == '0':
                rolls.append(100)
            else:
                rolls.append( int(tens_die + unit_die) )
            
        rolls.sort()
        if is_penalty:
            rolls.reverse()
        
        success_status = self.classify_success(rolls[0])
        return success_status, rolls
    
    
#--------------------------------------------------------
def clean_input(brute_string):
    """ padronizing input string """
    #string.punctuarion -> '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    string_punctuation = ' !"#$%&\'()*,./:;<=>?@[\\]^_`{|}~' # +,-
    #string.ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
    string_unused_letters = 'abcfghijlmnopqrstuvwyz' # d,x,k,e
    string_blicklisted = string_punctuation + string_unused_letters
    
    string = brute_string.lower()
    
    for char in string:
        if char in string_blicklisted:
            string = string.replace(char,'')
            
    return string

def interpret(string):
    """
    processes a string into a roll request

    """

    try:
        if string[0] == '-':
            string = '0'+string
    except IndexError:
        string='0'
    string = string.replace('+-','-').replace('-','+-')
    print('Calculating:',string)
    string_list = string.split('+')
    
    return string_list


def dice_thrower(string_list):
    #print(string_list)
    rolled_dice = []
    modifiers = 0
    
    for item in string_list:
    
        try:
            number_of_dice = int(item.split('d')[0])
        except ValueError:
            number_of_dice = 1  
    
        if ('d' in item and 'k' in item):
            raise ValueError ('Conflicted notations used in a die (d and k)')

        elif 'd' in item: # notação 'd' -> SimpleDie, ExplodingDie
            rolled_dice = d_throw(item, number_of_dice, rolled_dice)
    
        elif 'k' in item: # notação 'k' -> L5rDie
            rolled_dice = k_throw(item, number_of_dice, rolled_dice)

        else:
            modifiers += int(item)
            #print('modifiers',modifiers)
    
    #print('b4 print rolled_dice',rolled_dice)        
    #print('b4 print append',rolled_dice.append(modifiers))
    rolled_dice.append(modifiers)
    
    return rolled_dice

def d_throw(item, number_of_dice, rolled_dice):  
    """ 'd' notation: arbitrary faces dice roll. item:string, number_of_dice:
        int, rolled_dice:list
    """
    #print('number_of_dice',number_of_dice)
    die_type = item.split('d')[1]
    #print('die_type',die_type)
    if 'x' in die_type:
        rolled_dice.append(ExplodingDie(die_type).roll(number_of_dice))
    else:
        rolled_dice.append(SimpleDie(int(die_type)).roll(number_of_dice))
    
    #print('rolled_dice',rolled_dice)
    
def k_throw(item, rolled_pool, rolled_dice):
    """ 'k' notation: d10 rolled/kept dice roll (L5r style). item:string,
    rolled_pool:int, rolled_dice:list
    """
    #print('rolled_pool',rolled_pool)
    kept_pool = item.split('k')[1]
    #print('kept_pool',kept_pool)

    rolled_dice.append(L5rDie().roll(rolled_pool,kept_pool))

    #print('rolled_dice',rolled_dice)

def result_presenter(rolled_dice):

    total = 0
    for elem in rolled_dice:
        if type(elem) is list:
            total += sum(elem)
        elif type(elem) is int:
            total += elem
        else:
            print(type(elem))
            raise TypeError
    
    return print('RESULT:' , total , '| Details:' , rolled_dice)


def roll(): #keep string part before ':' as roll describer -> Attack:1d20+5 -> Attack:17 , [12],+5
    roll_me = input("What's to be rolled? ")
    if 'help' in roll_me.lower():
        print('provisory_help_message')
    else:
        return result_presenter(dice_thrower(interpret(clean_input(roll_me))))

    



















