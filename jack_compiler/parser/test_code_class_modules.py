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
def test_class():
    codes = '''
    class Main {
        function void main() {
            var Array a;
            var int length;
            let length = Keyboard.readInt("HOW MANY NUMBERS? ");
            let a = Array.new(length);
            do Array.dispose(a);
            return;}'''
    _,unstructured_xml = segmentCodes(codes)
    class_handler = ClassHandler(unstructured_xml,'''''')

if __name__ == '__main__':
    for instance in test_instance:
        instance()
