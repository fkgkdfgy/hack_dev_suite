from base_modules import *
from expression_modules import *

class StatementException(Exception):
    pass

class MultiStatementHandler(MultiUnitHandler):
    isTerminal = True
    label = 'statements'

    empty_allowed = True

    @property
    def base_handler(self):
        if not hasattr(self, '_base_handler'):
            self._base_handler = StatementHandler()
        return self._base_handler
    @property
    def options_handlers(self):
        if not hasattr(self, '_options_handlers'):
            self._options_handlers = [StatementHandler()]
        return self._options_handlers

    def toCode(self):
        result = ''
        for child in self.children:
            statement_code = child.toCode()
            print(statement_code)
            result += statement_code
        return result
    
class LetStatementHandler(SequenceHandler):
    isTerminal = True
    label = 'letStatement'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('let',SupportHandler(('let', 'keyword'))),
                ('varName',VarNameHandler()),
                ('=',SupportHandler(('=', 'symbol'))),
                ('expression',ExpressionHandler()),
                (';',SupportHandler((';', 'symbol')))
            ]
        return self._check_chain
    
    def toCode(self):
        try: 
            result = ''
            var_tuple = self.searchVariable(self.children[1].getWord())
            expression = self.children[3]
            result += expression.toCode()
            result += 'pop ' + var_tuple[0] + ' ' + str(var_tuple[2]) + '\n'
            return result
        except:
            raise StatementException('LetStatementHandler can not find varName in {0}'.format(self.children[1].getWord()))

class LetArrayStatementHandler(SequenceHandler):
    isTerminal = True
    label = 'letStatement'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('let',SupportHandler(('let', 'keyword'))),
                ('varName',VarNameHandler()),
                ('[',SupportHandler(('[', 'symbol'))),
                ('expression',ExpressionHandler()),
                (']',SupportHandler((']', 'symbol'))),
                ('=',SupportHandler(('=', 'symbol'))),
                ('expression',ExpressionHandler()),
                (';',SupportHandler((';', 'symbol')))
            ]
        return self._check_chain
    
    def toCode(self):
        try:
            result = ''
            var_tuple = self.searchVariable(self.children[1].getWord())
            expression1 = self.children[3]
            expression2 = self.children[6]
            result += expression1.toCode()
            result += 'push ' + var_tuple[0] + ' ' + str(var_tuple[2]) + '\n'
            result += 'add\n'
            result += expression2.toCode()
            result += 'pop temp 0\n'
            result += 'pop pointer 1\n'
            result += 'push temp 0\n'
            result += 'pop that 0\n'
            return result
        except Exception as e:
            raise StatementException('LetArrayStatementHandler can not find varName in {0}'.format(self.children[1].getWord()))

class PureIfStatementHandler(SequenceHandler):
    isTerminal = False
    label = 'ifStatement'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('if',SupportHandler(('if', 'keyword'))),
                ('(',SupportHandler(('(', 'symbol'))),
                ('expression',ExpressionHandler()),
                (')',SupportHandler((')', 'symbol'))),
                ('{',SupportHandler(('{', 'symbol'))),
                ('statements',MultiStatementHandler()),
                ('}',SupportHandler(('}', 'symbol')))
            ]
        return self._check_chain

class PureElseStatementHandler(SequenceHandler):
    isTerminal = False
    label = 'elseStatement'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('else',SupportHandler(('else', 'keyword'))),
                ('{',SupportHandler(('{', 'symbol'))),
                ('statements',MultiStatementHandler()),
                ('}',SupportHandler(('}', 'symbol')))
            ]
        return self._check_chain
    
