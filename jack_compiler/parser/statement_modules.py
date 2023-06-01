from base_module import *
from expression_modules import *

class StatementException(Exception):
    pass

def check_chain(left_xml, func_list):
    if not func_list:
        raise StatementException('check_chain must have at least one function')
    for func in func_list:
        find_length = func(left_xml)
        if find_length >=0:
            left_xml = left_xml[find_length:]
        else:
            break
    if not left_xml:
        return True
    return False

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

class StatementKeywordHandler(BaseHandler):
    isTerminal = True
    label = 'statementkeyword'
    def processXML(self, word_and_type):
        self.xml = common_convert(word_and_type[1])(word_and_type[0])

    @common_empty_check
    def isStatementKeyword(unstructured_xml):
        if unstructured_xml[0][1] == 'keyword' and unstructured_xml[0][0].text in ['let', 'if', 'while', 'do', 'return']:
            return True
        return False
    
class LetStatementHandler(BaseHandler):
    isTerminal = False
    label = 'letStatement'

    check_chain = {
        'let': (SupportHandler(('let', 'keyword')).findTarget, lambda x: SupportHandler(('let', 'keyword')).toXML()),
        'varName': (VarNameHandler.isVarName, lambda x: VarNameHandler(x).toXML()),
        '=': (SupportHandler(('=', 'symbol')).findTarget, lambda x: SupportHandler(('=', 'symbol')).toXML()),
        'expression': (ExpressionHandler.isExpression, lambda x: ExpressionHandler(x).toXML()),
        ';': (SupportHandler((';', 'symbol')).findTarget, lambda x: SupportHandler((';', 'symbol')).toXML())
    }

    def processXML(self, unstructured_xml):
        self.xml = ''
        for check_name, (check_function, convert_function) in LetStatementHandler.check_chain.items():
            find_length = check_function(unstructured_xml)
            if find_length >= 0:
                self.xml += convert_function(unstructured_xml[:find_length])
                unstructured_xml = unstructured_xml[find_length:]
            else:
                raise StatementException('LetStatementHandler.processXML error: {0} not found'.format(check_name))

    @common_empty_check
    def isLetStatement(unstructured_xml):
        return check_chain(unstructured_xml,[ check_function for check_function,_ in LetStatementHandler.check_chain.values()])

    def findletStatement(unstructured_xml):
        pass

class ifStatementHandler(BaseHandler):
    isTerminal = False
    label = 'ifStatement'

    def processXML(self, unstructured_xml):
        pass

    @common_empty_check
    def isifStatement(unstructured_xml):
        pass

    def findifStatement(unstructured_xml):
        pass


class StatementHandler(BaseHandler):    
    isTerminal = False
    label = 'statement'

    check_function = {
        'letStatement': ()
    }

    def processXML(self, unstructured_xml):
        self.xml = ''
        for statement in unstructured_xml:
            statement_type = statement[0].text
            if statement_type == 'letStatement':
                self.xml += LetHandler(statement).toXML()
            elif statement_type == 'ifStatement':
                self.xml += IfHandler(statement).toXML()
            elif statement_type == 'whileStatement':
                self.xml += WhileHandler(statement).toXML()
            elif statement_type == 'doStatement':
                self.xml += DoHandler(statement).toXML()
            elif statement_type == 'returnStatement':
                self.xml += ReturnHandler(statement).toXML()
            else:
                raise StatementException('Unknown statement type: {0}'.format(statement_type))
            
class MultiStatementHandler(BaseHandler):
    isTerminal = False
    label = 'statements'

    def processXML(self, unstructured_xml):
        pass

    @common_empty_check
    def isMultiStatement(unstructured_xml):
        pass

    def findMultiStatement(unstructured_xml):
        pass