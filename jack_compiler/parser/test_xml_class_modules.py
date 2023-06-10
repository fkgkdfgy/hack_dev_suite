import sys
import os
sys.path.append(os.path.dirname(__file__))

from tokenizer import Tokenizer
from base_modules import *
from expression_modules import *
from statement_modules import *
from class_modules import *

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
    # 按照\n 分割 codes
    if '\n' in codes:
        codes = codes.split('\n')
        total_unstructured_xml = []
        for code in codes:
            _,unstructure_xml = tokenizer.processLine(code)
            total_unstructured_xml.extend(unstructure_xml)
        return '',total_unstructured_xml
    else:    
        return tokenizer.processLine(codes)

def assert_answer(answer, result):
    assert removeWhiteSpace(answer) == removeWhiteSpace(result), 'answer: {0} \n result: {1}'.format(answer, result)

@add_test_instance
def test_classname():
    _,unstructured_xml = segmentCodes('''a''')
    handler = ClassNameHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<identifier> a </identifier>''')
    # 测试 find
    # assert ClassNameHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert ClassNameHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_subroutinename():
    _,unstructured_xml = segmentCodes('''AS_12_31_23a_sdasd''')
    handler = SubroutineNameHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<identifier> AS_12_31_23a_sdasd </identifier>''')
    # 测试 find
    # assert SubroutineNameHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert SubroutineNameHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_type():
    _,unstructured_xml = segmentCodes('''AS_12_31_23a_sdasd''')
    handler = TypeHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<identifier> AS_12_31_23a_sdasd </identifier>''')
    # 测试 find
    # assert TypeHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert TypeHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_varDec():
    _,unstructured_xml = segmentCodes('''var int a,b,c;''')
    handler = VarDecHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<varDec>
                <keyword> var </keyword>
                
                    <keyword> int </keyword>
                
                <identifier> a </identifier>
                    <symbol> , </symbol>
                    <identifier> b </identifier>
                    <symbol> , </symbol>
                    <identifier> c </identifier>
                <symbol> ; </symbol>
            </varDec>''')
    # 测试 find
    # assert VarDecHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert VarDecHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_classVarDec():
    _,unstructured_xml = segmentCodes('''static int a,b,c;''')
    handler = ClassVarDecHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<classVarDec>
                <keyword> static </keyword>
                
                    <keyword> int </keyword>
                
                <identifier> a </identifier>
                
                    <symbol> , </symbol>
                    <identifier> b </identifier>
                    <symbol> , </symbol>
                    <identifier> c </identifier>
                
                <symbol> ; </symbol>
            </classVarDec>''')
    # 测试 find
    # assert ClassVarDecHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert ClassVarDecHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_voidParameterList():
    _,unstructured_xml = segmentCodes('''''')
    handler = ParameterListHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<parameterList>
            </parameterList>''')
    # 测试 find
    # assert ParameterListHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert ParameterListHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_parameterList():
    _,unstructured_xml = segmentCodes('''int a, boolean b, AS_12_31_23a_sdasd c''')
    handler = ParameterListHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<parameterList>
                
                    <keyword> int </keyword>
                
                <identifier> a </identifier>
                    <symbol> , </symbol>
                    
                        <keyword> boolean </keyword>
                    
                    <identifier> b </identifier>
                    <symbol> , </symbol>
                    
                        <identifier> AS_12_31_23a_sdasd </identifier>
                    
                    <identifier> c </identifier>
            </parameterList>''')
    # 测试 find
    # assert ParameterListHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert ParameterListHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_voidSubroutineDec():
    _,unstructured_xml = segmentCodes('''function void a() { return x;}''')
    handler = SubroutineDecHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<subroutineDec>
                <keyword> function </keyword>
                <keyword> void </keyword>
                <identifier> a </identifier>
                <symbol> ( </symbol>
                <parameterList>    
                </parameterList>
                <symbol> ) </symbol>
                <subroutineBody>
                    <symbol> { </symbol>
                    <statements>
                        <returnStatement>
                            <keyword> return </keyword>
                            <expression>
                                <term>
                                    <identifier> x </identifier>
                                </term>
                            </expression>
                            <symbol> ; </symbol>
                        </returnStatement>
                    </statements>
                    <symbol> } </symbol>
                </subroutineBody>
            </subroutineDec>''')
    # 测试 find
    # # assert SubroutineDecHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert SubroutineDecHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_subroutineDec():
    _,unstructured_xml = segmentCodes('''function void a(int b) {let x = 1;}''')
    handler = SubroutineDecHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<subroutineDec>
                <keyword> function </keyword>
                <keyword> void </keyword>
                <identifier> a </identifier>
                <symbol> ( </symbol>
                <parameterList>    
                    
                        <keyword> int </keyword>
                    
                    <identifier> b </identifier>
                </parameterList>
                <symbol> ) </symbol>
                <subroutineBody>
                    <symbol> { </symbol>
                    <statements>
                        <letStatement>
                            <keyword> let </keyword>
                            <identifier> x </identifier>
                            <symbol> = </symbol>
                            <expression>
                                <term>
                                    <integerConstant> 1 </integerConstant>
                                </term> 
                            </expression>
                            <symbol> ; </symbol>
                        </letStatement>
                    </statements>
                    <symbol> } </symbol>
                </subroutineBody>
            </subroutineDec>''')
    # 测试 find
    # # assert SubroutineDecHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert SubroutineDecHandler().isTarget(unstructured_xml) == True


@add_test_instance
def test_subroutineBody():
    _,unstructured_xml = segmentCodes('''{var int a; let a = 1;}''')
    handler = SubroutineBodyHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<subroutineBody>
                <symbol> { </symbol>
                <varDec>
                    <keyword> var </keyword>
                    
                        <keyword> int </keyword>
                    
                    <identifier> a </identifier>
                    <symbol> ; </symbol>
                </varDec>
                <statements>
                    <letStatement>
                        <keyword> let </keyword>
                        <identifier> a </identifier>
                        <symbol> = </symbol>
                        <expression>
                            <term>
                                <integerConstant> 1 </integerConstant>
                            </term> 
                        </expression>
                        <symbol> ; </symbol>
                    </letStatement>
                </statements>
                <symbol> } </symbol>
            </subroutineBody>''')
    # 测试 find
    # assert SubroutineBodyHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert SubroutineBodyHandler().isTarget(unstructured_xml) == True


