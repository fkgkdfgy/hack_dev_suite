
import os
import sys

sys.path.append(os.path.dirname(__file__))

from expression_modules import *
from statement_modules import *
from class_modules import *

class GrammarException(Exception):
    pass


class Grammar:

    def __init__(self) :
        self.class_list = []
        self.xml = ''

    def processXML(self, unstructured_tokens):
        print(unstructured_tokens)
        while unstructured_tokens:
            class_handler = ClassHandler()
            unstructured_tokens = class_handler.processXML(unstructured_tokens)
            self.class_list.append(class_handler)
        return self.toXML()

    def toXML(self):
        result = ''
        for class_handler in self.class_list:
            result += class_handler.toXML()
        return result
    
    def toCode(self):
        result = ''
        for class_handler in self.class_list:
            result += class_handler.toCode()
        return result
