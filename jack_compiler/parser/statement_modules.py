from base_modules import *
from expression_modules import *

class StatementException(Exception):
    pass

class MultiStatementHandler(SequenceHandler):
    isTerminal = False
    label = 'statements'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('multiStatments',MultiUnitHandler(None,[StatementHandler()]))
            ]
        return self._check_chain
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [1]
        return self._valid_num

class LetStatementHandler(SequenceHandler):
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

    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [5]
        return self._valid_num

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

    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [8]
        return self._valid_num

class IfStatementHandler(SequenceHandler):
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
                ('}',SupportHandler(('}', 'symbol'))),
                ('else',SupportHandler(('else', 'keyword'))),
                ('{',SupportHandler(('{', 'symbol'))),
                ('statements',MultiStatementHandler()),
                ('}',SupportHandler(('}', 'symbol')))
            ]
        return self._check_chain

    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [7,11]
        return self._valid_num

class WhileStatementHandler(SequenceHandler):
    isTerminal = False
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

    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [7]
        return self._valid_num

class SubroutineCallHandler(SelectHandler):
    isTerminal = True
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
    isTerminal = False
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
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [3]
        return self._valid_num

class ReturnStatementHandler(SequenceHandler):
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
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [3]
        return self._valid_num

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
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [2]
        return self._valid_num

class StatementHandler(SelectHandler):    
    isTerminal = True
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
    

