import os
import sys
import argparse

from text_io import TextIO
from tokenizer import Tokenizer
from grammar import Grammar

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser(description='jack file is used to translate .jack into .xml file')
    arg_parser.add_argument('--file',default=None,type=str)
    args = arg_parser.parse_args()

    if args.file and not os.path.exists(args.file):
        raise Exception('jack file:{0} is not existed'.format(args.file))
    
    abs_file_path = args.file
    structured_xml_path = args.file + ".xml"
    
    text_io = TextIO(abs_file_path,structured_xml_path)
    tokenizer = Tokenizer()
    grammar = Grammar()
    
    lines = text_io.get_all_lines()

    total_unstructured_xml = []
    for line in lines:
        print(line)
        _,unstructured_xml = tokenizer.processLine(line)
        total_unstructured_xml.extend(unstructured_xml)
    print('total unstructured xml : \n{0}'.format(total_unstructured_xml))

    for index, word in  enumerate(total_unstructured_xml):
        if word[0] == 'class':
            total_unstructured_xml = total_unstructured_xml[index:]

    structured_xml = grammar.processXML(total_unstructured_xml)

    text_io.write_line(structured_xml)
    text_io.close_write()