@add_test_instance
def test_class_complex():
    _,unstructured_xml = segmentCodes('''class A {static int a; function void b() {let x = 1;}}''')
    handler = ClassHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<class>
                <keyword> class </keyword>
                <identifier> A </identifier>
                <symbol> { </symbol>
                <classVarDec>
                    <keyword> static </keyword>
                    
                        <keyword> int </keyword>
                    
                    <identifier> a </identifier>
                    <symbol> ; </symbol>
                </classVarDec>
                <subroutineDec>
                    <keyword> function </keyword>
                    <keyword> void </keyword>
                    <identifier> b </identifier>
                    <symbol> ( </symbol>
                    <parameterList>
                    </parameterList>
                    <symbol> ) </symbol>
                    <subroutineBody>
                        <symbol> { </symbol>
                        <statements>
                            <letStatement>
                                <keyword> let </keyword>
                                <identifier> x </identifier>
                                <symbol> = </symbol>
                                <expression>
                                    <term>
                                        <integerConstant> 1 </integerConstant>
                                    </term> 
                                </expression>
                                <symbol> ; </symbol>
                            </letStatement>
                        </statements>
                        <symbol> } </symbol>
                    </subroutineBody>
                </subroutineDec>
                <symbol> } </symbol>
            </class>''')
    # 测试 find
    # assert ClassHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    # assert ClassHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_class_more_complex():
    _,unstructured_xml = segmentCodes('''class A {static int a; function void b() {let x = 1;} function void c() {let y = 2;}}''')
    handler = ClassHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<class>
                <keyword> class </keyword>
                <identifier> A </identifier>
                <symbol> { </symbol>
                <classVarDec>
                    <keyword> static </keyword>
                    
                        <keyword> int </keyword>
                    
                    <identifier> a </identifier>
                    <symbol> ; </symbol>
                </classVarDec>
                <subroutineDec>
                    <keyword> function </keyword>
                    <keyword> void </keyword>
                    <identifier> b </identifier>
                    <symbol> ( </symbol>
                    <parameterList>
                    </parameterList>
                    <symbol> ) </symbol>
                    <subroutineBody>
                        <symbol> { </symbol>
                        <statements>
                            <letStatement>
                                <keyword> let </keyword>
                                <identifier> x </identifier>
                                <symbol> = </symbol>
                                <expression>
                                    <term>
                                        <integerConstant> 1 </integerConstant>
                                    </term> 
                                </expression>
                                <symbol> ; </symbol>
                            </letStatement>
                        </statements>
                        <symbol> } </symbol>
                    </subroutineBody>
                </subroutineDec>
                <subroutineDec>
                    <keyword> function </keyword>
                    <keyword> void </keyword>
                    <identifier> c </identifier>
                    <symbol> ( </symbol>
                    <parameterList>
                    </parameterList>
                    <symbol> ) </symbol>
                    <subroutineBody>
                        <symbol> { </symbol>
                        <statements>
                            <letStatement>
                                <keyword> let </keyword>
                                <identifier> y </identifier>
                                <symbol> = </symbol>
                                <expression>
                                    <term>
                                        <integerConstant> 2 </integerConstant>
                                    </term> 
                                </expression>
                                <symbol> ; </symbol>
                            </letStatement>
                        </statements>
                        <symbol> } </symbol>
                    </subroutineBody>
                </subroutineDec>
                <symbol> } </symbol>
            </class>''')

if __name__ == '__main__':
    for test_case in test_instance:
        test_case()
