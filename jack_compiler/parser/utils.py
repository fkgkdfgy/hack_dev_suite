class ParserException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

BuiltInKeywords=['class' , 'constructor' , 'function' ,
                 'method' , 'field' , 'static' , 'var' , 'int' , 
                 'char' , 'boolean' , 'void' , 'true' , 'false' , 
                 'null' , 'this' , 'let' , 'do' , 'if' , 'else' , 
                 'while' , 'return']

BuiltInSymbol = ['{' , '}' , '(' , ')' , '[' , ']' , '.' , ',' , ';' , '+' , '-' , '*' , 
                 '/' , '&' , ',' , '<' , '>' , '=' , '~']

SegmentSymbol = [' ','\t','\r','\n','"']

# 用于将token转换为XML
# example: common_convert('keyword')('class') == '<keyword> class </keyword>'
def common_convert(type):
    def inner_helper(word):
        return "<{0}> {1} </{0}>".format(type,word)
    return inner_helper

def string_convert(word):
    return "<{0}> {1} </{0}>".format("stringConst",word[1:-1])

def common_empty_check(func):
    def inner_helper(word):
        if not word:
            return False
        return func(word)
    return inner_helper
