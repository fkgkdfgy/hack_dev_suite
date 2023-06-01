from utils import * 

class BaseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class BaseHandler:

    isTerminal = False
    label = ''

    def __init__(self, unstructed_xml=None):
        if unstructed_xml:
            self.xml = ''
            self.processXML(unstructed_xml)
        else:
            self.xml = ''
    
    def toXML(self):
        result_xml = ''
        if not self.isTerminal:
            result_xml = '<{0}>'.format(self.label)
            result_xml += self.xml
            result_xml += '</{0}>'.format(self.label)
        else:
            result_xml = self.xml
        return result_xml
    
    def processXML(self,unstructured_xml):
        pass

class PsedoHandler(BaseHandler):
    isTerminal = True
    label = 'psedo'

    def processXML(self, word_and_type):
        self.xml = common_convert(word_and_type[1])(word_and_type[0])



class SupportHandler(BaseHandler):
    isTerminal = True
    label = 'support'

    def processXML(self, word_and_type):
        self.xml = common_convert(word_and_type[1])(word_and_type[0])

class NameHandler(BaseHandler):
    isTerminal = True
    label = 'name'

    def processXML(self, unstructured_xml):
        if NameHandler.isName(unstructured_xml):
            self.xml += common_convert('identifier')(unstructured_xml[0][0])
        else:
            raise BaseException("something wrong with {0}".format(unstructured_xml))

    @common_empty_check
    def isName(unstructured_xml):
        if len(unstructured_xml) == 1 and unstructured_xml[0][1] == 'identifier':
            return True
        return False
    
    def findName(unstructured_xml):
        if not unstructured_xml:
            return -1
        if NameHandler.isName(unstructured_xml[0:1]):
            return 1
        return -1
    

class Unit:
    def __init__(self,name, find_function, is_function, transform_function):
        self.name = name
        self.find_function = find_function
        self.is_function = is_function
        self.transform_function = transform_function

# 这是个辅助的handler 用于处理多种重复的情况
class MultiUnitHandler(BaseHandler):
    isTerminal = True
    label = 'multiUnit'

    def __init__(self, base_unit, option_units,unstructed_xml=None):
        self.base_unit = base_unit
        self.option_units = option_units
        super().__init__(unstructed_xml)
    
    def processXML(self, unstructured_xml):
        if self.isMultiUnit(unstructured_xml):
            find_length = 0
            if self.base_unit:
                find_length = self.findBaseUnit(unstructured_xml)
                self.xml = self.base_unit.transform_function(unstructured_xml[:find_length])
            for unit in self.option_units:
                unit_length = unit.find_function(unstructured_xml[find_length:])
                self.xml += unit.transform_function(unstructured_xml[find_length:find_length+unit_length])
                find_length += unit_length
        else:
            raise BaseException("MultiUnitHandler: unstructured_xml is not a multi unit")

    @common_empty_check
    def isMultiUnit(self,unstructured_xml):
        if self.findMultiUnit(unstructured_xml) == len(unstructured_xml):
            return True
        return False

    # 使用 base_unit 来寻找开始的结果，如果找到了，就使用option_units来寻找后续的结果
    # 如果没有找到，就返回-1
    # 如果 base_unit == None , 就使用 option_units 来寻找结果
    # 如果 unstructured_xml == 0 , 就返回-1
    def findMultiUnit(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        if self.base_unit:
            base_unit_length = self.findBaseUnit(unstructured_xml)
            if base_unit_length < 0:
                return -1
        else:
            base_unit_length = 0
        option_units_length = self.findOptionUnits(unstructured_xml[base_unit_length:])
        return base_unit_length if option_units_length < 0 else base_unit_length + option_units_length

    def findBaseUnit(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        if self.base_unit:
            return self.base_unit.find_function(unstructured_xml)
        return 0
    
    def findOptionUnits(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        find_length = 0
        for unit in self.option_units:
            unit_length = unit.find_function(unstructured_xml)
            if unit_length <0:
                return -1
            find_length += unit_length
        next_find_length = self.findOptionUnits(unstructured_xml[find_length:])
        return find_length if next_find_length < 0 else find_length + next_find_length
