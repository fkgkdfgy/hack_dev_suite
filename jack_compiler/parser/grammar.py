
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
        while unstructured_tokens:
            find_length = self.class_handler.findTarget(unstructured_tokens)
            if find_length <0:
                raise GrammarException('Cannot parse the following tokens: %s' % unstructured_tokens[:10])
            structured_xml = self.class_handler.processXML(unstructured_tokens[:find_length])
            self.xml += structured_xml
            unstructured_tokens = unstructured_tokens[find_length:]
        return self.xml