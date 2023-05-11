

import sys
import os
import assembler_parser 
import assembler_io
import assembler_symboltable
import assembler_translator

from utilis import *



if __name__ == '__main__':
    asm_file = sys.argv[1]
    hack_file = sys.argv[1]+'.hack'

    data_io = assembler_io.TextIO(asm_file,hack_file)
    sentense_parser = assembler_parser.Parser()
    symboltable = assembler_symboltable.SymbolTable()
    translator = assembler_translator.Translator()

    # 
    new_line = data_io.get_line()
    while new_line:
        new_line = new_line[0:-1]
        segments = sentense_parser.Process(new_line)
        symboltable.DetectLabels(segments)
        new_line = data_io.get_line()
    data_io.reset_line_count()

    # 
    new_line = data_io.get_line()
    while new_line:
        new_line = new_line[0:-1]
        segments = sentense_parser.Process(new_line)
        symboltable.DetectVariable(segments)
        new_line = data_io.get_line()
    data_io.reset_line_count()

    
    new_line = data_io.get_line()
    while new_line:
        new_line = new_line[0:-1]
        segments = sentense_parser.Process(new_line)
        print(segments)
        symboltable.DetectValueofLabel(segments)
        new_line = data_io.get_line()
    print('variable',symboltable.variable)
    print('label',symboltable.label)

    data_io.reset_line_count()

    new_line = data_io.get_line()
    while new_line:
        print(new_line)
        new_line = new_line[0:-1]
        segments = sentense_parser.Process(new_line)
        print(segments)
        new_segments = symboltable.Process(segments)
        print(new_segments)
        binary = translator.Process(new_segments)
        new_line = data_io.get_line()
        if binary:
            data_io.write_line(binary+"\n")
        
    
    data_io.close_write()