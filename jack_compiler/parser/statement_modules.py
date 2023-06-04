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
            self.children.append(pure_if_statement_handler)
        except Exception as e:
            raise StatementException('IfStatementHandler can not find pureIfStatement in {0}'.format(unstructured_xml))
        pure_else_statement_handler = copy.deepcopy(self.check_chain[1][1])
        try:
            unstructured_xml = pure_else_statement_handler.processXML(unstructured_xml)
            self.children.append(pure_else_statement_handler)
        except Exception as e:
            pass
        return unstructured_xml

class WhileStatementHandler(SequenceHandler):
    isTerminal = True
    label = 'whileStatement'

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
    