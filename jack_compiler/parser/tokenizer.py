
from utils import *

BuiltInKeywords=['class' , 'constructor' , 'function' ,
                 'method' , 'field' , 'static' , 'var' , 'int' , 
                 'char' , 'boolean' , 'void' , 'true' , 'false' , 
                 'null' , 'this' , 'let' , 'do' , 'if' , 'else' , 
                 'while' , 'return']

BuiltInSymbol = ['{' , '}' , '(' , ')' , '[' , ']' , '. ' , ', ' , '; ' , '+' , '-' , '*' , 
                 '/' , '&' , ',' , '<' , '>' , '=' , '~']

SegmentSymbol = [' ','\t','\r','\n','"']

def isKeyword(word):
    return word in BuiltInKeywords

def isSymbol(word):
    return word in BuiltInSymbol

def isIntegerConstant(word):
    return word.isdigit()

def isStringConstant(word):
    return word[0] == '"' and word[-1] == '"'

def isIdentifer(word):
    def isValidChar(c):
        return c.isalpha() or c.isdigit() or c=='_'
    if not word or word[0].isdigit():
        return False
    for c in word[1:]:
        if not isValidChar(c):
            return False
    return True

def removeComment(sentense):
    result = sentense
    if '//' in result:
        index = result.find('//')
        result = result[0:index]
    return result

def removeHeadChar(line):
    if not line:
        return line
    while line[0] in [' ','\r','\t']:
        line = line[1:]
    return line

def common_convert(type):
    def inner_helper(word):
        return "<{0}> {1} </{0}>".format(type,word)
    return inner_helper

def string_convert(word):
    return "<{0}> {1} </{0}>".format("stringConst",word[1:-1])

class Tokenizer:
    def __init__(self) -> None:
        self.token_func={'keyword':(isKeyword,common_convert('keyword')),
                         'symbol':(isSymbol,common_convert('symbol')),
                         'intConst':(isIntegerConstant,common_convert('intConst')),
                         'stringConst':(isStringConstant,string_convert),
                         'identifier':(isIdentifer,common_convert('identifier'))}

    def segementLine(self,line,words):
        if not line:
            return
        
        if line[0] == '"':
            index = line[1:].find('"')
            if index<0:
                raise ParserException("something wrong with {0}".format(line))
            words.append(line[0:index+1])
            self.segementLine(line[index+1:],words)
            return
        
        if line[0] in BuiltInKeywords:
            words.append(line[0])
            self.segementLine(line[1:],words)
            return 
        
        if line[0] in SegmentSymbol:
            self.segementLine(line[1:],words)
            return
        
        for index, char in enumerate(line):
            if char in BuiltInSymbol or char in SegmentSymbol:
                words.append(line[0:index])
                self.segementLine(line[index:],words)
                break                
        return 
    
    def transformWordIntoXML(self,word):
        for key,value in self.token_func:
            judge_func,convert_func = value
            if judge_func(word):
                return convert_func(word)
        raise ParserException('unable to recognize this word{0}'.format(word))

    def processLine(self,line):
        line = removeComment(line)
        line = removeHeadChar(line)
        if not line:
            return ''
        
        result = ''
        words = []
        self.segementLine(line,words)
        for word in words:
            result += self.transformWordIntoXML(word) + "\n"
        return result
    
    
        