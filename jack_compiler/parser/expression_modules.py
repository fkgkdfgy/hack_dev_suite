from utils import *
from base_modules import * 

class ExpressionException(Exception):
    pass

class VarNameHandler(NameHandler):
    label = 'varName'

class KeywordConstantHandler(SimpleHandler):
    isTerminal = False
    label = 'keywordConstant'

    def findTarget(self, unstructured_xml):
        if not unstructured_xml:
            return -1
        elif unstructured_xml[0][1] == 'keyword' and unstructured_xml[0][0] in ['true','false','null','this']:
            return 1
        else:
            return -1

class OpHandler(SimpleHandler):
    isTerminal = False
    label = 'op'

    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        elif unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['+','-','*','/','&','|','<','>','=']:
            return 1
        else:
            return -1

class ConstantHandler(SimpleHandler):
    isTerminal = False
    label = 'constant'
    
    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        elif unstructured_xml[0][1] in ['integerConstant','stringConstant']:
            return 1
        else:
            return -1
        
class UnaryOpHandler(SimpleHandler):
    isTerminal = False
    label = 'unaryOp'
    
    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        elif unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['~','-']:
            return 1
        else:
            return -1

class ExpressionListHandler(MultiUnitHandler):
    isTerminal = True
    label = 'expressionList'
    
    empty_allowed = True

    @property
    def base_handler(self):
        if not hasattr(self, '_base_handler'):
            self._base_handler = ExpressionHandler()
        return self._base_handler
    
    @property
    def options_handlers(self):
        if not hasattr(self, '_options_handlers'):
            self._options_handlers = [SupportHandler((',', 'symbol')), ExpressionHandler()]
        return self._options_handlers


class ExpressionHandler(MultiUnitHandler):
    isTerminal = True
    label = 'expression'

    empty_allowed = False
    @property
    def base_handler(self):
        if not hasattr(self, '_base_handler'):
            self._base_handler = TermHandler()
        return self._base_handler
    
    @property
    def options_handlers(self):
        if not hasattr(self, '_options_handlers'):
            self._options_handlers = [OpHandler(), TermHandler()]
        return self._options_handlers

class PureFunctionCallHandler(SequenceHandler):
    isTerminal = False
    label = 'subroutineCall'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('varName',VarNameHandler()),
                ('(',SupportHandler(('(', 'symbol'))),
                ('expressionList',ExpressionListHandler()),
                (')',SupportHandler((')', 'symbol')))
            ]
        return self._check_chain
        
class ClassFunctionCallHandler(SequenceHandler):
    isTerminal = False
    label = 'subroutineCall'
    
    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('varName',VarNameHandler()),
                ('.',SupportHandler(('.', 'symbol'))),
                ('varName',VarNameHandler()),
                ('(',SupportHandler(('(', 'symbol'))),
                ('expressionList',ExpressionListHandler()),
                (')',SupportHandler((')', 'symbol')))
            ]
        return self._check_chain

class TermExpressionHandler(SequenceHandler):
    isTerminal = False
    label = 'term'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('(',SupportHandler(('(', 'symbol'))),
                ('expression',ExpressionHandler()),
                (')',SupportHandler((')', 'symbol')))
            ]
        return self._check_chain
    
class ArrayGetHandler(SequenceHandler):
    isTerminal = False
    label = 'term'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('varName',VarNameHandler()),
                ('[',SupportHandler(('[', 'symbol'))),
                ('expression',ExpressionHandler()),
                (']',SupportHandler((']', 'symbol')))
            ]
        return self._check_chain

class UnaryOpTermHandler(SequenceHandler):
    isTerminal = False
    label = 'term'

    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('unaryOp',UnaryOpHandler()),
                ('term',TermHandler())
            ]
        return self._check_chain
    
class TermHandler(SelectHandler):
    isTerminal = True
    label = 'term'

    @property
    def candidates(self):
        if not hasattr(self, '_candidates'):
            self._candidates = {
                'isPureFunctionCall': PureFunctionCallHandler(),
                'isClassFunctionCall': ClassFunctionCallHandler(),
                'isConstant':  ConstantHandler(),
                'isExpression': TermExpressionHandler(),
                'isUnaryOpTerm': UnaryOpTermHandler(),
                'isName': VarNameHandler(),
                'isKeywordConstant': KeywordConstantHandler(),
                'isArrayGet': ArrayGetHandler(),
            }
        return self._candidates

