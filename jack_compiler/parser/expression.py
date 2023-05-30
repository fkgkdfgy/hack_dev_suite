
from base import *
from utils import *

class ExpressionException(Exception):
    pass

class KeywordConstantHandler(BaseHandler):
    isTerminal = True
    label = 'keywordConstant'
    
    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 keywordConstant，就直接转化成XML
        if unstructured_xml[0][1] == 'keyword' and unstructured_xml[0][0] in ['true','false','null','this']:
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])+"\n"
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))
    
    # 如果能从unstructured_xml中提取出一个keywordConstant，就返回1，否则返回-1
    def isKeywordConstant(unstructured_xml):
        if unstructured_xml[0][1] == 'keyword' and unstructured_xml[0][0] in ['true','false','null','this']:
            return 1
        return -1

class UnaryOpHandler(BaseHandler):
    isTerminal = True
    label = 'unaryOp'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 unaryOp，就直接转化成XML
        if unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['~','-']:
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])+"\n"
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))

    # 如果能从unstructured_xml中提取出一个unaryOp，就返回1，否则返回-1
    def isUnaryOp(unstructured_xml):
        if unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['~','-']:
            return 1
        return -1

class OpHandler(BaseHandler):
    isTerminal = True
    label = 'op'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 op，就直接转化成XML
        if unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['+','-','*','/','&','|','<','>','=']:
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])+'\n'
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))

    def isOp(unstructured_xml):
        if unstructured_xml[0][1] == 'symbol' and unstructured_xml[0][0] in ['+','-','*','/','&','|','<','>','=']:
            return 1
        return -1

class VarNameHandler(BaseHandler):
    isTerminal = True
    label = 'varName'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 varName，就直接转化成XML
        if unstructured_xml[0][1] == 'identifier':
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])
        else:
            raise ExpressionException("something wrong with {0}".format(unstructured_xml))

    # 如果能从unstructured_xml中提取出一个varName，就返回1，否则返回-1
    def isVarName(unstructured_xml):
        if unstructured_xml[0][1] == 'identifier':
            return 1
        return -1
    

class SubroutineCallHandler(BaseHandler):
    isTerminal = True
    label = 'subroutineCall'
    def processXML(self, unstructured_xml):
        # 1. 处理 subroutineName ( expressionList )
        if VarNameHandler.isVarName(unstructured_xml[0:1]) and unstructured_xml[1][0] == '(' and unstructured_xml[-1][0] == ')':
            self.xml = VarNameHandler(unstructured_xml[0:1]).toXML()
            self.xml += common_convert('symbol')('(') +"\n"
            if not ExpressionListHandler.isExpressionList(unstructured_xml[2:-1]):
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))
            self.xml += ExpressionListHandler(unstructured_xml[2:-1]).toXML()
            self.xml += common_convert('symbol')(')')+ "\n"
        # 2. 处理 className . subroutineName ( expressionList )
        elif VarNameHandler.isVarName(unstructured_xml[0:1]) and unstructured_xml[1][0] == '.' and VarNameHandler.isVarName(unstructured_xml[2:3]) and unstructured_xml[3][0] == '(' and unstructured_xml[-1][0] == ')':
            self.xml = VarNameHandler(unstructured_xml[0:1]).toXML()
            self.xml += common_convert('symbol')('.') +"\n"
            self.xml += VarNameHandler(unstructured_xml[2:3]).toXML()
            self.xml += common_convert('symbol')('(') +"\n"
            if not ExpressionListHandler.isExpressionList(unstructured_xml[4:-1]):
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))
            self.xml += ExpressionListHandler(unstructured_xml[4:-1]).toXML()
            self.xml += common_convert('symbol')(')')+ "\n"

    def isSubroutineCall(unstructured_xml):
        # 1. 处理 subroutineName ( expressionList )
        if VarNameHandler.isVarName(unstructured_xml[0:1]) \
            and unstructured_xml[1][0] == '(':
            expressionList_end_index = ExpressionListHandler.isExpressionList(unstructured_xml[2:])
            if expressionList_end_index == -1 or unstructured_xml[expressionList_end_index+2][0] != ')':
                return -1
            return expressionList_end_index+3
        # 2. 处理 className . subroutineName ( expressionList )
        elif VarNameHandler.isVarName(unstructured_xml[0:1]) \
            and unstructured_xml[1][0] == '.' \
            and VarNameHandler.isVarName(unstructured_xml[2:3]) \
            and unstructured_xml[3][0] == '(':
            expressionList_end_index = ExpressionListHandler.isExpressionList(unstructured_xml[4:])
            if expressionList_end_index == -1 or unstructured_xml[expressionList_end_index+4][0] != ')':
                return -1
            return expressionList_end_index+5
        return -1

