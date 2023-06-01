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

    def findTarget(self,unstructured_xml):
        pass

    def isTarget(self,unstructured_xml):
        if self.findTarget(unstructured_xml) == len(unstructured_xml):
            return True
        return False

class SupportHandler(BaseHandler):
    isTerminal = True
    label = 'support'

    def processXML(self, word_and_type):
        self.xml = common_convert(word_and_type[1])(word_and_type[0])

class NameHandler(BaseHandler):
    isTerminal = True
    label = 'name'

    def processXML(self, unstructured_xml):
        if NameHandler.isTarget(unstructured_xml):
            self.xml += common_convert('identifier')(unstructured_xml[0][0])
        else:
            raise BaseException("something wrong with {0}".format(unstructured_xml))
    
    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        if unstructured_xml[0][1] == 'identifier':
            return True
        return -1

# 这是个辅助的handler 用于处理多种重复的情况
class MultiUnitHandler(BaseHandler):
    isTerminal = True
    label = 'multiUnit'

    def __init__(self, base_handler, options_handlers,unstructed_xml=None):
        self.base_handler = base_handler
        self.options_handlers = options_handlers
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
            return self.xml
        else:
            raise BaseException("MultiUnitHandler: unstructured_xml is not a multi unit")

    def isTarget(self,unstructured_xml):
        if self.findMultiUnit(unstructured_xml) == len(unstructured_xml):
            return True
        return False

    # 使用 base_unit 来寻找开始的结果，如果找到了，就使用option_units来寻找后续的结果
    # 如果没有找到，就返回-1
    # 如果 base_unit == None , 就使用 option_units 来寻找结果
    # 如果 unstructured_xml == 0 , 就返回-1
    def findTarget(self,unstructured_xml):
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
    
class EmptyHandler(BaseHandler):
    isTerminal = True
    label = 'empty'

    def __init__(self, unstructed_xml=None):
        self.xml = ''

    def processXML(self, unstructured_xml):
        return self.toXML()

    def toXML(self):
        return ''
    
    def isTarget(self,unstructured_xml):
        if not unstructured_xml:
            return True
        return False
    
    # 因为是找空白所以永远不可能失败
    def findTarget(self,unstructured_xml):
        return 0
    
class OrHanlder(BaseHandler):
    isTerminal = True
    label = 'or'
    def __init__(self, handler1, handler2, unstructed_xml=None):
        self.handler1 = handler1
        self.handler2 = handler2
        super().__init__(unstructed_xml)

    def processXML(self, unstructured_xml):
        self.xml = ''
        if self.isTarget(unstructured_xml):
            if self.isTarget1(unstructured_xml):
                self.xml = self.handler1.processXML(unstructured_xml)
            else:
                self.xml = self.handler2.processXML(unstructured_xml)
            return self.toXML()
        else:
            raise BaseException("OrHandler: unstructured_xml is not a unit")

    def isTarget1(self,unstructured_xml):
        if self.handler1.isTarget(unstructured_xml):
            return True
        return False

    def isTarget2(self,unstructured_xml):
        if self.handler2.isTarget(unstructured_xml):
            return True
        return False

    def isTarget(self,unstructured_xml):
        if self.isTarget1(unstructured_xml) and self.isTarget2(unstructured_xml):
            raise BaseException("OrHandler: find two units")
        if self.isTarget1(unstructured_xml) or self.isTarget2(unstructured_xml):
            return True
        return False

    def findTarget1(self,unstructured_xml):
        return self.handler1.findTarget(unstructured_xml)

    def findTarget2(self,unstructured_xml):
        return self.handler2.findTarget(unstructured_xml)
    
    def findTarget(self,unstructured_xml):
        find_length1 = self.findTarget1(unstructured_xml)
        find_length2 = self.findTarget2(unstructured_xml)
        if find_length1 < 0 and find_length2 < 0:
            return -1
        if find_length1 > 0 and find_length2 > 0:
            raise BaseException("OrHandler: find two units")
        if find_length1 < 0:
            return find_length2
        if find_length2 < 0:
            return find_length1

