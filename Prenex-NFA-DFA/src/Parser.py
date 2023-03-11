from __future__ import annotations
from builtins import print
from typing import Type
from src.Regex import Character, Operator
from src.DFA import DFA

def isAtom(s: str) -> bool:
    if s.isalnum():
        return True
    return False
def createConcat(s: str) -> str:
    req = Requirements()
    my_str = s
    pos = 0
    for char in my_str:
        if pos < len(my_str) - 1:
            if isAtom(my_str[pos]) and isAtom(my_str[pos + 1]):
                my_str = my_str[:pos + 1] + '.' + my_str[pos + 1:]
                pos = pos + 1

            elif isAtom(my_str[pos]) and my_str[pos + 1] == '(':
                my_str = my_str[:pos + 1] + '.' + my_str[pos + 1:]
                pos = pos + 1

            elif my_str[pos] == ')' and isAtom(my_str[pos + 1]):
                my_str = my_str[:pos + 1] + '.' + my_str[pos + 1:]
                pos = pos + 1

            elif my_str[pos] == ')' and my_str[pos + 1] == '(':
                my_str = my_str[:pos + 1] + '.' + my_str[pos + 1:]
                pos = pos + 1

            elif my_str[pos] == '*' or my_str[pos] == '+':

                if my_str[pos + 1] == '(':
                    my_str = my_str[:pos + 1] + '.' + my_str[pos + 1:]
                    pos = pos + 1
                elif isAtom(my_str[pos + 1]):
                    my_str = my_str[:pos + 1] + '.' + my_str[pos + 1:]
                    pos = pos + 1


        pos = pos + 1
    return my_str
def replaceNums() -> str:
    numbers = '('
    for i in range(9):
        numbers = numbers + str(i) + '|'
    numbers = numbers + '9)'
    return numbers
def replaceChars(type) -> str:
    chars = '('
    if type == 0:
        for i in range(ord('a'), ord('z')):
            chars = chars + chr(i) + '|'
        chars = chars + 'z)'
    if type == 1:
        for i in range(ord('A'), ord('Z')):
            chars = chars + chr(i) + '|'
        chars = chars + 'Z)'
    return chars

class Requirements:
    def __init__ (self):
        self.operators = {'.', '|', '*', '+', '?', '(', ')'}
        self.priority = {'|':1, '?':3, '.':2, '*':3, '+':3}
class Parser:
    # This function should:
    # -> Classify input as either character(or string) or operator
    # -> Convert special inputs like [0-9] to their correct form
    # -> Convert escaped characters
    # You can use Character and Operator defined in Regex.py
    @staticmethod
    def preprocess(regex: str) -> list:
        pass

    @staticmethod
    def infixToPrefix(my_str) -> str:
        req = Requirements()
        stack = []
        output = ''
        for char in my_str:
            if char not in req.operators:
                output = output + char
            elif char == '(':
                stack.append('(')
            elif char == ')':
                while stack and stack[-1] != '(':
                    output = output + stack.pop()
                stack.pop()
            else:
                while stack and stack[-1] != '(' and req.priority[char] <= req.priority[stack[-1]]:
                    output = output + stack.pop()
                stack.append(char)
        while stack:
            output = output + stack.pop()
        return output

    # This function should construct a prenex expression out of a normal one.
    @staticmethod
    def toPrenex(s: str) -> str:
        if s == "eps":
            return s
        req = Requirements()
        my_str = s
        if '[0-9]' in my_str:
            my_str = my_str.replace('[0-9]', replaceNums())
        if '[a-z]' in my_str:
            my_str = my_str.replace('[a-z]', replaceChars(0))
        if '[A-Z]' in my_str:
            my_str = my_str.replace("[A-Z]", replaceChars(1))
        print(my_str)
        my_str = createConcat(my_str)
        print(my_str)
        #infix to postfix
        my_str = Parser.infixToPrefix(my_str)
        #postfix to prefix
        stack = []
        output = ''
        for char in my_str:
            if char in req.operators:
                if char == '*' or char == '+':
                    op1 = stack.pop()
                    temp = char + op1
                    stack.append(temp)
                else:
                    op1 = stack.pop()
                    op2 = stack.pop()
                    temp = char + op2 + op1
                    stack.append(temp)
            else:
                stack.append(char)
        while stack:
            output = output + stack.pop()

        #adaug spatii
        pos = 0
        for char in output:
            if pos < len(output) - 1:
                output = output[:pos + 1] + ' ' + output[pos + 1:]
                pos = pos + 2

        my_str = output
        my_str = my_str.replace(".", "CONCAT")
        my_str = my_str.replace("|", "UNION")
        my_str = my_str.replace('*', "STAR")
        my_str = my_str.replace("+", "PLUS")
        my_str = my_str.replace("?", "MAYBE")
        return my_str

if __name__ == "__main__":
    s = Parser.toPrenex("ab|c")
    dfa = DFA.fromPrenex(s)
    print(dfa.accepts("c"))
    print(dfa.accepts("ab"))
    print(dfa.accepts("ac"))
    print(dfa.accepts("abc"))
    print(s)