class TermHandler(BaseHandler):
    isTerminal = False
    label = 'term'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 intConst | stringConst ，就直接转化成XML
        if unstructured_xml[0][1] in ['intConst','stringConst']:
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])
        # 2. 如果unstructured_xml 长度是1，且是 varName，就直接转化成XML
        elif VarNameHandler.isVarName(unstructured_xml):
            self.xml = VarNameHandler(unstructured_xml).toXML()
        elif KeywordConstantHandler.isKeywordConstant(unstructured_xml):
            self.xml = KeywordConstantHandler(unstructured_xml).toXML()
        # 3. 如果第一个字符是一元运算符，并且后面是一个term，就转化成XML
        elif UnaryOpHandler.isUnaryOp(unstructured_xml[0:1]):
            self.xml = UnaryOpHandler(unstructured_xml[0:1]).toXML()
            if len(unstructured_xml) != 2 and not TermHandler.isTerm(unstructured_xml[1:]):
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))
            self.xml += TermHandler(unstructured_xml[1:]).toXML()
        # 4. 如果第一个字符是 ( ，并且后面是一个expression，最后一个字符是 ) ，就转化成XML
        elif unstructured_xml[0][0] == '(' and unstructured_xml[-1][0] == ')':
            self.xml = common_convert('symbol')(unstructured_xml[0][0])
            if not ExpressionHandler.isExpression(unstructured_xml[1:-1]):
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))
            self.xml += ExpressionHandler(unstructured_xml[1:-1]).toXML()
            self.xml += common_convert('symbol')(unstructured_xml[-1][0])
        # 5. 如果第一个字符是 varName, 并且后面是 [ ，并且后面是一个expression，最后一个字符是 ] ，就转化成XML
        elif VarNameHandler.isVarName(unstructured_xml[0]) and unstructured_xml[1][0] == '[' and unstructured_xml[-1][0] == ']':
            self.xml = VarNameHandler(unstructured_xml[0]).toXML()
            self.xml += common_convert('symbol')(unstructured_xml[1][0])
            if not ExpressionHandler.isExpression(unstructured_xml[2:-1]):
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))
            self.xml += ExpressionHandler(unstructured_xml[2:-1]).toXML()
            self.xml += common_convert('symbol')(unstructured_xml[-1][0])
        # 6. 如果检查到是一个subroutineCall，就转化成XML
        elif SubroutineCallHandler.isSubroutineCall(unstructured_xml):
            self.xml = SubroutineCallHandler(unstructured_xml).toXML()

    # 如果能从unstructured_xml中提取出一个Term，就返回第一个诊断是Term的end_index, 否则返回-1
    def isTerm(unstructured_xml):
        if unstructured_xml[0][1] in ['intConst','stringConst','keyword']:
            return 1
        elif VarNameHandler.isVarName(unstructured_xml):
            return 1
        elif unstructured_xml[0][0] in ['~','-']:
            if len(unstructured_xml) != 2 and not TermHandler.isTerm(unstructured_xml[1:]):
                return -1
            return 1
        elif unstructured_xml[0][0] == '(':
            expression_end_index = ExpressionHandler.isExpression(unstructured_xml[1:])
            if expression_end_index == -1 or unstructured_xml[expression_end_index+1][0] != ')':
                return -1
            return expression_end_index+2
        elif VarNameHandler.isVarName(unstructured_xml[0]) and unstructured_xml[1][0] == '[' and unstructured_xml[-1][0] == ']':
            expression_end_index = ExpressionHandler.isExpression(unstructured_xml[2:-1])
            if expression_end_index == -1 or unstructured_xml[expression_end_index+2][0] != ']':
                return -1
            return expression_end_index+3
        elif SubroutineCallHandler.isSubroutineCall(unstructured_xml):
            return SubroutineCallHandler.isSubroutineCall(unstructured_xml)
        return -1
        
