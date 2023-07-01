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
        print(self.getWord())
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

class ValueException(Exception):
    pass

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
        if self.word_and_type[1] == 'integerConstant':
            result = 'push constant {0}\n'.format(self.word_and_type[0])
        else:
            # 给String.new传入参数
            result = 'push constant {0}\n'.format(len(self.word_and_type[0]))
            result += 'call String.new 1\n'
            for char in self.word_and_type[0]:
                result += 'push constant {0}\n'.format(ord(char))
                result += 'call String.appendChar 2\n'
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

    def processXML(self, unstructured_xml):
        try:
            expression_handler = ExpressionHandler()
            unstructured_xml = expression_handler.processXML(unstructured_xml)
            self.addChildren([expression_handler])
        except Exception as e:
            pass
        while unstructured_xml:
            origin_unstructured_xml = copy.deepcopy(unstructured_xml)
            try:
                comma_handler = SupportHandler((',', 'symbol'))
                unstructured_xml = comma_handler.processXML(unstructured_xml)
                self.addChildren([comma_handler])
            except Exception as e:
                unstructured_xml = origin_unstructured_xml
                break
            try:
                expression_handler = ExpressionHandler()
                unstructured_xml = expression_handler.processXML(unstructured_xml)
                self.addChildren([expression_handler])
            except Exception as e:
                error_description = '\n'
                error_description += 'Deeper Error({0}): \n{1}\n'.format(self.label,e)
                error_description += 'Expression , ... , Non-Expression\n'
                raise Exception(error_description)
        return unstructured_xml        

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

    def processXML(self, unstructured_xml):
        try:
            term_handler = TermHandler()
            unstructured_xml = term_handler.processXML(unstructured_xml)
            self.addChildren([term_handler])
        except Exception as e:
            xml_to_show = ' '.join([item[0] for item in unstructured_xml[:10]])
            raise Exception('can not find term in {0}'.format(xml_to_show))
        try:
            op_handler = OpHandler()
            unstructured_xml = op_handler.processXML(unstructured_xml)
            try:
                self.addChildren([op_handler])
                unstructured_xml = self.processXML(unstructured_xml)
            except Exception as e:
                error_description = '\n'
                error_description += 'Deeper Error({0}): \n{1}\n'.format(self.label,e)
                error_description += 'Term Op Non-Term\n'
                raise Exception(error_description)
        except Exception as e:
            pass
        return unstructured_xml
    
    def toCode(self):
        result = ''
        term_handlers = [child for child in self.children if child.label == 'term']
        op_handlers = [child for child in self.children if child.label == 'op']
        result += term_handlers[0].toCode()
        for term_handler, op_handler in zip(term_handlers[1:], op_handlers):
            result += term_handler.toCode()
            result += op_handler.toCode()
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
            description_of_variable = self.parent_handler.searchVariable(var_name)
            if description_of_variable[1] != 'class' :
                # 压入指针
                result += 'push {0} {1}\n'.format(description_of_variable[0], description_of_variable[2])
                # 压入参数
                result += self.children[4].toCode()
                # 调用函数
                result += 'call {0}.{1} {2}\n'.format(description_of_variable[1], self.children[2].getWord(), self.children[4].getExpressionSize()+1)
            else:
                print('Variable {0} not defined, treat as a class'.format(var_name))
                # 压入参数
                result += self.children[4].toCode()
                # 调用函数
                result += 'call {0}.{1} {2}\n'.format(var_name, self.children[2].getWord(), self.children[4].getExpressionSize())
        except Exception as e:
            print(e)
            print('the reason might be other file is not included into one file.')
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
        result = ''
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
    
    # TODO: 现在对于负数的判断只支持最简单的 -12 这种
    #       并不支持 -(((12))) 这种符合的判断
    def isNegative(self):
        if self.children[0].getWord() == '-' and \
            isinstance(self.children[1].selected_candidate, ConstantHandler) and \
            self.children[1].selected_candidate.getWordType() == 'integerConstant':
            return True
        else:
            return False
    
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
    
    def processXML(self, unstructured_xml):
        try:
            left_xml = SelectHandler.processXML(self, unstructured_xml)
            self.checkConstantValue()
            return left_xml
        except Exception as e:
            raise e

    def checkConstantValue(self):
        # 检查正数是否超过了32767
        if isinstance(self.selected_candidate, ConstantHandler) and \
            int(self.selected_candidate.getWord())>=32768:
            raise ValueException('constant value too large, positive number should be less than 32768')
        # 检查负数是否超过了-32768
        elif isinstance(self.selected_candidate, UnaryOpTermHandler) and \
            self.selected_candidate.isNegative():
            if int(self.selected_candidate.children[1].selected_candidate.getWord())>32768:
                raise ValueException('constant value too large, negative number should be less than -32768') 
            if int(self.selected_candidate.children[1].selected_candidate.getWord())==32768:
                tmp_unstructured_xml = [('~','symbol'),('32767','integerConstant')]
                tmp_selected_candidate = UnaryOpHandler()
                tmp_selected_candidate.processXML(tmp_unstructured_xml)
                self.selected_candidate = tmp_selected_candidate

    def toCode(self):
        result = ''
        result = self.selected_candidate.toCode()
        return result
