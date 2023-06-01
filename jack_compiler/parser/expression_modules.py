from utils import *
from base_modules import * 

class ExpressionException(Exception):
    pass

class VarNameHandler(NameHandler):
    label = 'varName'

class KeywordConstantHandler(SimpleHandler):
    isTerminal = True
    label = 'keywordConstant'

    def findTarget(self, unstructured_xml):
        if not unstructured_xml:
            return -1
        elif unstructured_xml[0][1] == 'keyword' and unstructured_xml[0][0] in ['true','false','null','this']:
            return 1
        else:
            return -1

class OpHandler(SimpleHandler):
    isTerminal = True
    label = 'op'

    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        elif unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['+','-','*','/','&','|','<','>','=']:
            return 1
        else:
            return -1

class ConstantHandler(SimpleHandler):
    isTerminal = True
    label = 'constant'
    
    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        elif unstructured_xml[0][1] in ['intConst','stringConst']:
            return 1
        else:
            return -1
        
class UnaryOpHandler(BaseHandler):
    isTerminal = True
    label = 'unaryOp'
    
    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        elif unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['~','-']:
            return 1
        else:
            return -1

class ExpressionHandler(SequenceHandler):
    isTerminal = False
    label = 'expression'

    def __init__(self, unstructed_xml=None):
        self.check_chain = [
            ('isMultiOpTerm', MultiUnitHandler(TermHandler(None),[OpHandler(None),TermHandler(None)]))
        ]
        self.valid_num = [1]
        super().__init__(unstructed_xml)

# wait for later TODO
class ExpressionListHandler(SelectHandler):
    isTerminal = False
    label = 'expressionList'

    def __init__(self, unstructed_xml=None):
        self.candidates = {
            'isEmpty': EmptyHandler(),
            'isMultiExpression': MultiUnitHandler(ExpressionHandler(),[SupportHandler((',' , 'symbol')),ExpressionHandler()])
        }
        super().__init__(unstructed_xml)

class PureFunctionCallHandler(SequenceHandler):
    isTerminal = True
    label = 'subroutineCall'

    def __init__(self, unstructed_xml=None):
        self.check_chain = [
            ('varName',VarNameHandler()),
            ('(',SupportHandler(('(', 'symbol'))),
            ('expressionList',ExpressionListHandler()),
            (')',SupportHandler((')', 'symbol')))
        ]
        self.valid_num = [4]
        super().__init__(unstructed_xml)

class ClassFunctionCallHandler(SequenceHandler):
    isTerminal = True
    label = 'subroutineCall'

    def __init__(self, unstructed_xml=None):
        self.check_chain = [
            ('varName',VarNameHandler()),
            ('.',SupportHandler(('.', 'symbol'))),
            ('varName',VarNameHandler()),
            ('(',SupportHandler(('(', 'symbol'))),
            ('expressionList',ExpressionListHandler()),
            (')',SupportHandler((')', 'symbol')))
        ]
        self.valid_num = [6]
        super().__init__(unstructed_xml)

class TermExpressionHandler(SequenceHandler):
    isTerminal = False
    label = 'term'

    def __init__(self, unstructed_xml=None):
        self.check_chain = [
            ('(',SupportHandler(('(', 'symbol'))),
            ('expression',ExpressionHandler()),
            (')',SupportHandler((')', 'symbol')))
        ]
        super().__init__(unstructed_xml)

class ArrayGetHandler(SequenceHandler):
    isTerminal = False
    label = 'term'

    def __init__(self, unstructed_xml=None):
        self.check_chain = [
            ('varName',VarNameHandler()),
            ('[',SupportHandler(('[', 'symbol'))),
            ('expression',ExpressionHandler()),
            (']',SupportHandler((']', 'symbol')))
        ]
        super().__init__(unstructed_xml)

class UnaryOpTermHandler(SequenceHandler):
    isTerminal = False
    label = 'term'

    def __init__(self, unstructed_xml=None):
        self.check_chain = [
            ('unaryOp',UnaryOpHandler()),
            ('term',TermHandler())
        ]
        super().__init__(unstructed_xml)

class TermHandler(SelectHandler):
    isTerminal = False
    label = 'term'

    def __init__(self, unstructured_xml):
        self.candidates = {
                'isConstant':  ConstantHandler(),
                'isName': VarNameHandler(),
                'isKeywordConstant': KeywordConstantHandler(),
                'isPureFunctionCall': PureFunctionCallHandler(),
                'isClassFunctionCall': ClassFunctionCallHandler(),
                'isExpression': TermExpressionHandler(),
                'isArrayGet': ArrayGetHandler(),
                'isUnaryOpTerm': UnaryOpHandler(),
        }

        BaseHandler.__init__(self, unstructured_xml)

