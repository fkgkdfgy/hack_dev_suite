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
        return self.toXML()

class NameHandler(BaseHandler):
    isTerminal = True
    label = 'name'

    def processXML(self, unstructured_xml):
        if NameHandler.isTarget(unstructured_xml):
            self.xml += common_convert('identifier')(unstructured_xml[0][0])
            return self.toXML()
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
        if self.isTarget(unstructured_xml):
            find_length = 0
            if self.base_handler:
                find_length = self.findBaseTarget(unstructured_xml)
                self.xml = self.base_handler.processXML(unstructured_xml[:find_length])
            for handler in self.options_handlers:
                unit_length = handler.findTarget(unstructured_xml[find_length:])
                self.xml += handler.processXML(unstructured_xml[find_length:find_length+unit_length])
                find_length += unit_length
            return self.toXML()
        else:
            raise BaseException("MultiUnitHandler: unstructured_xml is not a multi unit")

    # 使用 base_unit 来寻找开始的结果，如果找到了，就使用option_units来寻找后续的结果
    # 如果没有找到，就返回-1
    # 如果 base_unit == None , 就使用 option_units 来寻找结果
    # 如果 unstructured_xml == 0 , 就返回-1
    def findTarget(self,unstructured_xml):
        if self.base_handler:
            base_unit_length = self.findBaseTarget(unstructured_xml)
            if base_unit_length < 0:
                return -1
        else:
            base_unit_length = 0
        option_units_length = self.findOptionTarget(unstructured_xml[base_unit_length:])
        return base_unit_length if option_units_length < 0 else base_unit_length + option_units_length

    def findBaseTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        if self.base_handler:
            return self.base_handler.findTarget(unstructured_xml)
        return 0
    
    def findOptionTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        find_length = 0
        for handler in self.options_handlers:
            unit_length = handler.findTarget(unstructured_xml)
            if unit_length <0:
                return -1
            find_length += unit_length
        next_find_length = self.findOptionTarget(unstructured_xml[find_length:])
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

def check_chain_with_func_list(left_xml, func_list):
    find_flag = [False] * len(func_list)
    if not func_list:
        raise BaseException('check_chain must have at least one function')
    for index,func in enumerate(func_list):
        find_length = func(left_xml)
        if find_length >=0:
            left_xml = left_xml[find_length:]
            find_flag[index] = True
        else:
            break
    return find_flag


class SequenceHandler(BaseHandler):

    check_chain = []
    valid_num = []

    def __init__(self, unstructed_xml=None):
        super().__init__(unstructed_xml)

    def processXML(self, unstructured_xml):
        self.xml = ''
        if self.isTarget(unstructured_xml):
            find_flag = check_chain_with_func_list(unstructured_xml, [ find_function for _,find_function,_ in self.check_chain])
            for index,function_pair in enumerate(self.check_chain):
                item_name, find_function, process_function = function_pair
                if find_flag[index]:
                    find_length = find_function(unstructured_xml)
                    self.xml += process_function(unstructured_xml[:find_length])
                    unstructured_xml = unstructured_xml[find_length:]
                else:
                    break
        else:
            raise BaseException("SequenceHandler: unstructured_xml is not a unit")

    def findTarget(self,unstructured_xml):
        find_flag = check_chain_with_func_list(unstructured_xml, [ find_function for _,find_function,_ in self.check_chain])
        # 如果 find_flag 中的 True 的个数不在 valid_num 中，返回 False
        if find_flag.count(True) not in self.valid_num:
            return -1
        else:
            find_length = 0
            for index,function_pair in enumerate(self.check_chain):
                item_name, find_function, process_function = function_pair
                if find_flag[index]:
                    find_length += find_function(unstructured_xml[find_length:])
                else:
                    break
            return find_length   