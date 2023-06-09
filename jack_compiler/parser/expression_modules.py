from utils import *
from base_modules import * 

class ExpressionException(Exception):
    pass

class VarNameHandler(NameHandler):
    label = 'varName'

    def toCode(self):
        try:
            # description_of_variable ::= (attribute, type, index)
            description_of_variable = self.parent_handler.searchVariable(self.getWord())
        except:
            raise Exception('Variable {0} not defined'.format(self.getWord()))
        result = 'push {0} {1}\n'.format(description_of_variable[0], description_of_variable[2])
        return result

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
    
    def toCode(self):
        if self.getWord() == 'true':
            result = 'push constant 0\n'
            result += 'not\n'
        elif self.getWord() == 'false':
            result = 'push constant 0\n'
        elif self.getWord() == 'null':
            result = 'push constant 0\n'
        elif self.getWord() == 'this':
            result = 'push pointer 0\n'
        return result

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
    
    def toCode(self):
        if self.getWord() == '+':
            result = 'add\n'
        elif self.getWord() == '-':
            result = 'sub\n'
        elif self.getWord() == '*':
            result = 'call Math.multiply 2\n'
        elif self.getWord() == '/':
            result = 'call Math.divide 2\n'
        elif self.getWord() == '&':
            result = 'and\n'
        elif self.getWord() == '|':
            result = 'or\n'
        elif self.getWord() == '<':
            result = 'lt\n'
        elif self.getWord() == '>':
            result = 'gt\n'
        elif self.getWord() == '=':
            result = 'eq\n'
        return result
    
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
        
    def toCode(self):
        result = ''
        result += 'push constant {0}\n'.format(self.getWord())
        return result

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
    
    def toCode(self):
        if self.getWord() == '~':
            result = 'not\n'
        elif self.getWord() == '-':
            result = 'neg\n'
        return result

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
    
    def toCode(self):
        expression_handlers = [child for child in self.children if child.label == 'expression']
        result = ''
        for expression_handler in expression_handlers:
            result += expression_handler.toCode()
        return result
    
    def getExpressionSize(self):
        return len([child for child in self.children if child.label == 'expression'])

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
    
    def toCode(self):
        if len(self.children) == 0:
            raise Exception('Empty expression')
        if len(self.children) == 1:
            result = self.children[0].toCode()
        else:
            op_handlers = [child for child in self.children if child.label == 'op']
            term_handlers = [child for child in self.children if child.label == 'term']
            result = ''
            result += term_handlers[0].toCode()
            for i in range(len(op_handlers)):
                result += term_handlers[i+1].toCode()
                result += op_handlers[i].toCode()
        return result

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

    def toCode(self):
        try:
            class_name = self.searchVariable('this')[1]
        except Exception as e:
            raise Exception('Function {0} not defined, because can not find this'.format(self.children[0].getWord()))
        # 先压入this
        result = ''
        result += 'push pointer 0\n'
        # 再压入参数
        result += self.children[2].toCode()
        # 调用函数
        result += 'call {0}.{1} {2}\n'.format(class_name, self.children[0].getWord(), self.children[2].getExpressionSize()+1)
        return result

class ClassFunctionCallHandler(SequenceHandler):
    isTerminal = False
    label = 'subroutineCall'
    
    @property
    def check_chain(self):
        if not hasattr(self, '_check_chain'):
            self._check_chain = [
                ('varName',VarNameHandler()),
                ('.',SupportHandler(('.', 'symbol'))),
                ('subroutineName',VarNameHandler()),
                ('(',SupportHandler(('(', 'symbol'))),
                ('expressionList',ExpressionListHandler()),
                (')',SupportHandler((')', 'symbol')))
            ]
        return self._check_chain
    
    # varName.Subroutine() call can cover:
    # varName.memberSubroutine()
    # className.staticSubroutine()
    def toCode(self):
        # 获取对象
        result = ''
        var_name = self.children[0].getWord()
        try:
            # description_of_variable ::= (attribute, type, index)
            description_of_variable = self.parent_handler.searchVariable(var_name)
            result += 'push {0} {1}\n'.format(description_of_variable[0], description_of_variable[2])
            # 压入参数
            result += self.children[4].toCode()
            # 调用函数
            result += 'call {0}.{1} {2}\n'.format(description_of_variable[1], self.children[2].getWord(), self.children[4].getExpressionSize()+1)
        except:
            print('Variable {0} not defined, treat as a class'.format(var_name))
            # 压入参数
            result += self.children[4].toCode()
            # 调用函数
            result += 'call {0}.{1} {2}\n'.format(var_name, self.children[2].getWord(), self.children[4].getExpressionSize())
        return result

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
    
    def toCode(self):
        result = ''
        result += self.children[1].toCode()
        return result
    
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

    def toCode(self):
        # 给that赋值
        result += self.children[0].toCode()
        # 计算数组的地址
        result += self.children[2].toCode()
        # 获取地址
        result += 'add\n'
        result += 'pop pointer 1\n'
        # 获取值
        result += 'push that 0\n'
        return result

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
    
    def toCode(self):
        result = ''
        result += self.children[1].toCode()
        result += self.children[0].toCode()
        return result
    
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
    
    def toCode(self):
        result = ''
        result = self.selected_candidate.toCode()
        return result
