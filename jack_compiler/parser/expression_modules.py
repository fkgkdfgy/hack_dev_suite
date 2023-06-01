from utils import *
from base_modules import * 

class ExpressionException(Exception):
    pass

class VarNameHandler(BaseHandler):
    isTerminal = True
    label = 'varName'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 varName，就直接转化成XML
        if VarNameHandler.isVarName(unstructured_xml):
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))

    # 如果能从unstructured_xml中提取出一个varName，就返回1，否则返回0
    @common_empty_check
    def isVarName(unstructured_xml):
        if len(unstructured_xml) == 1 and unstructured_xml[0][1] == 'identifier':
            return True
        return False
    
    def findVarName(unstructured_xml):
        if not unstructured_xml:
            return -1
        elif VarNameHandler.isVarName(unstructured_xml[0:1]):
            return 1
        else:
            return -1

class KeywordConstantHandler(BaseHandler):
    isTerminal = True
    label = 'keywordConstant'
    
    # process xml
    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 keywordConstant，就直接转化成XML
        find_length = KeywordConstantHandler.findKeyConstant(unstructured_xml)
        if find_length>=0:
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))
    
    # 判断unstructured_xml是否是keywordConstant
    @common_empty_check
    def isKeywordConstant(unstructured_xml):
        if len(unstructured_xml)==1 and unstructured_xml[0][1] == 'keyword' and unstructured_xml[0][0] in ['true','false','null','this']:
            return True
        return False

    # 寻找unstructured_xml中的最长满足条件的keywordConstant，返回其长度，如果找不到返回-1
    def findKeyConstant(unstructured_xml):
        if not unstructured_xml:
            return -1
        elif KeywordConstantHandler.isKeywordConstant(unstructured_xml[0:1]):
            return 1
        else:
            return -1

class OpHandler(BaseHandler):
    isTerminal = True
    label = 'op'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 op，就直接转化成XML
        if OpHandler.isOp(unstructured_xml):
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))
    
    def isOp(unstructured_xml):
        if not unstructured_xml:
            return False
        if len(unstructured_xml) == 1 and unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['+','-','*','/','&','|','<','>','=']:
            return True
        return False
    
    def findOp(unstructured_xml):
        if not unstructured_xml:
            return -1
        elif OpHandler.isOp(unstructured_xml[0:1]):
            return 1
        else:
            return -1

class ConstantHandler(BaseHandler):
    isTerminal = True
    label = 'constant'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 varName，就直接转化成XML
        if ConstantHandler.isConstant(unstructured_xml):
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))

    # 如果能从unstructured_xml中提取出一个varName，就返回1，否则返回0
    @common_empty_check
    def isConstant(unstructured_xml):
        if len(unstructured_xml) == 1 and unstructured_xml[0][1] in ['intConst','stringConst']:
            return True
        return False
    
    def findConstant(unstructured_xml):
        if not unstructured_xml:
            return -1
        elif ConstantHandler.isConstant(unstructured_xml[0:1]):
            return 1
        else:
            return -1
        
class UnaryOpHandler(BaseHandler):
    isTerminal = True
    label = 'unaryOp'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 unaryOp，就直接转化成XML
        if unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['~','-']:
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))

    # 如果能从unstructured_xml中提取出一个unaryOp，就返回1，否则返回0
    def isUnaryOp(unstructured_xml):
        if not unstructured_xml:
            return 0
        if unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['~','-']:
            return 1
        return 0
    
    def findUnaryOp(unstructured_xml):
        if not unstructured_xml:
            return -1
        elif UnaryOpHandler.isUnaryOp(unstructured_xml[0:1]):
            return 1
        else:
            return -1

class ExpressionListHandler(BaseHandler):
    isTerminal = False
    label = 'expressionList'

    def processXML(self, unstructured_xml):
        children= []

        def recursive_fill_children(unstructured_xml):
            if not unstructured_xml:
                return
            if ExpressionHandler.isExpression(unstructured_xml):
                children.append(ExpressionHandler(unstructured_xml))
                return
            find_length = ExpressionHandler.findExpression(unstructured_xml)
            if find_length != -1:
                children.append(ExpressionHandler(unstructured_xml[0:find_length]))
                children.append(PsedoHandler(unstructured_xml[find_length]))
                recursive_fill_children(unstructured_xml[find_length+1:])
            else:
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))

        if ExpressionListHandler.isExpressionList(unstructured_xml):
            recursive_fill_children(unstructured_xml)
            for child in children:
                self.xml += child.toXML()
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))

    # ExpressionList ::= (expression (',' expression)* )?
    def isExpressionList(unstructured_xml):
        if not unstructured_xml:
            return True
        if ExpressionHandler.isExpression(unstructured_xml):
            return True
        find_length = ExpressionHandler.findExpression(unstructured_xml)
        if find_length != -1:
            if unstructured_xml[find_length][1] == 'symbol' and unstructured_xml[find_length][0] == ',':
                return ExpressionListHandler.isExpressionList(unstructured_xml[find_length+1:])
        return False
    
    # 因为expressionList 可以为空，所以这个函数没有意义，所以在调用的时候，直接报错
    def findExpressionList(unstructured_xml):
        raise ExpressionException("this function should not be called")

