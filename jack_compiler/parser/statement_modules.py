from base_modules import *
from expression_modules import *

class StatementException(Exception):
    pass

class MultiStatementHandler(SequenceHandler):
    isTerminal = True
    label = 'statements'

    def processXML(self, unstructured_xml):
        self.xml = ''
        statement_length = StatementHandler().findTarget(unstructured_xml)
        while statement_length > 0:
            self.xml += StatementHandler().processXML(unstructured_xml[:statement_length])
            unstructured_xml = unstructured_xml[statement_length:]
            statement_length = StatementHandler().findTarget(unstructured_xml)
        
        if not unstructured_xml:
            return self.toXML()
        raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

    def findTarget(self, unstructured_xml):
        origin_length = len(unstructured_xml)
        statement_length = StatementHandler().findTarget(unstructured_xml)
        while statement_length > 0:
            unstructured_xml = unstructured_xml[statement_length:]
            statement_length = StatementHandler().findTarget(unstructured_xml)
        return origin_length - len(unstructured_xml)

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

    def findTarget(self, unstructured_xml):
        try:
            try:
                last_semicolon_index = unstructured_xml.index((';', 'symbol'))
            except ValueError:
                return -1
            self.processXML(unstructured_xml[:last_semicolon_index+1])
        except StatementException:
            return -1
        return last_semicolon_index+1
    
    def processXML(self, unstructured_xml):
        self.xml = ''
        if SupportHandler(('let', 'keyword')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('keyword')('let')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if VarNameHandler().isTarget(unstructured_xml[0:1]):
            self.xml += VarNameHandler().processXML(unstructured_xml[0:1])
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler(('=', 'symbol')).isTarget(unstructured_xml[0:1]):
            self.xml += common_convert('symbol')('=')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if ExpressionHandler().isTarget(unstructured_xml[0:-1]):
            self.xml += ExpressionHandler().processXML(unstructured_xml[0:-1])
            unstructured_xml = unstructured_xml[-1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler((';', 'symbol')).isTarget(unstructured_xml[0:1]):
            self.xml += common_convert('symbol')(';')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

        if not unstructured_xml:
            return self.toXML()
        raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
    
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

    def findTarget(self, unstructured_xml):
        try:
            try:
                last_semicolon_index = unstructured_xml.index((';', 'symbol'))
            except ValueError:
                return -1
            self.processXML(unstructured_xml[:last_semicolon_index+1])
        except StatementException:
            return -1
        return last_semicolon_index+1
    
    def processXML(self, unstructured_xml):
        self.xml = ''
        if SupportHandler(('let', 'keyword')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('keyword')('let')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if VarNameHandler().isTarget(unstructured_xml[0:1]):
            self.xml += VarNameHandler().processXML(unstructured_xml[0:1])
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler(('[', 'symbol')).isTarget(unstructured_xml[0:1]):
            self.xml += common_convert('symbol')('[')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        # find ] symbol index
        try:
            last_right_bracket_index = unstructured_xml.index((']', 'symbol'))
        except ValueError:
            raise StatementException('the end token ] of let statement is missing')
        if ExpressionHandler().isTarget(unstructured_xml[:last_right_bracket_index]):
            self.xml += ExpressionHandler().processXML(unstructured_xml[:last_right_bracket_index])
            unstructured_xml = unstructured_xml[last_right_bracket_index:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler((']', 'symbol')).isTarget(unstructured_xml[0:1]):
            self.xml += common_convert('symbol')(']')
            unstructured_xml = unstructured_xml[1:]
        if SupportHandler(('=', 'symbol')).isTarget(unstructured_xml[0:1]):
            self.xml += common_convert('symbol')('=')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if ExpressionHandler().isTarget(unstructured_xml[0:-1]):
            self.xml += ExpressionHandler().processXML(unstructured_xml[0:-1])
            unstructured_xml = unstructured_xml[-1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml)) 
        if SupportHandler((';', 'symbol')).isTarget(unstructured_xml[0:1]):
            self.xml += common_convert('symbol')(';')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

        if not unstructured_xml:
            return self.toXML()
        raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

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
    
    def processXML(self, unstructured_xml):
        self.xml = ''
        if SupportHandler(('if', 'keyword')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('keyword')('if')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler(('(', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')('(')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        try:
            left_brace_index = unstructured_xml.index(('{', 'symbol'))
        except ValueError:
            raise StatementException('the start { is missing')
        if ExpressionHandler().isTarget(unstructured_xml[0:left_brace_index-1]):
            self.xml += ExpressionHandler().processXML(unstructured_xml[0:left_brace_index-1])
            unstructured_xml = unstructured_xml[left_brace_index-1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler((')', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')(')')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler(('{', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')('{')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        statements_length = MultiStatementHandler().findTarget(unstructured_xml)
        if statements_length >= 0:
            self.xml += MultiStatementHandler().processXML(unstructured_xml[:statements_length])
            unstructured_xml = unstructured_xml[statements_length:]
        if SupportHandler(('}', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')('}')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if not unstructured_xml:
            return self.toXML()
        if SupportHandler(('else', 'keyword')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('keyword')('else')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler(('{', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')('{')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        statements_length = MultiStatementHandler().findTarget(unstructured_xml)
        if statements_length >= 0:
            self.xml += MultiStatementHandler().processXML(unstructured_xml[:statements_length])
            unstructured_xml = unstructured_xml[statements_length:]
        if SupportHandler(('}', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')('}')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

        if not unstructured_xml:
            return self.toXML()
        raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))            
        
    def findTarget(self, unstructured_xml):
        origin_length = len(unstructured_xml)
        if not SupportHandler(('if', 'keyword')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        if not SupportHandler(('(', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        try:
            left_brace_index = unstructured_xml.index(('{', 'symbol'))
        except ValueError:
            return -1
        if not ExpressionHandler().isTarget(unstructured_xml[:left_brace_index-1]):
            return -1
        unstructured_xml = unstructured_xml[left_brace_index-1:]
        if not SupportHandler((')', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        if not SupportHandler(('{', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        statements_length = MultiStatementHandler().findTarget(unstructured_xml)
        if statements_length >= 0:
            unstructured_xml = unstructured_xml[statements_length:]
        if not SupportHandler(('}', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        if not SupportHandler(('else', 'keyword')).isTarget(unstructured_xml[:1]):
            return origin_length - len(unstructured_xml)
        unstructured_xml = unstructured_xml[1:]
        if not SupportHandler(('{', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        statements_length = MultiStatementHandler().findTarget(unstructured_xml)
        if statements_length >= 0:
            unstructured_xml = unstructured_xml[statements_length:]
        if not SupportHandler(('}', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        return origin_length - len(unstructured_xml)

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

    def processXML(self, unstructured_xml):
        self.xml = ''
        if SupportHandler(('while', 'keyword')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('keyword')('while')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler(('(', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')('(')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        try:
            left_brace_index = unstructured_xml.index(('{', 'symbol'))
        except ValueError:
            raise StatementException('the start { is missing')
        if ExpressionHandler().isTarget(unstructured_xml[0:left_brace_index-1]):
            self.xml += ExpressionHandler().processXML(unstructured_xml[0:left_brace_index-1])
            unstructured_xml = unstructured_xml[left_brace_index-1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler((')', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')(')')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler(('{', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')('{')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        statements_length = MultiStatementHandler().findTarget(unstructured_xml)
        if statements_length >= 0:
            self.xml += MultiStatementHandler().processXML(unstructured_xml[:statements_length])
            unstructured_xml = unstructured_xml[statements_length:]
        if SupportHandler(('}', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')('}')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

        if not unstructured_xml:
            return self.toXML()
        raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

    def findTarget(self, unstructured_xml):
        origin_length = len(unstructured_xml)
        if not SupportHandler(('while', 'keyword')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        if not SupportHandler(('(', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        try:
            left_brace_index = unstructured_xml.index(('{', 'symbol'))
        except ValueError:
            return -1
        if not ExpressionHandler().isTarget(unstructured_xml[:left_brace_index-1]):
            return -1
        unstructured_xml = unstructured_xml[left_brace_index-1:]
        if not SupportHandler((')', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        if not SupportHandler(('{', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        statements_length = MultiStatementHandler().findTarget(unstructured_xml)
        if statements_length >= 0:
            unstructured_xml = unstructured_xml[statements_length:]
        if not SupportHandler(('}', 'symbol')).isTarget(unstructured_xml[:1]):
            return -1
        unstructured_xml = unstructured_xml[1:]
        return origin_length - len(unstructured_xml)
        
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

    def findTarget(self, unstructured_xml):
        try:
            try:
                last_semicolon_index = unstructured_xml.index((';', 'symbol'))
            except ValueError:
                return -1
            self.processXML(unstructured_xml[:last_semicolon_index+1])
        except StatementException:
            return -1
        return last_semicolon_index+1
    
    def processXML(self, unstructured_xml):
        self.xml = ''
        if SupportHandler(('do', 'keyword')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('keyword')('do')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SubroutineCallHandler().isTarget(unstructured_xml[0:-1]):
            self.xml += SubroutineCallHandler().processXML(unstructured_xml[0:-1])
            unstructured_xml = unstructured_xml[-1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if SupportHandler((';', 'symbol')).isTarget(unstructured_xml[0:1]):
            self.xml += common_convert('symbol')(';')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

        if not unstructured_xml:
            return self.toXML()
        raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
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

    def processXML(self, unstructured_xml):
        self.xml = ''
        if SupportHandler(('return', 'keyword')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('keyword')('return')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))
        if ExpressionHandler().isTarget(unstructured_xml[0:-1]):
            self.xml += ExpressionHandler().processXML(unstructured_xml[0:-1])
            unstructured_xml = unstructured_xml[-1:]
        
        if SupportHandler((';', 'symbol')).isTarget(unstructured_xml[0:1]):
            self.xml += common_convert('symbol')(';')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

        if not unstructured_xml:
            return self.toXML()
        raise StatementException('Cannot parse the following tokens: {0}'.format(unstructured_xml))

    def findTarget(self, unstructured_xml):
        try:
            try:
                last_semicolon_index = unstructured_xml.index((';', 'symbol'))
            except ValueError:
                return -1
            self.processXML(unstructured_xml[:last_semicolon_index+1])
        except StatementException:
            return -1
        return last_semicolon_index+1

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
            }
        return self._candidates
    
    def findTarget(self, unstructured_xml):
        for candidate in self.candidates.values():
            find_length = candidate.findTarget(unstructured_xml)
            if find_length >0:
                return find_length
        return -1