
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
        self.class_handler = ClassHandler()
        self.xml = ''

    def processXML(self, unstructured_tokens):
        self.xml = ''
        print(unstructured_tokens)
        while unstructured_tokens:
            class_handler = ClassHandler()
            unstructured_tokens = class_handler.processXML(unstructured_tokens)
            self.xml += class_handler.toXML()
        return self.xml