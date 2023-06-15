
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
    
    def registrateSymbolTable(self):
        for child in self.children:
            child.registrateSymbolTable()

        # 检查是否存在重名的 class
        class_names = [child.getClassName() for child in self.children]
        if len(class_names) != len(set(class_names)):
            raise GrammarException('find a class name repeated')
        
        # 获取所有child 的 symbol table
        static_symbol_dict = {}
        count = 0
        for child in self.children:
            for var_name, info_tuple in child.symbol_table:
                child_class_name = child.getClassName()
                static_name = '{0}.{1}'.format(child_class_name, var_name)
                if static_name in static_symbol_dict:
                    raise GrammarException('find a var_name{0} referred by multi_variables'.format(static_name))
                static_symbol_dict[static_name] = copy.deepcopy(info_tuple)
                static_symbol_dict[static_name][2] = count
                count +=1 

        # 将static_symbol_dict 注册到所有的 symbol_table 中
        for child in self.children:
            for var_name, info_tuple in static_symbol_dict.items():
                child_class_name = child.getClassName()
                static_name = '{0}.{1}'.format(child_class_name, var_name)
                child.symbol_table[var_name] = static_symbol_dict[static_name]          
        return

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