import os
import sys
import argparse

from text_io import TextIO
from tokenizer import Tokenizer
from grammar import Grammar

if __name__ == '__main__':
    
    abs_file_path = ''
    structured_xml_path = ''
    
    # text_io = TextIO(abs_file_path,structured_xml_path)
    tokenizer = Tokenizer()
    grammar = Grammar()
    
    # lines = text_io.get_all_lines()

    text = '''
    // This file is part of www.nand2tetris.org
    // and the book "The Elements of Computing Systems"
    // by Nisan and Schocken, MIT Press.
    // File name: projects/10/ArrayTest/Main.jack

    // (identical to projects/09/Average/Main.jack)

    // ** Computes the average of a sequence of integers. */
    class Main {
        function void main() {
            var Array a;
            var int length;
            var int i, sum;
        
        let length = Keyboard.readInt("HOW MANY NUMBERS? ");
        let a = Array.new(length);
        let i = 0;
        
        while (i < length) {
            let a[i] = Keyboard.readInt("ENTER THE NEXT NUMBER: ");
            let i = i + 1;
        }
        
        let i = 0;
        let sum = 0;
        
        while (i < length) {
            let sum = sum + a[i];
            let i = i + 1;
        }
        
        do Output.printString("THE AVERAGE IS: ");
        do Output.printInt(sum / length);
        do Output.println();
        
        return;
        }
    }   
    '''

    total_unstructured_xml = []
    lines = text.split('\n')
    for line in lines:
        _,unstructured_xml = tokenizer.processLine(line)
        total_unstructured_xml.extend(unstructured_xml)
    print('total unstructured xml : \n{0}'.format(total_unstructured_xml))
    structured_xml = grammar.processXML(total_unstructured_xml)

