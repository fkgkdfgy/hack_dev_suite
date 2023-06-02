
from utils import *

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
    while line and line[0] in [' ','\r','\t']:
        line = line[1:]
    return line

class Tokenizer:
    def __init__(self) -> None:
        self.token_func={'keyword':(isKeyword,common_convert('keyword')),
                         'symbol':(isSymbol,common_convert('symbol')),
                         'intConst':(isIntegerConstant,common_convert('intConst')),
                         'stringConst':(isStringConstant,string_convert),
                         'identifier':(isIdentifer,common_convert('identifier'))}

    def segementLine(self,line,words):
        # 如果line 为空, 直接返回
        if not line:
            return
        
        # 如果第一个符号是 “ 向后寻找下一个 ” 然后取这其中的word(带着两边双引号)
        # ie. line == "words" words.append("words")
        if line[0] == '"':
            index = line[1:].find('"')
            if index<0:
                raise ParserException("something wrong with {0}".format(line))
            words.append(line[0:index+2])
            self.segementLine(line[index+2:],words)
            return
        
        # 如果是 BuiltInSymbol 就保存这个 symbol
        if line[0] in BuiltInSymbol:
            words.append(line[0])
            self.segementLine(line[1:],words)
            return 
        
        # 如果是分割符号，就跳过继续进行分割
        if line[0] in SegmentSymbol:
            self.segementLine(line[1:],words)
            return
        
        # 提取第一个Sumbol前的整个字段
        for index, char in enumerate(line):
            if char in BuiltInSymbol or char in SegmentSymbol:
                words.append(line[0:index])
                self.segementLine(line[index:],words)
                return                
            
        # 获取整个line 这出现在整个line 都是字符的情况
        words.append(line)
        return

    def transformWordIntoXML(self,word):
        for key,value in self.token_func.items():
            judge_func,convert_func = value
            if judge_func(word):
                xml = convert_func(word)
                word_and_type=(word if not key == 'stringConst' else word[1:-1],key)
                return xml,word_and_type 
        raise ParserException('unable to recognize this word{0}'.format(word))

    def processLine(self,line):
        if not line:
            return '',[]

        line = removeComment(line)
        line = removeHeadChar(line)

        if not line:
            return '',[]
        
        words = []
        self.segementLine(line,words)
       
        result = ''
        words_and_types = []
        for word in words:
            xml, word_and_type = self.transformWordIntoXML(word)
            result += xml + "\n"
            words_and_types.append(word_and_type)
        return result,words_and_types
    
if __name__ == "__main__":
    tokenizer = Tokenizer()
    
    # test line segments 
    line = "do calculate(x1,x2,e23_123);"
    words = []
    tokenizer.segementLine(line,words)
    print(words)

    line = '''while(~(x=10)){}'''
    words = []
    tokenizer.segementLine(line,words)
    print(words)

    line = '''          while(~(x=10)){do calculate(x1,x2,e23_123);} // test comment '''
    total_xml,unstructured_list = tokenizer.processLine(line)
    print(total_xml)
    print(unstructured_list)

    # more unit test
    line = '''class Main {  function void main() { var SquareGame game; let game = SquareGame.new(); do game.run(); do game.dispose(); return; } }'''
    total_xml,unstructured_list = tokenizer.processLine(line)
    print(total_xml)
    print(unstructured_list)
