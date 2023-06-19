from base_modules import *
from expression_modules import *

class StatementException(Exception):
    pass

class MultiStatementHandler(MultiUnitHandler):
    isTerminal = True
    label = 'statements'

    empty_allowed = True
    
    def processXML(self, unstructured_xml):
        while unstructured_xml:
            if unstructured_xml[0][0] not in ['let','if','while','do','return']:
                return unstructured_xml
            try:
                statement_handler = StatementHandler()
                unstructured_xml = statement_handler.processXML(unstructured_xml)
                self.addChildren([statement_handler])
            except Exception as e:
                error_description = '\n'
                error_description += 'Deeper error: \n{}\n'.format(e)
                error_description += 'statement; ...; None-statement;\n'
                raise StatementException(error_description)      
        return unstructured_xml

    def toCode(self):
        result = ''
        for child in self.children:
            statement_code = child.toCode()
            print(statement_code)
            result += statement_code
        return result
    
class SimpleLetStatementHandler(SequenceHandler):
    isTerminal = False
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
    isTerminal = False
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

class LetStatementHandler(SelectHandler):
    isTerminal = True
    label = 'letStatement'

    @property
    def candidates(self):
        if not hasattr(self, '_candidates'):
            self._candidates = {
                'simpleLetStatement': SimpleLetStatementHandler(),
                'letArrayStatement': LetArrayStatementHandler()
            }
        return self._candidates

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
        if unstructured_xml and unstructured_xml[0][0] == 'else':
            try:
                unstructured_xml = pure_else_statement_handler.processXML(unstructured_xml)
                self.addChildren([pure_else_statement_handler])
            except Exception as e:
                xml_to_show = ' '.join([item[0] for item in unstructured_xml][0:10])
                error_description = '\n'
                error_description += 'Deeper error: \n{0} \n'.format(e)
                error_description += 'IfStatementHandler can not find pureElseStatement, When else is found\n'
                error_description += 'Unstructured_xml is: \n{0}\n'.format(xml_to_show)
                raise StatementException(error_description)
        return unstructured_xml
    
    def toCode(self):
        result = ''
        label1 = 'IF_TRUE' + str(IfStatementHandler.id)
        label2 = 'IF_FALSE' + str(IfStatementHandler.id)
        label3 = 'IF_END' + str(IfStatementHandler.id)
        IfStatementHandler.id += 1
        pure_if_statement = self.children[0]
        expression = pure_if_statement.children[2]
        result += expression.toCode()
        result += 'if-goto ' + label1 + '\n'
        result += 'goto ' + label2 + '\n'
        result += 'label '+label1 + '\n'
        statements = pure_if_statement.children[5]
        result += statements.toCode()
        result += 'goto ' + label3 + '\n'
        result += 'label '+label2 + '\n'
        if len(self.children) == 2:
            pure_else_statement = self.children[1]
            statements =  pure_else_statement.children[2]
            result += statements.toCode()
        result += 'label '+label3 + '\n'
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
        label1 = 'WHILE_EXP' + str(WhileStatementHandler.id)
        label2 = 'WHILE_END' + str(WhileStatementHandler.id)
        WhileStatementHandler.id += 1
        result += 'label '+ label1 + '\n'
        expression = self.children[2]
        result += expression.toCode()
        result += 'not\n'
        result += 'if-goto ' + label2 + '\n'
        statements = self.children[5]
        result += statements.toCode()
        result += 'goto ' + label1 + '\n'
        result += 'label '+label2 + '\n'
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
    isTerminal = False
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

class ActualReturnStatementHandler(SequenceHandler):
    isTerminal = False
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

class ReturnStatementHandler(SelectHandler):
    isTerminal = True
    label = 'returnStatement'

    @property
    def candidates(self):
        if not hasattr(self, '_candidates'):
            self._candidates = {
                'voidReturn': VoidReturnStatementHandler(),
                'actualReturn': ActualReturnStatementHandler()
            }
        return self._candidates

class StatementHandler(SelectHandler):    
    isTerminal = False
    label = 'statement'
    
    def processXML(self, unstructured_xml):
        if not unstructured_xml:
            raise StatementException('StatementHandler can not find any statement')
        if unstructured_xml[0][0] not in ['let','if','while','do','return']:
            raise StatementException('StatementHandler can not find any statement with the first word {0}'.format(unstructured_xml[0][0]))
        keyword_to_handler = {
            'let': LetStatementHandler(),
            'if': IfStatementHandler(),
            'while': WhileStatementHandler(),
            'do': DoStatementHandler(),
            'return': ReturnStatementHandler()
        }
        target_keyword = unstructured_xml[0][0]
        target_handler = keyword_to_handler[target_keyword]
        try:
            unstructured_xml = target_handler.processXML(unstructured_xml)
            self.selected_candidate = target_handler
        except Exception as e:
            error_description = '\n'
            error_description += 'Deeper error: \n{}\n'.format(e)
            error_description += 'statement; ...; None-statement;\n'
            raise StatementException(error_description)
        return unstructured_xml