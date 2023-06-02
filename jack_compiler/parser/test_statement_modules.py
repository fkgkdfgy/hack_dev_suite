import sys
import os
sys.path.append(os.path.dirname(__file__))

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
    assert LetStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert LetStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_let_statement_array():
    _,unstructured_xml = segmentCodes('''let x[1] = 1;''')
    handler = LetArrayStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> [ </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ] </symbol> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement>''')
    # 测试 find
    assert LetArrayStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert LetArrayStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_if_statement():
    _,unstructured_xml = segmentCodes('''if (x) {let x = 1;}''')
    handler = IfStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<ifStatement> <keyword> if </keyword> <symbol> ( </symbol> <expression> <term> <identifier> x </identifier> </term> </expression> <symbol> ) </symbol> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> </ifStatement>''')
    # 测试 find
    assert IfStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert IfStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_if_else_statement():
    _,unstructured_xml = segmentCodes('''if (x) {let x = 1;} else {let x = 2;}''')
    handler = IfStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<ifStatement> <keyword> if </keyword> <symbol> ( </symbol> <expression> <term> <identifier> x </identifier> </term> </expression> <symbol> ) </symbol> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> <keyword> else </keyword> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 2 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> </ifStatement>''')
    # 测试 find
    assert IfStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert IfStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_while_statement():
    _,unstructured_xml = segmentCodes('''while (x) {let x = 1;}''')
    handler = WhileStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<whileStatement> <keyword> while </keyword> <symbol> ( </symbol> <expression> <term> <identifier> x </identifier> </term> </expression> <symbol> ) </symbol> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> </whileStatement>''')
    # 测试 find
    assert WhileStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert WhileStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_do_statement():
    _,unstructured_xml = segmentCodes('''do x();''')
    handler = DoStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<doStatement> <keyword> do </keyword> <identifier> x </identifier> <symbol> ( </symbol> <expressionList> </expressionList> <symbol> ) </symbol> <symbol> ; </symbol> </doStatement>''')
    # 测试 find
    assert DoStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert DoStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_return_statement():
    _,unstructured_xml = segmentCodes('''return x;''')
    handler = ReturnStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<returnStatement> <keyword> return </keyword> <expression> <term> <identifier> x </identifier> </term> </expression> <symbol> ; </symbol> </returnStatement>''')
    # 测试 find
    assert ReturnStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ReturnStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_return_statement_void():
    _,unstructured_xml = segmentCodes('''return     ;''')
    handler = VoidReturnStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<returnStatement> <keyword> return </keyword> <symbol> ; </symbol> </returnStatement>''')
    # 测试 find
    assert VoidReturnStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert VoidReturnStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statement_let_statement():
    _,unstructured_xml = segmentCodes('''let x = 1;''')
    handler = StatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement>''')
    # 测试 find
    assert StatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert StatementHandler().isTarget(unstructured_xml) == True


