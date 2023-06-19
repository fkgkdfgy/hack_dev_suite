import os

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

