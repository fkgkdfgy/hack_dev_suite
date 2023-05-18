#!/bin/python

import os
import sys
import argparse

class VMIOException(Exception):
    pass



class TextIO:
    def __init__(self,asm_file,hack_file):
        self.text_file = asm_file
        self.lines = []
        if self.text_file:
            flow = open(asm_file,mode='r')
            self.lines = flow.readlines()
            flow.close()
        self.count = 0
        self.file_to_write = None
        if hack_file:
            self.file_to_write = open(hack_file,mode='w+')

    def get_line(self):
        if not self.lines:
            raise VMIOException('try to get line from a empty IO, please check IO text_file{0}'.format(self.text_file))
        if self.count<len(self.lines):
            line = self.lines[self.count]
            self.count+=1
            return line
        else:
            return None
    
    def write_line(self,sentense):
        if not self.file_to_write:
            raise VMIOException('try to write line from a empty IO, please check IO file_to_write{0}'.format(self.file_to_write))
        if self.file_to_write:
            self.file_to_write.write(sentense)

    def close_write(self):
        if self.file_to_write:
            self.file_to_write.close()

    def reset(self,asm_file,hack_file):
        self.close_write()
        self.__init__(asm_file,hack_file)

    def reset_line_count(self):
        self.count = 0
    
    def get_all_lines(self):
        return self.lines

if __name__ == '__main__':
    test_io = TextIO('/home/vensin/hack_assembler/test_material/test_io.txt',
                     '/home/vensin/hack_assembler/test_material/test_io_result.txt')
    new_line = test_io.get_line()
    while new_line:
        print(new_line)
        new_line = test_io.get_line()