@add_test_instance
def test_statement_let_statement_array():
    _,unstructured_xml = segmentCodes('''let x[1] = 1;''')
    handler = StatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> [ </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ] </symbol> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement>''')
    # 测试 find
    assert StatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert StatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statement_if_statement():
    _,unstructured_xml = segmentCodes('''if (x) {let x = 1;}''')
    handler = StatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<ifStatement> <keyword> if </keyword> <symbol> ( </symbol> <expression> <term> <identifier> x </identifier> </term> </expression> <symbol> ) </symbol> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> </ifStatement>''')
    # 测试 find
    assert StatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert StatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statement_if_statement_else():
    _,unstructured_xml = segmentCodes('''if (x) {let x = 1;} else {let x = 1;}''')
    handler = StatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<ifStatement> <keyword> if </keyword> <symbol> ( </symbol> <expression> <term> <identifier> x </identifier> </term> </expression> <symbol> ) </symbol> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> <keyword> else </keyword> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> </ifStatement>''')
    # 测试 find
    assert StatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert StatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statement_while_statement():
    _,unstructured_xml = segmentCodes('''while (x) {let x = 1;}''')
    handler = StatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<whileStatement> <keyword> while </keyword> <symbol> ( </symbol> <expression> <term> <identifier> x </identifier> </term> </expression> <symbol> ) </symbol> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> x </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> </whileStatement>''')
    # 测试 find
    assert StatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert StatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statement_do_statement():
    _,unstructured_xml = segmentCodes('''do x();''')
    handler = StatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<doStatement> <keyword> do </keyword> <identifier> x </identifier> <symbol> ( </symbol> <expressionList> </expressionList> <symbol> ) </symbol> <symbol> ; </symbol> </doStatement>''')
    # 测试 find
    assert StatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert StatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statement_return_statement():
    _,unstructured_xml = segmentCodes('''return x;''')
    handler = StatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<returnStatement> <keyword> return </keyword> <expression> <term> <identifier> x </identifier> </term> </expression> <symbol> ; </symbol> </returnStatement>''')
    # 测试 find
    assert StatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert StatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statement_return_statement_void():
    _,unstructured_xml = segmentCodes('''return;''')
    handler = StatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<returnStatement> <keyword> return </keyword> <symbol> ; </symbol> </returnStatement>''')
    # 测试 find
    assert StatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert StatementHandler().isTarget(unstructured_xml) == True

# code for codeSegement ::= let a=1; let A[1] = A_2[A_4(3+5)];
@add_test_instance
def test_statements_let_statement_complex():
    _,unstructured_xml = segmentCodes('''let a=1; let A[1] = A_2[A_4(3+5)];''')
    handler = MultiStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<statements> <letStatement> <keyword> let </keyword> <identifier> a </identifier> <symbol> = </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ; </symbol> </letStatement> <letStatement> <keyword> let </keyword> <identifier> A </identifier> <symbol> [ </symbol> <expression> <term> <intConst> 1 </intConst> </term> </expression> <symbol> ] </symbol> <symbol> = </symbol> <expression> <term> <identifier> A_2 </identifier> <symbol> [ </symbol> <expression> <term> <identifier> A_4 </identifier> <symbol> ( </symbol> <expressionList> <expression> <term> <intConst> 3 </intConst> </term> <symbol> + </symbol> <term> <intConst> 5 </intConst> </term> </expression> </expressionList> <symbol> ) </symbol> </term> </expression> <symbol> ] </symbol></term> </expression> <symbol> ; </symbol> </letStatement> </statements>''')
    # 测试 find
    assert MultiStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert MultiStatementHandler().isTarget(unstructured_xml) == True

