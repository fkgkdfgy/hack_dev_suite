

import sys
import os
import argparse
import translator_io 
import translator_parser
from translator import Translator

from utilis import *

def process_file(codes,file_name):
    sentense_parser = translator_parser.Parser()
    translator = Translator(file_name)

    result_codes = ''

    for line in codes:
        new_line = line[0:-1]
        print(new_line)
        segments = sentense_parser.Process(new_line)
        print(segments)
        result = translator.process(segments)
        if result:
            result_codes += result

    return result_codes

def process_dir(dir_path):

    def split_files_and_dirs(dir_path):

        def IsDir(abs_path):
            return os.path.isdir(abs_path)
        
        def IsVMFile(abs_path):
            if os.path.isfile(abs_file_name):
                split_names= os.path.basename(file_name).split('.')
                if split_names and split_names[-1] == 'vm':
                    return True
            return False

        file_list,dir_list,abs_file_list,abs_dir_list = [],[],[],[]
        files = os.listdir(dir_path)
        
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

    if not file_list:
        return 

    # 先处理 Sys.vm 这个文件
    total_codes = ''
    if 'Sys.vm' in file_list:
        abs_sys_file = os.path.join(dir_path,'Sys.vm')
        data_io = translator_io.TextIO(abs_sys_file, None)   
        file_list.remove('Sys.vm')

        codes = data_io.get_all_lines()
        result_codes = process_file(codes,'Sys')
        total_codes += result_codes

    for file in file_list:    
        abs_file = os.path.join(dir_path,file)
        data_io = translator_io.TextIO(abs_file, None)   

        codes = data_io.get_all_lines()
        result_codes = process_file(codes,file[0:-3])
        total_codes += result_codes
    
    data_io = translator_io.TextIO(None,os.path.join(dir_path,'Sys.asm'))
    for code in total_codes:
        data_io.write_line(code)
    data_io.close_write()

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