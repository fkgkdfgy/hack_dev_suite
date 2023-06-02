
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
    return tokenizer.processLine(codes)

def assert_answer(answer, result):
    assert removeWhiteSpace(answer) == removeWhiteSpace(result), 'answer: {0} \n result: {1}'.format(answer, result)

@add_test_instance
def test_classname():
    _,unstructured_xml = segmentCodes('''a''')
    handler = ClassNameHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<identifier> a </identifier>''')
    # 测试 find
    assert ClassNameHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ClassNameHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_subroutinename():
    _,unstructured_xml = segmentCodes('''AS_12_31_23a_sdasd''')
    handler = SubroutineNameHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<identifier> AS_12_31_23a_sdasd </identifier>''')
    # 测试 find
    assert SubroutineNameHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert SubroutineNameHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_type():
    _,unstructured_xml = segmentCodes('''AS_12_31_23a_sdasd''')
    handler = TypeHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<identifier> AS_12_31_23a_sdasd </identifier>''')
    # 测试 find
    assert TypeHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert TypeHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_varDec():
    _,unstructured_xml = segmentCodes('''var int a,b,c;''')
    handler = VarDecHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<varDec>
                <keyword> var </keyword>
                <type>
                    <keyword> int </keyword>
                </type>
                <varName> a </varName>
                <multi_varName>
                    <symbol> , </symbol>
                    <varName> b </varName>
                    <symbol> , </symbol>
                    <varName> c </varName>
                </multi_varName>
                <symbol> ; </symbol>
            </varDec>''')
    # 测试 find
    assert VarDecHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert VarDecHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_classVarDec():
    _,unstructured_xml = segmentCodes('''static int a,b,c;''')
    handler = ClassVarDecHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<classVarDec>
                <keyword> static </keyword>
                <type>
                    <keyword> int </keyword>
                </type>
                <varName> a </varName>
                <multi_varName>
                    <symbol> , </symbol>
                    <varName> b </varName>
                    <symbol> , </symbol>
                    <varName> c </varName>
                </multi_varName>
                <symbol> ; </symbol>
            </classVarDec>''')
    # 测试 find
    assert ClassVarDecHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ClassVarDecHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_voidParameterList():
    _,unstructured_xml = segmentCodes('''''')
    handler = ParameterListHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<parameterList>
            </parameterList>''')
    # 测试 find
    assert ParameterListHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ParameterListHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_parameterList():
    _,unstructured_xml = segmentCodes('''int a, boolean b, AS_12_31_23a_sdasd c''')
    handler = ParameterListHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<parameterList>
                <type>
                    <keyword> int </keyword>
                </type>
                <varName> a </varName>
                <multi_parameter>
                    <symbol> , </symbol>
                    <type>
                        <keyword> boolean </keyword>
                    </type>
                    <varName> b </varName>
                    <symbol> , </symbol>
                    <type>
                        <identifier> AS_12_31_23a_sdasd </identifier>
                    </type>
                    <varName> c </varName>
                </multi_parameter>
            </parameterList>''')
    # 测试 find
    assert ParameterListHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert ParameterListHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_voidSubroutineDec():
    _,unstructured_xml = segmentCodes('''function void a() {}''')
    handler = SubroutineDecHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<subroutineDec>
                <keyword> function </keyword>
                <keyword> void </keyword>
                <subroutineName> a </subroutineName>
                <symbol> ( </symbol>
                <parameterList>
                </parameterList>
                <symbol> ) </symbol>
                <subroutineBody>
                    <symbol> { </symbol>
                    <varDec>
                    </varDec>
                    <statements>
                    </statements>
                    <symbol> } </symbol>
                </subroutineBody>
            </subroutineDec>''')
    # 测试 find
    assert SubroutineDecHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert SubroutineDecHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_subroutineDec():
    _,unstructured_xml = segmentCodes('''function void a(int b) {let x = 1;}''')
    handler = SubroutineDecHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<subroutineDec>
                <keyword> function </keyword>
                <keyword> void </keyword>
                <subroutineName> a </subroutineName>
                <symbol> ( </symbol>
                <parameterList>    
                    <type>
                        <keyword> int </keyword>
                    </type>
                    <varName> b </varName>
                </parameterList>
                <symbol> ) </symbol>
                <subroutineBody>
                    <symbol> { </symbol>
                    <varDec>
                    </varDec>
                    <statements>
                        <letStatement>
                            <keyword> let </keyword>
                            <varName> x </varName>
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
    assert SubroutineDecHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert SubroutineDecHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_voidSubroutineBody():
    _,unstructured_xml = segmentCodes('''{}''')
    handler = SubroutineBodyHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<subroutineBody>
                <symbol> { </symbol>
                <varDec>
                </varDec>
                <statements>
                </statements>
                <symbol> } </symbol>
            </subroutineBody>''')
    # 测试 find
    assert SubroutineBodyHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert SubroutineBodyHandler().isTarget(unstructured_xml) == True

@add_test_instance
def test_subroutineBody():
    _,unstructured_xml = segmentCodes('''{var int a; let a = 1;}''')
    handler = SubroutineBodyHandler(unstructured_xml)
    assert_answer(handler.toXML(), '''<subroutineBody>
                <symbol> { </symbol>
                <varDec>
                    <keyword> var </keyword>
                    <type>
                        <keyword> int </keyword>
                    </type>
                    <varName> a </varName>
                </varDec>
                <statements>
                    <letStatement>
                        <keyword> let </keyword>
                        <varName> a </varName>
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
    assert SubroutineBodyHandler().findTarget(unstructured_xml) == len(unstructured_xml)
    # 测试 is
    assert SubroutineBodyHandler().isTarget(unstructured_xml) == True

if __name__ == '__main__':
    for test_case in test_instance:
        test_case()
