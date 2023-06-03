from base_modules import *
from expression_modules import *

class StatementException(Exception):
    pass

class MultiStatementHandler(SequenceHandler):
    isTerminal = True
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

    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [5]
        return self._valid_num

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

    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [8]
        return self._valid_num

class IfStatementHandler(SequenceHandler):
    isTerminal = True
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

    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [7]
        return self._valid_num
    
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
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [3]
        return self._valid_num

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
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [3]
        return self._valid_num

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
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [2]
        return self._valid_num

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
    
    def findTarget(self, unstructured_xml):
        next_statement_index = len(unstructured_xml)
        for word in unstructured_xml:
            if word[0] in ['if','while','do','return','let']:
                next_statement_index = unstructured_xml.index(word)
                break
        return SelectHandler.findTarget(self, unstructured_xml[:next_statement_index])
