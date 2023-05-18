

import sys
import os
import argparse
import translator_io 
import translator_parser
import memory_translator

from utilis import *

def process_file(codes,vm_path,asm_file):
    vm_file = vm_path
    asm_file = asm_file

    frame_name = os.path.basename(asm_file).split('.')[0]

    data_io = translator_io.TextIO(vm_file,asm_file)
    sentense_parser = translator_parser.Parser()
    translator = memory_translator.Translator(frame_name)

    for line in codes:
        new_line = line[0:-1]
        print(new_line)
        segments = sentense_parser.Process(new_line)
        print(segments)
        result = translator.process(segments)
        if result:
            data_io.write_line(result)
    data_io.close_write()


def process_dir(dir_path):
    
    def get_all_codes(file_list):
        total_codes = []
        sys_file = os.path.join(dir_path,'Sys.vm')
        if sys_file in file_list:
            data_io = translator_io.TextIO(sys_file, None)    
            total_codes.extend(data_io.get_all_lines())
            file_list.remove(sys_file)
        
        for file in file_list:
            data_io = translator_io.TextIO(file, None)    
            total_codes.extend(data_io.get_all_lines())
        return total_codes 

    def split_files_and_dirs(dir_path):

        def IsDir(abs_path):
            return os.path.isdir(abs_path)
        
        def IsVMFile(abs_path):
            if os.path.isfile(abs_file_name):
                split_names= os.path.basename(file_name).split('.')
                if split_names and split_names[-1] == 'vm':
                    return True
            return False
        
        files = os.listdir(dir_path)
        file_list,dir_list,abs_file_list,abs_dir_list = [],[],[],[]
        for file_name in files:
            abs_file_name = os.path.join(dir_path,file_name)
            if IsDir(abs_file_name):
                dir_list.append(file_name)
                abs_dir_list.append(abs_file_name)
            elif IsVMFile(abs_file_name):
                file_list.append(file_name)
                abs_file_list.append(abs_file_name)
        
        return file_list,dir_list,abs_file_list,abs_dir_list

    if not os.path.exists(args.dir):
        raise VMTranslatorException('asm dir:{0} is not existed'.format(args.dir))
    
    file_list,dir_list,_,_ = split_files_and_dirs(dir_path)

    for dir in dir_list:
        process_dir(os.path.join(dir_path,dir))
    
    total_codes = get_all_codes(file_list)

    target_asm_file = os.path.join(dir_path,'Sys.vm.asm')
    process_file(codes=total_codes,vm_path=None,asm_file=target_asm_file)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='hack_assembler is used to translate .asm into .hack')
    arg_parser.add_argument('--dir',default=None,type=str)

    args = arg_parser.parse_args()

    if not args.dir:
        raise VMTranslatorException('please input a dir as target of translator')

    if args.dir and not os.path.exists(args.dir):
        raise VMTranslatorException('asm dir:{0} is not existed'.format(args.dir))
        
    if args.dir:
        process_dir(args.dir)