class ExpressionHandler(BaseHandler):
    isTerminal = False
    label = 'expression'

    def __init__(self, unstructed_xml=None):
        super().__init__(unstructed_xml)

    def processXML(self, unstructured_xml):
        
        children = []
        def recursive_fill_children(xml_need_check):
            if not xml_need_check:
                return
            if TermHandler.isTerm(xml_need_check):
                children.append(TermHandler(xml_need_check))
                return
            else:
                find_length = TermHandler.findTerm(xml_need_check)
                if find_length >=0:
                    children.append(TermHandler(xml_need_check[:find_length]))
                    children.append(OpHandler(xml_need_check[find_length:find_length+1]))
                    recursive_fill_children(xml_need_check[find_length+1:])
                else:
                    raise ExpressionException("something wrong with {0}".format(unstructured_xml))            

        if ExpressionHandler.isExpression(unstructured_xml):
            recursive_fill_children(unstructured_xml)
            self.xml = ''
            for child in children:
                self.xml += child.toXML()   
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))   

    # Expression ::= Term (op Term)*
    def isExpression(unstructured_xml):
        if not unstructured_xml:
            return False
        if TermHandler.isTerm(unstructured_xml):
            return True
        find_length = TermHandler.findTerm(unstructured_xml)
        if find_length!=-1 and OpHandler.isOp(unstructured_xml[find_length:find_length+1]):
            return ExpressionHandler.isExpression(unstructured_xml[find_length+1:])
        return False
    
    def findExpression(unstructured_xml):
        if not unstructured_xml:
            return -1
        if TermHandler.isTerm(unstructured_xml):
            return len(unstructured_xml)
        find_length = TermHandler.findTerm(unstructured_xml)
        if find_length!=-1:
            if OpHandler.isOp(unstructured_xml[find_length:find_length+1]):
                return find_length + 1 + ExpressionHandler.findExpression(unstructured_xml[find_length+1:])
            return find_length
        return -1

@common_empty_check
def isPureFunctionCall(unstructured_xml):
    if VarNameHandler.isVarName(unstructured_xml[0:1])  \
        and unstructured_xml[1][0] == '(' \
        and unstructured_xml[-1][0] == ')' \
        and ExpressionListHandler.isExpressionList(unstructured_xml[2:-1]):
        return True
    return False

@common_empty_check
def isMemberFunctionCall(unstructured_xml):
    if VarNameHandler.isVarName(unstructured_xml[0:1])  \
        and unstructured_xml[1][0] == '.' \
        and VarNameHandler.isVarName(unstructured_xml[2:3]) \
        and unstructured_xml[3][0] == '(' \
        and unstructured_xml[-1][0] == ')' \
        and ExpressionListHandler.isExpressionList(unstructured_xml[4:-1]):
        return True
    return False

def transformPureFunctionCall(unstructured_xml):
    
    result_xml = VarNameHandler(unstructured_xml[0:1]).toXML()
    result_xml += common_convert('symbol')('(')
    result_xml += ExpressionListHandler(unstructured_xml[2:-1]).toXML()
    result_xml += common_convert('symbol')(')')
    return result_xml

def transformMemberFunctionCall(unstructured_xml):
    result_xml = VarNameHandler(unstructured_xml[0:1]).toXML()
    result_xml += common_convert('symbol')('.')
    result_xml += VarNameHandler(unstructured_xml[2:3]).toXML()
    result_xml += common_convert('symbol')('(')
    result_xml += ExpressionListHandler(unstructured_xml[4:-1]).toXML()
    result_xml += common_convert('symbol')(')')
    return result_xml

