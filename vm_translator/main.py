

import sys
import os
import argparse
import translator_io 
import translator_parser
import memory_translator

from utilis import *



if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='hack_assembler is used to translate .asm into .hack')
    arg_parser.add_argument('--vm_file', default=None, type=str)

    args = arg_parser.parse_args()

    if not args.vm_file or not os.path.exists(args.vm_file):
        raise VMTranslatorException('asm file:{0} is not existed'.format(args.asm_file))

    vm_file = args.vm_file
    asm_file = args.vm_file+'.asm'

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