class ExpressionListHandler(BaseHandler):
    isTerminal = False
    label = 'expressionList'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 expression，就直接转化成XML
        if ExpressionHandler.isExpression(unstructured_xml):
            self.xml = ExpressionHandler(unstructured_xml).toXML()
        # 2. 如果unstructured_xml 长度大于1，且是 expression，就直接转化成XML
        elif ExpressionHandler.isExpression(unstructured_xml[0:1]):
            self.xml = ExpressionHandler(unstructured_xml[0:1]).toXML()
            self.xml += common_convert('symbol')(',') + "\n"
            if not ExpressionListHandler.isExpressionList(unstructured_xml[2:]):
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))
            self.xml += ExpressionListHandler(unstructured_xml[2:]).toXML()
        # 3. 如果unstructured_xml 长度大于1，且是 expression，就直接转化成XML
        elif ExpressionHandler.isExpression(unstructured_xml[0:1]):
            self.xml = ExpressionHandler(unstructured_xml[0:1]).toXML()
            self.xml += common_convert('symbol')(',') + "\n"
            if not ExpressionListHandler.isExpressionList(unstructured_xml[2:]):
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))
            self.xml += ExpressionListHandler(unstructured_xml[2:]).toXML()

    def isExpressionList(unstructured_xml):
        end_index = 0

        # 按照 Expression (, Expression)* 的顺序检查，如果就累加到end_index
        def seqence_check(xml_need_check):
            nonlocal end_index
            tmp_end_index = 0
            expression_end_index = ExpressionHandler.isExpression(xml_need_check)
            if expression_end_index != -1:
                expression_end_index += expression_end_index
                end_index += expression_end_index
                if xml_need_check[expression_end_index][0] == ',':
                    end_index += 1
                    tmp_end_index  += 1
                    seqence_check(xml_need_check[tmp_end_index:])
            else:
                return
        
        seqence_check(unstructured_xml)
        if end_index == 0:
            return -1
        return end_index

class ExpressionHandler(BaseHandler):
    isTerminal = True
    label = 'expression'

    def processXML(self, unstructured_xml):
        # 1. 如果unstructured_xml 长度是1，且是 term，就直接转化成XML
        if TermHandler.isTerm(unstructured_xml):
            self.xml = TermHandler(unstructured_xml).toXML()
        # 2. 如果unstructured_xml 长度大于1，可能是 term 

    # 如果能从unstructured_xml中提取出一个expression，就返回第一个诊断是expression的end_index, 否则返回-1
    def isExpression(unstructured_xml):
        end_index = 0

        # 按照 Term op Term op Term ... 的顺序检查，如果就累加到end_index
        def seqence_check(xml_need_check):
            nonlocal end_index
            tmp_end_index = 0
            term_end_index = TermHandler.isTerm(xml_need_check)
            if term_end_index != -1:
                term_end_index += term_end_index
                end_index += term_end_index
                if OpHandler.isOp(xml_need_check[term_end_index:]):
                    end_index += 1
                    tmp_end_index  += 1
                    seqence_check(xml_need_check[tmp_end_index:])
            else:
                return

        seqence_check(unstructured_xml)
        
        if end_index == 0:
            return -1
        return end_index

