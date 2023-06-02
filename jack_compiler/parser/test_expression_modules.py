from expression_modules import *
from tokenizer import Tokenizer

test_instance = []

def add_test_instance(instance):
    def wrapper():
        print('test {0} start'.format(instance.__name__))
        instance()
        print('test {0} end'.format(instance.__name__))
    test_instance.append(wrapper)
    return wrapper

def removeWhiteSpace(sentense):
    result = sentense
    while ' ' in result:
        index = result.find(' ')
        result = result[0:index] + result[index+1:]
    while '\n' in result:
        index = result.find('\n')
        result = result[0:index] + result[index+1:]
    while '\r' in result:
        index = result.find('\r')
        result = result[0:index] + result[index+1:]
    return result

def segmentCodes(codes):
    tokenizer=Tokenizer()
    return tokenizer.processLine(codes)

def assert_answer(answer, result):
    assert removeWhiteSpace(answer) == removeWhiteSpace(result), 'answer: {0} \n result: {1}'.format(answer, result)

@add_test_instance
def test_keywordConstant():
    # 测试 processXML
    _,unstructured_xml = segmentCodes('''true''')
    handler = KeywordConstantHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<keyword> true </keyword>''')
    # 测试 find
    assert KeywordConstantHandler().findTarget(unstructured_xml) == len(unstructured_xml),'{0} != {1}'.format(KeywordConstantHandler().findTarget(unstructured_xml), len(unstructured_xml))
    # 测试 is
    assert KeywordConstantHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_unaryOp():
    _,unstructured_xml = segmentCodes('''~''')
    handler = UnaryOpHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<symbol> ~ </symbol>''')
    # 测试 find
    assert UnaryOpHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert UnaryOpHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_op():
    _,unstructured_xml = segmentCodes('''+''')
    handler = OpHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<symbol> + </symbol>''')
    # 测试 find
    assert OpHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert OpHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_varName():
    _,unstructured_xml = segmentCodes('''a''')
    handler = VarNameHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<identifier> a </identifier>''')
    # 测试 find
    assert VarNameHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert VarNameHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_constant():
    _,unstructured_xml = segmentCodes('''123''')
    handler = ConstantHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<intConst> 123 </intConst>''')
    # 测试 find
    assert ConstantHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ConstantHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_term_isConstant():
    _,unstructured_xml = segmentCodes('''123''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <intConst> 123 </intConst> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_term_isVarName():
    _,unstructured_xml = segmentCodes('''a''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <identifier> a </identifier> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_term_isKeywordConstant():
    _,unstructured_xml = segmentCodes('''true''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <keyword> true </keyword> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_term_isStringConstant():
    _,unstructured_xml = segmentCodes('''"abc"''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <stringConst> abc </stringConst> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_term_isUnaryOpTerm():
    _,unstructured_xml = segmentCodes('''-a''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <symbol> - </symbol> <term> <identifier> a </identifier> </term> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_term_isTarget():
    _,unstructured_xml = segmentCodes('''(a)''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <symbol> ( </symbol> <expression> <term> <identifier> a </identifier> </term> </expression> <symbol> ) </symbol> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True


@add_test_instance
def test_term_isArrayGet():
    _,unstructured_xml = segmentCodes('''a[1]''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <identifier> a </identifier> <symbol> [ </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ] </symbol> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_term_isSubroutineCall():
    _,unstructured_xml = segmentCodes('''a()''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <identifier> a </identifier> <symbol> ( </symbol> <expressionList> </expressionList> <symbol> ) </symbol> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

# code for segmentCodes ::= A_1(A_2, A_3, A_4)
@add_test_instance
def test_term_isNestedSubroutineCall1():
    _,unstructured_xml = segmentCodes('''A_1(A_2, A_3, A_4)''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <identifier> A_1 </identifier> <symbol> ( </symbol> <expressionList> <expression> <term> <identifier> A_2 </identifier> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> A_3 </identifier> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> A_4 </identifier> </term> </expression> </expressionList> <symbol> ) </symbol> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

# code for segmentCodes ::= A_1(A_2(), A_3(), A_4())
@add_test_instance
def test_term_isNestedSubroutineCall2():
    _,unstructured_xml = segmentCodes('''A_1(A_2(), A_3(), A_4())''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <identifier> A_1 </identifier> <symbol> ( </symbol> <expressionList> <expression> <term> <identifier> A_2 </identifier> <symbol> ( </symbol> <expressionList> </expressionList> <symbol> ) </symbol> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> A_3 </identifier> <symbol> ( </symbol> <expressionList> </expressionList> <symbol> ) </symbol> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> A_4 </identifier> <symbol> ( </symbol> <expressionList> </expressionList> <symbol> ) </symbol> </term> </expression> </expressionList> <symbol> ) </symbol> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

# code for segmentCodes ::= A_3(A_4(A_5()))
@add_test_instance
def test_term_isNestedSubroutineCall3():
    _,unstructured_xml = segmentCodes('''A_2(A_3(A_4(A_5())))''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <identifier> A_2 </identifier> <symbol> ( </symbol> <expressionList> <expression> <term> <identifier> A_3 </identifier> <symbol> ( </symbol> <expressionList> <expression> <term> <identifier> A_4 </identifier> <symbol> ( </symbol> <expressionList> <expression> <term> 
    <identifier> A_5 </identifier> <symbol> ( </symbol> <expressionList>
    </expressionList> <symbol> ) </symbol> </term> </expression> </expressionList> <symbol> ) </symbol> </term> </expression> </expressionList> <symbol> ) </symbol> </term> </expression> </expressionList> <symbol> ) </symbol> </term>''')

# code for segmentCodes ::= A((a+b)=(3+5+6+c+d))
@add_test_instance
def test_term_isNestedSubroutineCall4():
    _,unstructured_xml = segmentCodes('''A((a+b)=(3+5+6+c+d))''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <identifier> A </identifier> <symbol> ( </symbol> <expressionList> <expression> <term> <symbol> ( </symbol> <expression> <term> <identifier> a </identifier> </term> <symbol> + </symbol> <term> <identifier> b </identifier> </term> </expression> <symbol> ) </symbol> </term> <symbol> = </symbol> <term> <symbol> ( </symbol> <expression> <term> <intConst> 3 </intConst> </term> <symbol> + </symbol> <term> <intConst> 5 </intConst> </term> <symbol> + </symbol> <term> <intConst> 6 </intConst> </term> <symbol> + </symbol> <term> <identifier> c </identifier> </term> <symbol> + </symbol> <term> <identifier> d </identifier> </term> </expression> <symbol> ) </symbol> </term> </expression> </expressionList> <symbol> ) </symbol> </term>''')

# code for segementCodes ::= A(3+5)
@add_test_instance
def test_term_isNestedSubroutineCall5():
    _,unstructured_xml = segmentCodes('''A(3+5)''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <identifier> A </identifier> <symbol> ( </symbol> <expressionList> <expression> <term> <intConst> 3 </intConst> </term> <symbol> + </symbol> <term> <intConst> 5 </intConst> </term> </expression> </expressionList> <symbol> ) </symbol> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

# code for segmentCodes ::= A_2[A_3[A_4[A_5]]]
@add_test_instance
def test_term_isNestedArrayGet():
    _,unstructured_xml = segmentCodes('''A_2[A_3[A_4[A_5]]]''')
    handler = TermHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<term> <identifier> A_2 </identifier> <symbol> [ </symbol> <expression> <term> <identifier> A_3 </identifier> <symbol> [ </symbol> <expression> <term> <identifier> A_4 </identifier> <symbol> [ </symbol> <expression> <term> <identifier> A_5 </identifier> </term> </expression> <symbol> ] </symbol> </term> </expression> <symbol> ] </symbol> </term> </expression> <symbol> ] </symbol> </term>''')
    # 测试 find
    assert TermHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TermHandler().isTarget(unstructured_xml) == True

# code for segmentCodes ::= a+b
@add_test_instance
def test_expression():
    _,unstructured_xml = segmentCodes('''a+b''')
    handler = ExpressionHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<expression> <term> <identifier> a </identifier> </term> <symbol> + </symbol> <term> <identifier> b </identifier> </term> </expression>''')
    # 测试 find
    assert ExpressionHandler().findTarget(unstructured_xml) == len(unstructured_xml),'{0} != {1}'.format(ExpressionHandler().findTarget(unstructured_xml), len(unstructured_xml))
    # 测试 is
    assert ExpressionHandler().isTarget(unstructured_xml) == True

# code for segmentCodes ::= a+b+3+5+6+c+d
@add_test_instance
def test_expression_isLongOpTermExpression():
    _,unstructured_xml = segmentCodes('''a+b+3+5+6+c+d''')
    handler = ExpressionHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<expression> <term> <identifier> a </identifier> </term> <symbol> + </symbol> <term> <identifier> b </identifier> </term> <symbol> + </symbol> <term> <intConst> 3 </intConst> </term> <symbol> + </symbol> <term> <intConst> 5 </intConst> </term> <symbol> + </symbol> <term> <intConst> 6 </intConst> </term> <symbol> + </symbol> <term> <identifier> c </identifier> </term> <symbol> + </symbol> <term> <identifier> d </identifier> </term> </expression>''')
    # 测试 find
    assert ExpressionHandler().findTarget(unstructured_xml) == len(unstructured_xml),'{0} != {1}'.format(ExpressionHandler().findTarget(unstructured_xml), len(unstructured_xml))
    # 测试 is
    assert ExpressionHandler().isTarget(unstructured_xml) == True

# code for segmentCodes ::= a+b+3+5+(3+5)+c+A[123]
@add_test_instance
def test_expression_isNestedLongOpTermExpression():
    _,unstructured_xml = segmentCodes('''a+b+3+5+(3+5)+c+A[123]''')
    handler = ExpressionHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<expression> <term> <identifier> a </identifier> </term> <symbol> + </symbol> <term> <identifier> b </identifier> </term> <symbol> + </symbol> <term> <intConst> 3 </intConst> </term> <symbol> + </symbol> <term> <intConst> 5 </intConst> </term> <symbol> + </symbol> <term> <symbol> ( </symbol> <expression> <term> <intConst> 3 </intConst> </term> <symbol> + </symbol> <term> <intConst> 5 </intConst> </term> </expression> <symbol> ) </symbol> </term> <symbol> + </symbol> <term> <identifier> c </identifier> </term> <symbol> + </symbol> <term> <identifier> A </identifier> <symbol> [ </symbol> <expression> <term> <intConst> 123 </intConst> </term> </expression> <symbol> ] </symbol> </term> </expression>''')
    # 测试 find
    assert ExpressionHandler().findTarget(unstructured_xml) == len(unstructured_xml),'{0} != {1}'.format(ExpressionHandler().findTarget(unstructured_xml), len(unstructured_xml))
    # 测试 is
    assert ExpressionHandler().isTarget(unstructured_xml) == True


@add_test_instance
def test_expressionList_isEmpty():
    _,unstructured_xml = segmentCodes('''''')
    handler = ExpressionListHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<expressionList> </expressionList>''')
    # 测试 find,此处应该assert
    assert ExpressionListHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ExpressionListHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_expressionList_isOneExpression():
    _,unstructured_xml = segmentCodes('''a''')
    handler = ExpressionListHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<expressionList> <expression> <term> <identifier> a </identifier> </term> </expression> </expressionList>''')
    # 测试 find
    assert ExpressionListHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ExpressionListHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_expressionList_isTwoExpression():
    _,unstructured_xml = segmentCodes('''a, b''')
    handler = ExpressionListHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<expressionList> <expression> <term> <identifier> a </identifier> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> b </identifier> </term> </expression> </expressionList>''')
    # 测试 find
    assert ExpressionListHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ExpressionListHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_expressionList_isThreeExpression():
    _,unstructured_xml = segmentCodes('''a, b, c''')
    handler = ExpressionListHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<expressionList> <expression> <term> <identifier> a </identifier> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> b </identifier> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> c </identifier> </term> </expression> </expressionList>''')
    # 测试 find
    assert ExpressionListHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ExpressionListHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_expressionList_isNestedExpressionList():
    _,unstructured_xml = segmentCodes('''a, A(b, c), d''')
    handler = ExpressionListHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<expressionList> <expression> <term> <identifier> a </identifier> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> A </identifier> <symbol> ( </symbol> <expressionList> <expression> <term> <identifier> b </identifier> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> c </identifier> </term> </expression> </expressionList> <symbol> ) </symbol> </term> </expression> <symbol> , </symbol> <expression> <term> <identifier> d </identifier> </term> </expression> </expressionList>''')
    # 测试 find
    assert ExpressionListHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ExpressionListHandler().isTarget(unstructured_xml) == True


if __name__ == '__main__':

    for test_case in test_instance:
        test_case()
