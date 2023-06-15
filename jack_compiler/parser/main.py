import os
import sys
import argparse

from text_io import TextIO
from tokenizer import Tokenizer
from grammar import Grammar

# 处理当前目录下的所有.jack 文件
# 将最终生成的文件放到当前目录下的output 文件夹中
# 保存的结果是一个jack文件，对应一个vm 文件 ie. Main.jack -> Main.vm
def processDir(dir_path,output_path):
    # 获取所有的jack 文件
    jack_files = []
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.jack'):
            jack_files.append(file_name)

    if not jack_files:
        raise Exception('there is no jack file in {0}'.format(dir_path))
    
    # 将jack_files 所有的文件集中到all_lines 中
    all_lines = []
    for jack_file in jack_files:
        abs_file_path = os.path.join(dir_path,jack_file)
        text_io = TextIO(abs_file_path,None)
        lines = text_io.get_all_lines()
        all_lines.extend(lines)
    
    # 将所有的lines 进行处理
    total_unstructured_xml = []
    tokenizer = Tokenizer()
    for line in all_lines:
        _,unstructured_xml = tokenizer.processLine(line)
        total_unstructured_xml.extend(unstructured_xml)
    
    # 将total_unstructured_xml 转换成xml 和 vm code
    grammar = Grammar() 
    grammar.processXML(total_unstructured_xml)

    # 保存 vm 文件
    for child in grammar.program_handler.children:
        xml = child.toXML()
        code = child.toCode()
        vm_file_name = child.getClassName() + '.vm'
        vm_file_path = os.path.join(output_path,vm_file_name)
        with open(vm_file_path,'w') as f:
            f.write(code)
        xml_file_name = child.getClassName() + '.xml'
        xml_file_path = os.path.join(output_path,xml_file_name)
        with open(xml_file_path,'w') as f:
            f.write(xml)


if __name__ == '__main__':

    # 获取输入参数, 只需要dir 和 output_path两个参数
    # dir 是必须有的参数，output_path 是可选参数
    # 如果没有指定output_path, 那么默认的output_path 是dir/output
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='the dir of jack files')
    parser.add_argument('-o', '--output_path', help='the output path of vm and xml files')
    args = parser.parse_args()

    # 获取 dir_path 的绝对路线
    dir_path = os.path.abspath(args.dir)
    output_path = args.output_path
    if not output_path:
        output_path = os.path.join(dir_path,'output')
        if not os.path.exists(output_path):
            os.makedirs(output_path)

    # 检查dir_path 是否存在
    if not os.path.exists(dir_path):
        raise Exception('dir_path {0} does not exist'.format(dir_path))
    
    # 处理dir_path 下的所有jack 文件
    try:
        processDir(dir_path,output_path)
    except Exception as e:
        print('error: {0}'.format(e))
        sys.exit(1)