if __name__ == "__main__":

    def handler_test(handler,unstructured_xml,answer_xml):
        handler.processXML(unstructured_xml)
        print(handler.toXML())
        assert handler.toXML() == answer_xml

    # 1. 单元测试: KeywordConstantHandler
    # 1.1 单元测试: KeywordConstantHandler.isKeywordConstant
    unstructured_xml = [('true','keyword')]
    assert KeywordConstantHandler.isKeywordConstant(unstructured_xml) == 1
    # 1.2 单元测试: KeywordConstantHandler.processXML
    unstructured_xml = [('true','keyword')]
    handler_test(KeywordConstantHandler(),unstructured_xml,'<keyword> true </keyword>\n')
    # 2. 单元测试: UnaryOpHandler
    # 2.1 单元测试: UnaryOpHandler.isUnaryOp
    unstructured_xml = [('~','symbol')]
    assert UnaryOpHandler.isUnaryOp(unstructured_xml) == 1
    # 2.2 单元测试: UnaryOpHandler.processXML
    unstructured_xml = [('~','symbol')]
    handler_test(UnaryOpHandler(),unstructured_xml,'<symbol> ~ </symbol>\n')
    # 3. 单元测试: OpHandler
    # 3.1 单元测试: OpHandler.isOp
    unstructured_xml = [('+','symbol')]
    assert OpHandler.isOp(unstructured_xml) == 1
    # 3.2 单元测试: OpHandler.processXML
    unstructured_xml = [('+','symbol')]
    handler_test(OpHandler(),unstructured_xml,'<symbol> + </symbol>\n')
    # 4. 单元测试: VarNameHandler
    # 4.1 单元测试: VarNameHandler.isVarName
    unstructured_xml = [('varName_1','identifier')]
    assert VarNameHandler.isVarName(unstructured_xml) == 1
    # 4.2 单元测试: VarNameHandler.processXML
    unstructured_xml = [('varName_1','identifier')]
    handler_test(VarNameHandler(),unstructured_xml,'<identifier> varName </identifier>')
    # 5. 单元测试: SubroutineCallHandler
    # 5.1 单元测试: SubroutineCallHandler.isSubroutineCall
    # 5.1.1 单元测试: SubroutineCallHandler.isSubroutineCall: subroutineName ( expressionList )
    unstructured_xml = [('varName_1','identifier'),('(','symbol'),(')','symbol')]
    assert SubroutineCallHandler.isSubroutineCall(unstructured_xml) == 3
    unstructured_xml = [('varName_1','identifier'),('(','symbol'),('expression_1','intConst'),(')','symbol')]
    assert SubroutineCallHandler.isSubroutineCall(unstructured_xml) == 5
    unstructured_xml = [('varName_1','identifier'),('(','symbol'),('expression_1','intConst'),('expression_2','intConst'),(')','symbol')]
    assert SubroutineCallHandler.isSubroutineCall(unstructured_xml) == 7
    # 5.1.2 单元测试: SubroutineCallHandler.isSubroutineCall: className . subroutineName ( expressionList )
    unstructured_xml = [('varName_1','identifier'),('.','symbol'),('varName_2','identifier'),('(','symbol'),(')','symbol')]
    assert SubroutineCallHandler.isSubroutineCall(unstructured_xml) == 5
    # 5.1.3 单元测试: SubroutineCallHandler.isSubroutineCall: Sys.Main(5,"print something")
    unstructured_xml = [('Sys','identifier'),('.','symbol'),('Main','identifier'),('(','symbol'),('5','intConst'),('print something','stringConst'),(')','symbol')]
    assert SubroutineCallHandler.isSubroutineCall(unstructured_xml) == 9
    # 5.1.4 单元测试: SubroutineCallHandler.isSubroutineCall: Sys.Main(5,"prompt",(a+b+(5)))
    unstructured_xml = [('Sys','identifier'),('.','symbol'),('Main','identifier'),('(','symbol'),('5','intConst'),('prompt','stringConst'),('(','symbol'),('(','symbol'),('a','identifier'),('+','symbol'),('b','identifier'),('(','symbol'),('5','intConst'),(')','symbol'),(')','symbol'),(')','symbol')]
    assert SubroutineCallHandler.isSubroutineCall(unstructured_xml) == 19
    # 5.2 单元测试: SubroutineCallHandler.processXML
    unstructured_xml = [('varName_1','identifier'),('(','symbol'),(')','symbol')]
    handler_test(SubroutineCallHandler(),unstructured_xml,'<identifier> varName </identifier> <symbol> ( </symbol>\n<expressionList>\n</expressionList>\n<symbol> ) </symbol>\n')
    unstructured_xml = [('varName_1','identifier'),('(','symbol'),('expression_1','intConst'),(')','symbol')]
    handler_test(SubroutineCallHandler(),unstructured_xml,'<identifier> varName </identifier> <symbol> ( </symbol>\n<expressionList>\n<expression> <term> <integerConstant> 1 </integerConstant> </term>\n</expression>\n</expressionList>\n<symbol> ) </symbol>\n')
    unstructured_xml = [('varName_1','identifier'),('(','symbol'),('expression_1','intConst'),('expression_2','intConst'),(')','symbol')]
    handler_test(SubroutineCallHandler(),unstructured_xml,'<identifier> varName </identifier> <symbol> ( </symbol>\n<expressionList>\n<expression> <term> <integerConstant> 1 </integerConstant> </term>\n</expression>\n<symbol> , </symbol>\n<expression> <term> <integerConstant> 2 </integerConstant> </term>\n</expression>\n</expressionList>\n<symbol> ) </symbol>\n')
    # 6. 单元测试: TermHandler
    # 6.1 单元测试: TermHandler.isTerm
    # 6.1.1 单元测试: TermHandler.isTerm: intConst | stringConst
    unstructured_xml = [('varName_1','identifier')]
    assert TermHandler.isTerm(unstructured_xml) == 1
    # 6.1.2 单元测试: TermHandler.isTerm: varName
    unstructured_xml = [('varName_1','identifier')]
    assert TermHandler.isTerm(unstructured_xml) == 1
    # 6.1.3 单元测试: TermHandler.isTerm: unaryOp term
    unstructured_xml = [('~','symbol'),('varName_1','identifier')]
    assert TermHandler.isTerm(unstructured_xml) == 2
    # 6.1.4 单元测试: TermHandler.isTerm: ( expression )
    unstructured_xml = [('(','symbol'),('varName_1','identifier'),(')','symbol')]
    assert TermHandler.isTerm(unstructured_xml) == 3
    # 6.1.5 单元测试: TermHandler.isTerm: varName [ expression ]
    unstructured_xml = [('varName_1','identifier'),('[','symbol'),('varName_2','identifier'),']','symbol']
    assert TermHandler.isTerm(unstructured_xml) == 5
    # 6.1.6 单元测试: TermHandler.isTerm: subroutineCall
    unstructured_xml = [('varName_1','identifier'),('(','symbol'),(')','symbol')]
    assert TermHandler.isTerm(unstructured_xml) == 3
    # 6.1.4 单元测试：TermHandler.isTerm: (~((a+b)))
    unstructured_xml = [('[','symbol'),('~','symbol'),('(','symbol'),('(','symbol'),('a','identifier'),('+','symbol'),('b','identifier'),(')','symbol'),(')','symbol'),']','symbol']
    assert TermHandler.isTerm(unstructured_xml) == 12
    # 6.1.5 单元测试：TermHandler.isTerm: (~((3+4)=(5+6)))
    unstructured_xml = [('[','symbol'),('~','symbol'),('(','symbol'),('(','symbol'),('3','intConst'),('+','symbol'),('4','intConst'),(')','symbol'),('=','symbol'),('(','symbol'),('5','intConst'),('+','symbol'),('6','intConst'),(')','symbol'),(')','symbol'),']','symbol']
    assert TermHandler.isTerm(unstructured_xml) == 20
    # 6.2 单元测试: TermHandler.processXML
    # 6.2.1 单元测试: TermHandler.processXML: intConst | stringConst
    unstructured_xml = [('3','intConst')]
    handler_test(TermHandler(),unstructured_xml,'<intConst> 3 </intConst>')
    # 6.2.2 单元测试: TermHandler.processXML: varName
    unstructured_xml = [('varName_1','identifier')]
    handler_test(TermHandler(),unstructured_xml,'<identifier> varName </identifier>')
    # 6.2.3 单元测试: TermHandler.processXML: unaryOp term
    unstructured_xml = [('~','symbol'),('varName_1','identifier')]
    handler_test(TermHandler(),unstructured_xml,'<symbol> ~ </symbol>\n<identifier> varName </identifier>')
    # 6.2.4 单元测试: TermHandler.processXML: ( expression )
    unstructured_xml = [('(','symbol'),('varName_1','identifier'),(')','symbol')]
    handler_test(TermHandler(),unstructured_xml,'<symbol> ( </symbol>\n<expression>\n<term> <identifier> varName </identifier> </term>\n</expression>\n<symbol> ) </symbol>')
    # 7. 单元测试: ExpressionListHandler
    # 7.1 单元测试: ExpressionListHandler.isExpressionList
    # 7.1.1 单元测试: ExpressionListHandler.isExpressionList: expression
    unstructured_xml = [('varName_1','identifier')]
    assert ExpressionListHandler.isExpressionList(unstructured_xml) == 1
    # 7.1.2 单元测试: ExpressionListHandler.isExpressionList: expression, expression
    unstructured_xml = [('varName_1','identifier'),(',','symbol'),('varName_2','identifier')]
    assert ExpressionListHandler.isExpressionList(unstructured_xml) == 3
    # 7.1.3 单元测试: ExpressionListHandler.isExpressionList: ("A"+"B"), (a+b+c), expression
    unstructured_xml = [('(','symbol'),('(','symbol'),('A','stringConst'),('+','symbol'),('B','stringConst'),(')','symbol'),(')','symbol'),(',','symbol'),('(','symbol'),('a','identifier'),('+','symbol'),('b','identifier'),('+','symbol'),('c','identifier'),(')','symbol'),(',','symbol'),('varName_1','identifier')]
    assert ExpressionListHandler.isExpressionList(unstructured_xml) == 19
    # 7.2 单元测试: ExpressionListHandler.processXML
    # 7.2.1 单元测试: ExpressionListHandler.processXML: ("A"+"B"), (a+b+c), expression
    unstructured_xml = [('(','symbol'),('(','symbol'),('A','stringConst'),('+','symbol'),('B','stringConst'),(')','symbol'),(')','symbol'),(',','symbol'),('(','symbol'),('a','identifier'),('+','symbol'),('b','identifier'),('+','symbol'),('c','identifier'),(')','symbol'),(',','symbol'),('varName_1','identifier')]
    handler_test(ExpressionListHandler(),unstructured_xml,'<expression>\n<term> <stringConstant> A </stringConstant> </term>\n<symbol> + </symbol>\n<term> <stringConstant> B </stringConstant> </term>\n</expression>\n<symbol> , </symbol>\n<expression>\n<term> <identifier> a </identifier> </term>\n<symbol> + </symbol>\n<term> <identifier> b </identifier> </term>\n<symbol> + </symbol>\n<term> <identifier> c </identifier> </term>\n</expression>\n<symbol> , </symbol>\n<expression>\n<term> <identifier> varName </identifier> </term>\n</expression>\n')
    # 8. 单元测试: ExpressionHandler
    # 8.1 单元测试: ExpressionHandler.isExpression
    # 8.1.1 单元测试: ExpressionHandler.isExpression: term op term op term ...
    pass