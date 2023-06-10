
import os
import sys

sys.path.append(os.path.dirname(__file__))

from expression_modules import *
from statement_modules import *
from class_modules import *

class GrammarException(Exception):
    pass

class ProgramHandler(BaseHandler):

    def processXML(self, unstructured_xml):
        self.children = []
        while unstructured_xml:
            try:
                class_handler = ClassHandler()
                unstructured_xml = class_handler.processXML(unstructured_xml)
                self.addChildren([class_handler])
            except:
                break
        return unstructured_xml
    
    def searchVariable(self, symbol):
        class_names = [child.getClassName() for child in self.children]
        # class_names 还需要添加一些BuiltIn Class
        class_names.extend(['Array','String','Math','Output','Screen','Keyboard','Memory','Sys'])
        if symbol in class_names:
            return [None,'class',None]

    def toCode(self):
        code = ''
        for child in self.children:
            code += child.toCode()
        return code

    def toXML(self):
        xml = ''
        for child in self.children:
            xml += child.toCode()
        return xml

class Grammar:

    def __init__(self) :
        self.class_list = []
        self.xml = ''
        self.program_handler = ProgramHandler()

    def processXML(self, unstructured_tokens):
        unstructured_tokens = self.program_handler.processXML(unstructured_tokens)
        return self.program_handler.toXML(), self.program_handler.toCode()