class SubroutineCallHandler(BaseHandler):
    isTerminal = True
    label = 'subroutineCall'

    check_function = {
            'isPureFunctionCall':  (isPureFunctionCall, lambda x: transformPureFunctionCall(x)),
            'isMemberFunctionCall': (isMemberFunctionCall, lambda x: transformMemberFunctionCall(x)),
        }

    def processXML(self, unstructured_xml):
        if not unstructured_xml:
            raise ExpressionException("unstructured_xml is empty")
        for check_function, convert_function in SubroutineCallHandler.check_function.values():
            if check_function(unstructured_xml):
                self.xml = convert_function(unstructured_xml)
                return
        raise ExpressionException("can't find a valid subroutineCall in {0}".format(unstructured_xml))

    def isSubroutineCall(unstructured_xml):
        if not unstructured_xml:
            return False
        for check_function,_ in SubroutineCallHandler.check_function.values():
            if check_function(unstructured_xml):
                return True
        return False
    
    def findSubroutineCall(unstructured_xml):
        if not unstructured_xml:
            return -1
        for i in range(len(unstructured_xml)+1)[::-1]:
            if SubroutineCallHandler.isSubroutineCall(unstructured_xml[0:i]):
                return i
        return -1

def transformUnaryOpTerm(unstructured_xml):
    result_xml = ''
    result_xml = UnaryOpHandler(unstructured_xml[0:1]).toXML()
    result_xml += TermHandler(unstructured_xml[1:]).toXML()
    return result_xml

def transformArrayGet(unstructured_xml):
    result_xml = ''
    result_xml = VarNameHandler(unstructured_xml[0:1]).toXML()
    result_xml += common_convert('symbol')(unstructured_xml[1][0])
    result_xml += ExpressionHandler(unstructured_xml[2:-1]).toXML()
    result_xml += common_convert('symbol')(unstructured_xml[-1][0])
    return result_xml

def transformExpression(unstructured_xml):
    result_xml = ''
    result_xml = common_convert('symbol')(unstructured_xml[0][0])
    result_xml += ExpressionHandler(unstructured_xml[1:-1]).toXML()
    result_xml += common_convert('symbol')(unstructured_xml[-1][0])
    return result_xml

@common_empty_check
def isUnaryOpTerm(unstructured_xml):
    if UnaryOpHandler.isUnaryOp(unstructured_xml[0:1]) and TermHandler.isTerm(unstructured_xml[1:]):
        return True
    return False

# 对应varName[expression]
@common_empty_check
def isArrayGet(unstructured_xml):
    if VarNameHandler.isVarName(unstructured_xml[0:1]) \
        and unstructured_xml[1][0] == '[' \
        and unstructured_xml[-1][0] == ']' \
        and ExpressionHandler.isExpression(unstructured_xml[2:-1]):
        return True
    return False

@common_empty_check
def isExpression(unstructured_xml):
    if unstructured_xml[0][0] == '(' and unstructured_xml[-1][0] == ')' and ExpressionHandler.isExpression(unstructured_xml[1:-1]):
        return True

class TermHandler(BaseHandler):
    isTerminal = False
    label = 'term'

    check_function = {
            'isConstant':  (ConstantHandler.isConstant, lambda x: ConstantHandler(x).toXML()),
            'isVarName': (VarNameHandler.isVarName, lambda x: VarNameHandler(x).toXML()),
            'isKeywordConstant': (KeywordConstantHandler.isKeywordConstant, lambda x: KeywordConstantHandler(x).toXML()),
            'isSubroutineCall': (SubroutineCallHandler.isSubroutineCall, lambda x: SubroutineCallHandler(x).toXML()),
            'isExpression': (isExpression, lambda x: transformExpression(x)),
            'isArrayGet': (isArrayGet, lambda x: transformArrayGet(x)),
            'isUnaryOpTerm': (isUnaryOpTerm, lambda x: transformUnaryOpTerm(x)),
        }

    def __init__(self, unstructured_xml):
        BaseHandler.__init__(self, unstructured_xml)

    def processXML(self, unstructured_xml):
        for check_function,transform_func in TermHandler.check_function.values():
            if check_function(unstructured_xml):
                self.xml = transform_func(unstructured_xml)
                return
        raise ExpressionException("something wrong with {0}".format(unstructured_xml))
    
    # 如果能从unstructured_xml中提取出一个Term，就返回第一个诊断是Term的end_index, 否则返回0
    def isTerm(unstructured_xml):
        for check_function,_ in TermHandler.check_function.values():
            if check_function(unstructured_xml):
                return True
        return False
    
    def findTerm(unstructured_xml):
        if not unstructured_xml:
            return -1
        for i in range(len(unstructured_xml)+1)[::-1]:
            if TermHandler.isTerm(unstructured_xml[0:i]):
                return i
        return -1    
    
