from base_module import *
from expression_modules import *

class StatementException(Exception):
    pass

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

    def processXML(self, unstructured_xml):
        if LetStatementHandler.isLetStatement(unstructured_xml):
            self.xml += StatementKeywordHandler(unstructured_xml[0]).toXML()
            self.xml += VarNameHandler(unstructured_xml[1:2]).toXML()
            self.xml += common_convert(unstructured_xml[2][1])(unstructured_xml[2][0])
            self.xml += ExpressionHandler(unstructured_xml[3:-1]).toXML()
            self.xml += common_convert(unstructured_xml[-1][1])(unstructured_xml[-1][0])
        else:
            raise StatementException('Not a valid letStatement: {0}'.format(unstructured_xml))

    # 如果要判断一个statement 是letStatement，那么必须要满足以下条件：
    # 1. 第一个word是let
    # 2. 第二个word是varName
    # 3. 第三个word是'='
    # 4. 第四个word是expression
    # 5. 第五个word是';'
    @common_empty_check
    def isLetStatement(unstructured_xml):
        if len(unstructured_xml) < 5:
            return False
        if unstructured_xml[0][0] == 'let' and \
            VarNameHandler.isvarName(unstructured_xml[1:2]) and \
            unstructured_xml[2][0] == '=' and \
            ExpressionHandler.isExpression(unstructured_xml[3:-1]) and \
            unstructured_xml[-1][0] == ';':
            return True
        return False
    
    def findletStatement(unstructured_xml):
        if not unstructured_xml:
            return -1
        for i in range(len(unstructured_xml)+1)[::-1]:
            if LetStatementHandler.isLetStatement(unstructured_xml[:i]):
                return i
        return -1

class ifStatementHandler(BaseHandler):
    isTerminal = False
    label = 'ifStatement'

    def processXML(self, unstructured_xml):
        if ifStatementHandler.isifStatement(unstructured_xml):
            self.xml += StatementKeywordHandler(unstructured_xml[0]).toXML()
            self.xml += common_convert(unstructured_xml[1][1])(unstructured_xml[1][0])
            self.xml += ExpressionHandler(unstructured_xml[2:-2]).toXML()
            self.xml += common_convert(unstructured_xml[-2][1])(unstructured_xml[-2][0])
            self.xml += StatementHandler(unstructured_xml[-1]).toXML()
        else:
            raise StatementException('Not a valid ifStatement: {0}'.format(unstructured_xml))

    # 如果要判断一个statement 是ifStatement，那么必须要满足以下条件：
    # 1. 第一个word是if
    # 2. 第二个word是'('
    # 3. 第三个word是expression
    # 4. 第四个word是')'
    # 5. 第五个word是'{'
    # 6. 第六个word是statements
    # 7. 第七个word是'}'
    @common_empty_check
    def isifStatement(unstructured_xml):
        if len(unstructured_xml) < 7:
            return False
        if unstructured_xml[0][0] == 'if' and \
            unstructured_xml[1][0] == '(' and \
            ExpressionHandler.isExpression(unstructured_xml[2:-2]) and \
            unstructured_xml[-2][0] == ')' and \
            unstructured_xml[-1][0] == '{' and \
            StatementHandler.isStatement(unstructured_xml[-1][1:-1]) and \
            unstructured_xml[-1][-1][0] == '}':
            return True
        return False
    
    def findifStatement(unstructured_xml):
        if not unstructured_xml:
            return -1
        for i in range(len(unstructured_xml)+1)[::-1]:
            if ifStatementHandler.isifStatement(unstructured_xml[:i]):
                return i
        return -1


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