

import sys
import os
import argparse
import translator_io 
import translator_parser
import memory_translator

from utilis import *

def process_file(file_path):
    vm_file = file_path
    asm_file = file_path+'.asm'

    frame_name = os.path.basename(vm_file).split('.')[0]

    data_io = translator_io.TextIO(vm_file,asm_file)
    sentense_parser = translator_parser.Parser()
    translator = memory_translator.Translator(frame_name)

    new_line = data_io.get_line()
    while new_line:
        print(new_line)
        new_line = new_line[0:-1]
        segments = sentense_parser.Process(new_line)
        print(segments)
        result = translator.process(segments)
        new_line = data_io.get_line()
        if result:
            data_io.write_line(result)
    data_io.close_write()

def process_dir(dir_path):
    pass


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='hack_assembler is used to translate .asm into .hack')
    arg_parser.add_argument('--file', default=None, type=str)
    arg_parser.add_argument('--dir',default=None,type=str)

    args = arg_parser.parse_args()

    if not args.file and not args.dir:
        raise VMTranslatorException('please input a file or dir as target of translator')
    
    if args.file and not os.path.exists(args.file):
        raise VMTranslatorException('asm file:{0} is not existed'.format(args.file))

    if args.dir and not os.path.exists(args.dir):
        raise VMTranslatorException('asm dir:{0} is not existed'.format(args.dir))

    if args.file:
        process_file(args.file)
    
    if args.dir:
        process_dir(args.dir)