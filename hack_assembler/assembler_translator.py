#!/bin/python

from cgi import test
from utilis import *

CompBuiltInCode={
    '0':'0101010',
    '1':'0111111',
    '-1':'0111010',
    'D':'0001100',
    'A':'0110000',
    '!D':'0001101',
    '!A':'0110001',
    '-D':'0001111',
    '-A':'0110011',
    'D+1':'0011111',
    'A+1':'0110111',
    'D-1':'0001110',
    'A-1':'0110010',
    'D+A':'0000010',
    'D-A':'0010011',
    'A-D':'0000111',
    'D&A':'0000000',
    'D|A':'0010101',
    'M':'1110000',
    '!M':'1110001',
    '-M':'1110011',
    'M+1':'1110111',
    'M-1':'1110010',
    'D+M':'1000010',
    'D-M':'1010011',
    'M-D':'1000111',
    'D&M':'1000000',
    'D|M':'1010101',
}

DestBuiltInCode = {
    None:'000',
    'M':'001',
    'D':'010',
    'MD':'011',
    'A':'100',
    'AM':'101',
    'AD':'110',
    'AMD':'111',
}

JumpBuiltInCode = {
    None:'000',
    'JGT':'001',
    'JEQ':'010',
    'JGE':'011',
    'JLT':'100',
    'JNE':'101',
    'JLE':'110',
    'JMP':'111',
}

def DecToBin(number, max_bit):
    result = '0'*max_bit
    binary = bin(number)[2:]
    bit_size = max_bit if len(binary) >= max_bit else len(binary)
    result = '0'*(max_bit-bit_size) + binary[0:bit_size]
    return result

class Translator:
    def __init__(self):
        pass
    
    def Process(self,words):
        # not translate label definition instruction
        if not words or words[0] == '(':
            return ''
       
        binary_code=''
        if words[0] == '@':
            binary_code = '0'
            binary_code += DecToBin(int(words[1]),15)
            print('value',words[1])
            print('binary',binary_code)
        else:
            binary_code = '111'
            left_words = words

            jump,dest,comp=None,None,None
            if ';' in left_words:
                jump = left_words[-1]
                left_words = left_words[0:-2]

            if '=' in left_words:
                dest = left_words[0]
                comp = ''.join(left_words[2:])
            else:
                comp = ''.join(left_words[0:])

            print('comp',comp)
            print('dest',dest)
            print('jump',jump)

            binary_code += CompBuiltInCode[comp]
            binary_code += DestBuiltInCode[dest]
            binary_code += JumpBuiltInCode[jump]

        return binary_code

if __name__ == '__main__':
    test_translator = Translator()
    
    result = DecToBin(256,15)
    print(result)

    # line=['(', 'ABC', ')']
    # result = test_translator.Process(line)
    # print(result)

    # line=['@', 'ASD']
    # result = test_translator.Process(line)
    # print(result)

    line=['@', '123']
    result = test_translator.Process(line)
    print(result)

    line=['0', ';', 'JMP']
    result = test_translator.Process(line)
    print(result)

    line=['AMD', '=', 'D', '+', '1', ';', 'JGE']
    result = test_translator.Process(line)
    print(result)