from statement_modules import *
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
def test_let_statement():
    _,unstructured_xml = segmentCodes('''let x = 1;''')
    handler = LetStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement>''')
    # 测试 find
    assert LetStatementHandler().findTargetStatement(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert LetStatementHandler().isTargetStatement(unstructured_xml) == True

@add_test_instance
def test_let_statement_array():
    _,unstructured_xml = segmentCodes('''let x[1] = 1;''')
    handler = LetStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> [ </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ] </symbol> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement>''')
    # 测试 find
    assert LetStatementHandler().findTargetStatement(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert LetStatementHandler().isTargetStatement(unstructured_xml) == True