# code for codeSegement ::= let x = 1; if(x=1) {while (x) {let x = 1;} let x = 1;} else {let x = 1;}
@add_test_instance
def test_statements_if_statement_complex():
    _,unstructured_xml = segmentCodes('''let x = 1; if(x=1) {while (x) {let x = 1;} let x = 1;} else {let x = 1;}''')
    handler = MultiStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<statements><letStatement><keyword>let</keyword><identifier>x</identifier><symbol>=</symbol><expression><term><intConst>1</intConst></term></expression><symbol>;</symbol></letStatement><ifStatement><keyword>if</keyword><symbol>(</symbol><expression><term><identifier>x</identifier></term><symbol>=</symbol><term><intConst>1</intConst></term></expression><symbol>)</symbol><symbol>{</symbol><statements><whileStatement><keyword>while</keyword><symbol>(</symbol><expression><term><identifier>x</identifier></term></expression><symbol>)</symbol><symbol>{</symbol><statements><letStatement><keyword>let</keyword><identifier>x</identifier><symbol>=</symbol><expression><term><intConst>1</intConst></term></expression><symbol>;</symbol></letStatement></statements><symbol>}</symbol></whileStatement><letStatement><keyword>let</keyword><identifier>x</identifier><symbol>=</symbol><expression><term><intConst>1</intConst></term></expression><symbol>;</symbol></letStatement></statements><symbol>}</symbol><keyword>else</keyword><symbol>{</symbol><statements><letStatement><keyword>let</keyword><identifier>x</identifier><symbol>=</symbol><expression><term><intConst>1</intConst></term></expression><symbol>;</symbol></letStatement></statements><symbol>}</symbol></ifStatement></statements>''')
    # 测试 find
    assert MultiStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert MultiStatementHandler().isTarget(unstructured_xml) == True

# code for codeSegement ::= while (x) { if (x) {let x = 1;} else {let x = 1;}} let x = 1;
@add_test_instance
def test_statements_while_statement_complex():
    _,unstructured_xml = segmentCodes('''while (x) { if (x) {let x = 1;} else {let x = 1;}} let x = 1;''')
    handler = MultiStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<statements><whileStatement><keyword>while</keyword><symbol>(</symbol><expression><term><identifier>x</identifier></term></expression><symbol>)</symbol><symbol>{</symbol><statements><ifStatement><keyword>if</keyword><symbol>(</symbol><expression><term><identifier>x</identifier></term></expression><symbol>)</symbol><symbol>{</symbol><statements><letStatement><keyword>let</keyword><identifier>x</identifier><symbol>=</symbol><expression><term><intConst>1</intConst></term></expression><symbol>;</symbol></letStatement></statements><symbol>}</symbol><keyword>else</keyword><symbol>{</symbol><statements><letStatement><keyword>let</keyword><identifier>x</identifier><symbol>=</symbol><expression><term><intConst>1</intConst></term></expression><symbol>;</symbol></letStatement></statements><symbol>}</symbol></ifStatement></statements><symbol>}</symbol></whileStatement><letStatement><keyword>let</keyword><identifier>x</identifier><symbol>=</symbol><expression><term><intConst>1</intConst></term></expression><symbol>;</symbol></letStatement></statements>''')
    # 测试 find
    assert MultiStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert MultiStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statements_do_statement_complex(): 
    _,unstructured_xml = segmentCodes('''do Output.printString("hello world"); do Output.printInt(1);''')
    handler = MultiStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<statements><doStatement><keyword>do</keyword><identifier>Output</identifier><symbol>.</symbol><identifier>printString</identifier><symbol>(</symbol><expressionList><expression><term><stringConst>hello world</stringConst></term></expression></expressionList><symbol>)</symbol><symbol>;</symbol></doStatement><doStatement><keyword>do</keyword><identifier>Output</identifier><symbol>.</symbol><identifier>printInt</identifier><symbol>(</symbol><expressionList><expression><term><intConst>1</intConst></term></expression></expressionList><symbol>)</symbol><symbol>;</symbol></doStatement></statements>''')
    # 测试 find
    assert MultiStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert MultiStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statements_return_statement_complex():
    _,unstructured_xml = segmentCodes('''return os.findcharformFile(file_1,tareget_line_num[3]); return;''')
    handler = MultiStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<statements><returnStatement><keyword>return</keyword><expression><term><identifier>os</identifier><symbol>.</symbol><identifier>findcharformFile</identifier><symbol>(</symbol><expressionList><expression><term><identifier>file_1</identifier></term></expression><symbol>,</symbol><expression><term><identifier>tareget_line_num</identifier><symbol>[</symbol><expression><term><intConst>3</intConst></term></expression><symbol>]</symbol></term></expression></expressionList><symbol>)</symbol></term></expression><symbol>;</symbol></returnStatement><returnStatement><keyword>return</keyword><symbol>;</symbol></returnStatement></statements>''')
    # 测试 find
    assert MultiStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert MultiStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statements_let_statement_complex():
    _,unstructured_xml = segmentCodes('''return os.findcharformFile(file_1,tareget_line_num[3]);''')
    handler = MultiStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<statements><returnStatement><keyword>return</keyword><expression><term><identifier>os</identifier><symbol>.</symbol><identifier>findcharformFile</identifier><symbol>(</symbol><expressionList><expression><term><identifier>file_1</identifier></term></expression><symbol>,</symbol><expression><term><identifier>tareget_line_num</identifier><symbol>[</symbol><expression><term><intConst>3</intConst></term></expression><symbol>]</symbol></term></expression></expressionList><symbol>)</symbol></term></expression><symbol>;</symbol></returnStatement></statements>''')
    # 测试 find
    assert MultiStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert MultiStatementHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_statements_if_statement_complex():
    _,unstructured_xml = segmentCodes('''if (os.haveScreen()) {let mouse_coordinate = os.MouseCoordinate();} else {let screen_i2c = os.ScreenI2C();}''')
    handler = MultiStatementHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<statements> <ifStatement> <keyword> if </keyword> <symbol> ( </symbol> <expression> <term> <identifier> os </identifier> <symbol> . </symbol> <identifier> haveScreen </identifier> <symbol> ( </symbol> <expressionList> </expressionList> <symbol> ) </symbol> </term> </expression> <symbol> ) </symbol> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> mouse_coordinate </identifier> <symbol> = </symbol> <expression> <term> <identifier> os </identifier> <symbol> . </symbol> <identifier> MouseCoordinate </identifier> <symbol> ( </symbol> <expressionList> </expressionList> <symbol> ) </symbol> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> <keyword> else </keyword> <symbol> { </symbol> <statements> <letStatement> <keyword> let </keyword> <identifier> screen_i2c </identifier> <symbol> = </symbol> <expression> <term> <identifier> os </identifier> <symbol> . </symbol> <identifier> ScreenI2C </identifier> <symbol> ( </symbol> <expressionList> </expressionList> <symbol> ) </symbol> </term> </expression> <symbol> ; </symbol> </letStatement> </statements> <symbol> } </symbol> </ifStatement> </statements>''')
    # 测试 find
    assert MultiStatementHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert MultiStatementHandler().isTarget(unstructured_xml) == True

if __name__ == '__main__':

    for test_case in test_instance:
        test_case()    