class IfStatementHandler(SequenceHandler):
    isTerminal = True
    label = 'ifStatement'
    id = 0

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('pureIfStatement',PureIfStatementHandler()),
                ('pureElseStatement',PureElseStatementHandler())
            ]
        return self._check_chain

    def processXML(self, unstructured_xml):
        self.children = []
        pure_if_statement_handler = copy.deepcopy(self.check_chain[0][1])
        try:
            unstructured_xml = pure_if_statement_handler.processXML(unstructured_xml)
            self.addChildren([pure_if_statement_handler])
        except Exception as e:
            raise StatementException('IfStatementHandler can not find pureIfStatement in {0}'.format(unstructured_xml))
        pure_else_statement_handler = copy.deepcopy(self.check_chain[1][1])
        try:
            unstructured_xml = pure_else_statement_handler.processXML(unstructured_xml)
            self.addChildren([pure_else_statement_handler])
        except Exception as e:
            pass
        return unstructured_xml
    
    def toCode(self):
        result = ''
        label1 = 'IF_TRUE' + str(self.id)
        label2 = 'IF_FALSE' + str(self.id)
        label3 = 'IF_END' + str(self.id)
        self.id += 1
        pure_if_statement = self.children[0]
        expression = pure_if_statement.children[2]
        result += expression.toCode()
        result += 'if-goto ' + label1 + '\n'
        result += 'goto ' + label2 + '\n'
        result += label1 + '\n'
        statements = pure_if_statement.children[5]
        result += statements.toCode()
        result += 'goto ' + label3 + '\n'
        result += label2 + '\n'
        if len(self.children) == 2:
            pure_else_statement = self.children[1]
            statements = pure_else_statement.children[2]
            result += statements.toCode()
        result += label3 + '\n'
        return result

class WhileStatementHandler(SequenceHandler):
    isTerminal = True
    label = 'whileStatement'
    id = 0

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('while',SupportHandler(('while', 'keyword'))),
                ('(',SupportHandler(('(', 'symbol'))),
                ('expression',ExpressionHandler()),
                (')',SupportHandler((')', 'symbol'))),
                ('{',SupportHandler(('{', 'symbol'))),
                ('statements',MultiStatementHandler()),
                ('}',SupportHandler(('}', 'symbol')))
            ]
        return self._check_chain
    
    def toCode(self):
        result = ''
        label1 = 'WHILE_EXP' + str(self.id)
        label2 = 'WHILE_END' + str(self.id)
        self.id += 1
        result += label1 + '\n'
        expression = self.children[2]
        result += expression.toCode()
        result += 'not\n'
        result += 'if-goto ' + label2 + '\n'
        statements = self.children[5]
        result += statements.toCode()
        result += 'goto ' + label1 + '\n'
        result += label2 + '\n'
        return result
        
class SubroutineCallHandler(SelectHandler):
    isTerminal = False
    label = 'subroutineCall'

    @property
    def candidates(self):
        if not hasattr(self, '_candidates'):
            self._candidates = {
                'pure': PureFunctionCallHandler(),
                'class': ClassFunctionCallHandler()
            }
        return self._candidates
    
class DoStatementHandler(SequenceHandler):
    isTerminal = True
    label = 'doStatement'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('do',SupportHandler(('do', 'keyword'))),
                ('subroutineCall',SubroutineCallHandler()),
                (';',SupportHandler((';', 'symbol')))
            ]
        return self._check_chain
    
    def toCode(self):
        result = ''
        subroutine_call = self.children[1]
        result += subroutine_call.toCode()
        result += 'pop temp 0\n'
        return result

class VoidReturnStatementHandler(SequenceHandler):
    isTerminal = True
    label = 'returnStatement'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('return',SupportHandler(('return', 'keyword'))),
                (';',SupportHandler((';', 'symbol')))
            ]
        return self._check_chain
    
    def toCode(self):
        result = ''
        result += 'push constant 0\n'
        result += 'return\n'
        return result

class ReturnStatementHandler(SequenceHandler):
    isTerminal = True
    label = 'returnStatement'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('return',SupportHandler(('return', 'keyword'))),
                ('expression',ExpressionHandler()),
                (';',SupportHandler((';', 'symbol')))
            ]
        return self._check_chain
    
    def toCode(self):
        result = ''
        expression = self.children[1]
        result += expression.toCode()
        result += 'return\n'
        return result

class StatementHandler(SelectHandler):    
    isTerminal = False
    label = 'statement'

    @property
    def candidates(self):
        if not hasattr(self, '_candidates'):
            self._candidates = {
                'letStatement': LetStatementHandler(),
                'letArrayStatement': LetArrayStatementHandler(),
                'ifStatement': IfStatementHandler(),
                'whileStatement': WhileStatementHandler(),
                'doStatement': DoStatementHandler(),
                'returnStatement': ReturnStatementHandler(),
                'voidReturnStatement': VoidReturnStatementHandler()
            }
        return self._candidates
    