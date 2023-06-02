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
        elif unstructured_xml[0][1] in ['intConst','stringConst']:
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

class ExpressionListHandler(SelectHandler):
    isTerminal = True
    label = 'expressionList'
    
    @property
    def candidates(self):
        if not hasattr(self, '_candidates'):
            self._candidates = {
                'isEmpty': EmptyHandler(),
                'isMultiExpression': MultiUnitHandler(ExpressionHandler(),[SupportHandler((',' , 'symbol')),ExpressionHandler()])
            }
        return self._candidates
    
    def findTarget(self, unstructured_xml):
        if not unstructured_xml:
            return 0
        return SelectHandler.findTarget(self, unstructured_xml)
    
class ExpressionHandler(SequenceHandler):
    isTerminal = True
    label = 'expression'
    
    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('isMultiOpTerm', MultiUnitHandler(TermHandler(None),[OpHandler(None),TermHandler(None)]))
            ]
        return self._check_chain
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [1]
        return self._valid_num

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
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [4]
        return self._valid_num

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
    
    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [6]
        return self._valid_num

class TermExpressionHandler(SequenceHandler):
    isTerminal = False
    label = 'term'

    @property
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [3]
        return self._valid_num
    
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
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [4]
        return self._valid_num
    
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
    def valid_num(self):
        if not hasattr(self, '_valid_num'):
            self._valid_num = [2]
        return self._valid_num
    
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
                'isConstant':  ConstantHandler(),
                'isName': VarNameHandler(),
                'isKeywordConstant': KeywordConstantHandler(),
                'isPureFunctionCall': PureFunctionCallHandler(),
                'isClassFunctionCall': ClassFunctionCallHandler(),
                'isExpression': TermExpressionHandler(),
                'isArrayGet': ArrayGetHandler(),
                'isUnaryOpTerm': UnaryOpTermHandler(),
            }
        return self._candidates

