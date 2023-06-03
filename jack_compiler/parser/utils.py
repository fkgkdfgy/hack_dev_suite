class ParserException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

BuiltInKeywords=['class' , 'constructor' , 'function' ,
                 'method' , 'field' , 'static' , 'var' , 'int' , 
                 'char' , 'boolean' , 'void' , 'true' , 'false' , 
                 'null' , 'this' , 'let' , 'do' , 'if' , 'else' , 
                 'while' , 'return']

BuiltInSymbol = ['{' , '}' , '(' , ')' , '[' , ']' , '.' , ',' , ';' , '+' , '-' , '*' , 
                 '/' , '&' , ',' , '<' , '>' , '=' , '~','|']

SegmentSymbol = [' ','\t','\r','\n','"']

# 用于将token转换为XML
# example: common_convert('keyword')('class') == '<keyword> class </keyword>'
def common_convert(type):
    def inner_helper(word):
        return "<{0}> {1} </{0}>".format(type,word)
    return inner_helper

def string_convert(word):
    return "<{0}> {1} </{0}>".format("stringConstant",word[1:-1])

# 用于放入的最后一个参数检查是否为空
# 此处为了适配类的方法， 讲单一的word 修改为 *args，来传递类的本体
def common_empty_check(func):
    def inner_helper(*args):
        if not args[-1]:
            return False
        return func(*args)
    return inner_helper
