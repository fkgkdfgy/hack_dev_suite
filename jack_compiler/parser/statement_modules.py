from base_module import *
from expression_modules import *

class StatementException(Exception):
    pass

# 如果检测到一个就将find_flag置为True
# 如果有一个func 没有成功找到，就直接返回find_flag
# 所以返回的 find_flag 一定是一个长度为len(func_list)的list
# find_flag ::= [((True)*)?,((False)*)?]
def check_chain_with_func_list(left_xml, func_list):
    find_flag = [False] * len(func_list)
    if not func_list:
        raise StatementException('check_chain must have at least one function')
    for index,func in enumerate(func_list):
        find_length = func(left_xml)
        if find_length >=0:
            left_xml = left_xml[find_length:]
            find_flag[index] = True
        else:
            break
    return find_flag

# 主要用于帮助处理chain_check ,所以这个特殊的handler有一些奇怪的地方

class SupportHandler(BaseHandler):
    isTerminal = True
    label = 'support'

    def __init__(self, target_word_and_type):
        if not target_word_and_type or len(target_word_and_type) != 1:
            raise StatementException('SupportHandler must have one word and type')
        super().__init__(target_word_and_type)
        self.target_word_and_type = target_word_and_type

    def processXML(self, word_and_type):
        self.xml = common_convert(word_and_type[1])(word_and_type[0])

    def isTarget(self, word_and_type):
        # 如果进来的word_and_type 不是tuple 或者长度不满足要求 直接报错
        if not isinstance(word_and_type, tuple) or len(word_and_type) != 2:
            raise StatementException('SupportHandler.isTarget must have one word and type')
        if word_and_type == self.target_word_and_type:
            return True
        return False   
    
    def findTarget(self, unstructured_xml):
        if unstructured_xml and self.isTarget(unstructured_xml[0]):
            return 1
        return -1

class TemplateStatmentHandler(BaseHandler):

    def __init__(self, unstructed_xml=None):
        self.check_chain = {}
        self.valid_num = []
        super().__init__(unstructed_xml)

    def processXML(self, unstructured_xml):
        self.xml = ''
        if self.isTargetStatement(unstructured_xml):
            find_flag = check_chain_with_func_list(unstructured_xml, [ check_function for check_function,_ in self.check_chain.values()])
            for index,function_pair in enumerate(self.check_chain.values()):
                if find_flag[index]:
                    find_length = function_pair[0](unstructured_xml)
                    self.xml += function_pair[1](unstructured_xml[:find_length])
                    unstructured_xml = unstructured_xml[find_length:]
                else:
                    break
        else:
            raise StatementException('ifStatementHandler processXML must have a ifStatement')

    @common_empty_check
    def isTargetStatement(self,unstructured_xml):
        find_flag = check_chain_with_func_list(unstructured_xml, [ check_function for check_function,_ in self.check_chain.values()])
        # 如果 find_flag 中的 True 的个数不在 valid_num 中，返回 False
        if find_flag.count(True) not in self.valid_num:
            return False
        return True

    def findTargetStatement(self,unstructured_xml):
        find_flag = check_chain_with_func_list(unstructured_xml, [ check_function for check_function,_ in self.check_chain.values()])
        # 如果 find_flag 中的 True 的个数不在 valid_num 中，返回 False
        if find_flag.count(True) not in self.valid_num:
            return -1
        else:
            find_length = 0
            for index,function_pair in enumerate(self.check_chain.values()):
                if find_flag[index]:
                    check_function,_ = function_pair
                    find_length += check_function(unstructured_xml[find_length:])
                else:
                    break
            return find_length    

class LetStatementHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'letStatement'

    def __init__(self, unstructed_xml=None):
        self.check_chain = {
            'let': (SupportHandler(('let', 'keyword')).findTarget, lambda x: SupportHandler(('let', 'keyword')).toXML()),
            'varName': (VarNameHandler.isVarName, lambda x: VarNameHandler(x).toXML()),
            '=': (SupportHandler(('=', 'symbol')).findTarget, lambda x: SupportHandler(('=', 'symbol')).toXML()),
            'expression': (ExpressionHandler.isExpression, lambda x: ExpressionHandler(x).toXML()),
            ';': (SupportHandler((';', 'symbol')).findTarget, lambda x: SupportHandler((';', 'symbol')).toXML()),            
        }
        self.valid_num = [5]
        super().__init__(unstructed_xml)

class LetArrayStatementHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'letStatement'

    def __init__(self, unstructed_xml=None):
        self.check_chain = {
            'let': (SupportHandler(('let', 'keyword')).findTarget, lambda x: SupportHandler(('let', 'keyword')).toXML()),
            'varName': (VarNameHandler.isVarName, lambda x: VarNameHandler(x).toXML()),
            '[': (SupportHandler(('[', 'symbol')).findTarget, lambda x: SupportHandler(('[', 'symbol')).toXML()),
            'expression': (ExpressionHandler.isExpression, lambda x: ExpressionHandler(x).toXML()),
            ']': (SupportHandler((']', 'symbol')).findTarget, lambda x: SupportHandler((']', 'symbol')).toXML()),
            '=': (SupportHandler(('=', 'symbol')).findTarget, lambda x: SupportHandler(('=', 'symbol')).toXML()),
            'expression': (ExpressionHandler.isExpression, lambda x: ExpressionHandler(x).toXML()),
            ';': (SupportHandler((';', 'symbol')).findTarget, lambda x: SupportHandler((';', 'symbol')).toXML()),            
        }
        self.valid_num = [9]
        super().__init__(unstructed_xml)

class IfStatementHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'ifStatement'

    def __init__(self, unstructed_xml=None):
        self.check_chain = {
            'if': (SupportHandler(('if', 'keyword')).findTarget, lambda x: SupportHandler(('if', 'keyword')).toXML()),
            '(': (SupportHandler(('(', 'symbol')).findTarget, lambda x: SupportHandler(('(', 'symbol')).toXML()),
            'expression': (ExpressionHandler.isExpression, lambda x: ExpressionHandler(x).toXML()),
            ')': (SupportHandler((')', 'symbol')).findTarget, lambda x: SupportHandler((')', 'symbol')).toXML()),
            '{': (SupportHandler(('{', 'symbol')).findTarget, lambda x: SupportHandler(('{', 'symbol')).toXML()),
            'statements': (MultiStatementHandler.isMultiStatement, lambda x: MultiStatementHandler(x).toXML()),
            '}': (SupportHandler(('}', 'symbol')).findTarget, lambda x: SupportHandler(('}', 'symbol')).toXML()),
            'else': (SupportHandler(('else', 'keyword')).findTarget, lambda x: SupportHandler(('else', 'keyword')).toXML()),
            '{': (SupportHandler(('{', 'symbol')).findTarget, lambda x: SupportHandler(('{', 'symbol')).toXML()),
            'statements': (MultiStatementHandler.isMultiStatement, lambda x: MultiStatementHandler(x).toXML()),
            '}': (SupportHandler(('}', 'symbol')).findTarget, lambda x: SupportHandler(('}', 'symbol')).toXML())
        }
        self.valid_num = [7,11]
        super().__init__(unstructed_xml)

class WhileStatementHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'whileStatement'

    def __init__(self, unstructed_xml=None):
        self.check_chain = {
            'while': (SupportHandler(('while', 'keyword')).findTarget, lambda x: SupportHandler(('while', 'keyword')).toXML()),
            '(': (SupportHandler(('(', 'symbol')).findTarget, lambda x: SupportHandler(('(', 'symbol')).toXML()),
            'expression': (ExpressionHandler.isExpression, lambda x: ExpressionHandler(x).toXML()),
            ')': (SupportHandler((')', 'symbol')).findTarget, lambda x: SupportHandler((')', 'symbol')).toXML()),
            '{': (SupportHandler(('{', 'symbol')).findTarget, lambda x: SupportHandler(('{', 'symbol')).toXML()),
            'statements': (MultiStatementHandler.isMultiStatement, lambda x: MultiStatementHandler(x).toXML()),
            '}': (SupportHandler(('}', 'symbol')).findTarget, lambda x: SupportHandler(('}', 'symbol')).toXML())
        }
        self.valid_num = [7]
        super().__init__(unstructed_xml)

class DoStatementHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'doStatement'

    def __init__(self, unstructed_xml=None):
        self.check_chain = {
            'do':   (SupportHandler(('do', 'keyword')).findTarget, lambda x: SupportHandler(('do', 'keyword')).toXML()),
            'subroutineCall': (SubroutineCallHandler.isSubroutineCall, lambda x: SubroutineCallHandler(x).toXML()),
            ';': (SupportHandler((';', 'symbol')).findTarget, lambda x: SupportHandler((';', 'symbol')).toXML())
        }
        self.valid_num = [3]
        super().__init__(unstructed_xml)

class ReturnStatementHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'returnStatement'

    def __init__(self, unstructed_xml=None):
        self.check_chain = {
            'return': (SupportHandler(('return', 'keyword')).findTarget, lambda x: SupportHandler(('return', 'keyword')).toXML()),
            'expression': (ExpressionHandler.isExpression, lambda x: ExpressionHandler(x).toXML()),
            ';': (SupportHandler((';', 'symbol')).findTarget, lambda x: SupportHandler((';', 'symbol')).toXML())
        }
        self.valid_num = [3]
        super().__init__(unstructed_xml)

class VoidReturnStatementHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'voidReturnStatement'

    def __init__(self, unstructed_xml=None):
        self.check_chain = {
            'return': (SupportHandler(('return', 'keyword')).findTarget, lambda x: SupportHandler(('return', 'keyword')).toXML()),
            ';': (SupportHandler((';', 'symbol')).findTarget, lambda x: SupportHandler((';', 'symbol')).toXML())
        }
        self.valid_num = [2]
        super().__init__(unstructed_xml)

class StatementHandler(BaseHandler):    
    isTerminal = False
    label = 'statement'

    check_function = {
        'letStatement': (LetStatementHandler().isTargetStatement, lambda x: LetStatementHandler(x).toXML()),
        'letArrayStatement': (LetArrayStatementHandler().isTargetStatement, lambda x: LetArrayStatementHandler(x).toXML()),
        'ifStatement': (IfStatementHandler().isTargetStatement, lambda x: IfStatementHandler(x).toXML()),
        'whileStatement': (WhileStatementHandler().isTargetStatement, lambda x: WhileStatementHandler(x).toXML()),
        'doStatement': (DoStatementHandler().isTargetStatement, lambda x: DoStatementHandler(x).toXML()),
        'returnStatement': (ReturnStatementHandler().isTargetStatement, lambda x: ReturnStatementHandler(x).toXML()),
        'voidReturnStatement': (VoidReturnStatementHandler().isTargetStatement, lambda x: VoidReturnStatementHandler(x).toXML())
    }

    def processXML(self, unstructured_xml):
        if StatementHandler.isStatement(unstructured_xml):
            find_length = StatementHandler.findStatement(unstructured_xml)
            for check_function,transform_function in StatementHandler.check_function.values():
                if check_function(unstructured_xml[:find_length]):
                    self.xml = transform_function(unstructured_xml[:find_length])
                    return
        else:
            raise Exception('StatementHandler: not a statement')

    @common_empty_check
    def isStatement(unstructured_xml):
        for check_function,_ in StatementHandler.check_function.values():
            if check_function(unstructured_xml):
                return True
        return False
    
    def findStatement(unstructured_xml):
        for i in range(len(unstructured_xml)+1)[::-1]:
            if StatementHandler.isStatement(unstructured_xml[:i]):
                return i
        return -1
    
class MultiStatementHandler(BaseHandler):
    isTerminal = False
    label = 'statements'

    def processXML(self, unstructured_xml):
        if MultiStatementHandler.isMultiStatement(unstructured_xml):
            left_xml = unstructured_xml
            while left_xml:
                find_length = StatementHandler.findStatement(left_xml)
                self.xml += StatementHandler(left_xml[:find_length]).toXML()
                left_xml = left_xml[find_length:]
        else:
            raise Exception('MultiStatementHandler: not a multi statement')

    @common_empty_check
    def isMultiStatement(unstructured_xml):
        find_length = MultiStatementHandler.findMultiStatement(unstructured_xml)
        if find_length <0:
            return False
        if find_length == len(unstructured_xml):
            return True
        return MultiStatementHandler.isMultiStatement(unstructured_xml[find_length:])

    def findMultiStatement(unstructured_xml):
        if not unstructured_xml:
            return -1
        find_length = StatementHandler.findStatements(unstructured_xml)
        if find_length < 0:
            return -1
        else:
            next_find_length = MultiStatementHandler.findMultiStatement(unstructured_xml[find_length:])
            return (find_length) if next_find_length < 0 else (find_length + next_find_length)
    