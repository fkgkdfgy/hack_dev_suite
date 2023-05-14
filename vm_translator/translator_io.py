#!/bin/python

import os
import sys
import argparse

class TextIO:
    def __init__(self,asm_file,hack_file):
        self.text_file = asm_file
        flow = open(asm_file,mode='r')
        self.lines = flow.readlines()
        self.count = 0
        self.file_to_write = open(hack_file,mode='w+')
        flow.close()

    def get_line(self):
        if self.count<len(self.lines):
            line = self.lines[self.count]
            self.count+=1
            return line
        else:
            return None
    
    def write_line(self,sentense):
        self.file_to_write.write(sentense)

    def close_write(self):
        self.file_to_write.close()

    def reset(self,asm_file,hack_file):
        self.close_write()
        self.__init__(asm_file,hack_file)

    def reset_line_count(self):
        self.count = 0

if __name__ == '__main__':
    test_io = TextIO('/home/vensin/hack_assembler/test_material/test_io.txt',
                     '/home/vensin/hack_assembler/test_material/test_io_result.txt')
    new_line = test_io.get_line()
    while new_line:
        print(new_line)
        new_line = test_io.get_line()