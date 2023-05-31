import os
import sys

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)

# 获取当前文件所在目录的路径
current_dir_path = os.path.dirname(current_file_path)

# 将当前目录加入到系统路径中
sys.path.append(current_dir_path+"/../")

from tokenizer import Tokenizer
from term_handler import TermHandler

def segmentCodes(codes):
    tokenizer=Tokenizer()
    return tokenizer.processLine(codes)

def test_IntConstand():
    # 测试 processXML
    _, unstructured_xml = segmentCodes("123")
    print(unstructured_xml)
    handler = TermHandler(unstructured_xml)
    assert handler.toXML() == '''<term><intConst> 123 </intConst></term>''','result:{0} \n gt:{1}'.format(handler.toXML(),'''<term><intConst> 123 </intConst></term>''')

def test_strConstant():
    # 测试 processXML
    unstructured_xml = segmentCodes('''"abc"''')
    handler = TermHandler(unstructured_xml)
    assert handler.toXML() == '''<term><stringConst> abc </stringConst></term>'''


def test_keywordConstant():
    # 测试 processXML
    unstructured_xml = segmentCodes('''true''')
    handler = TermHandler(unstructured_xml)
    assert handler.toXML() == '''<term><keyword> true </keyword></term>'''

def test_expression():
    # 测试 processXML
    unstructured_xml = segmentCodes('''(123)''')
    handler = TermHandler(unstructured_xml)
    assert handler.toXML() == '''<term><symbol> ( </symbol><expression><term><intConstant> 123 </intConstant></term></expression><symbol> ) </symbol></term>'''


if __name__ == '__main__':
    test_IntConstand()
    test_strConstant()
    test_keywordConstant()
    test_expression()
    print('test passed')