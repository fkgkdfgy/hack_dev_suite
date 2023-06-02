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
        if self.isTerminal:
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

class SimpleHandler(BaseHandler):
    isTerminal = False
    label = 'simple'

    def processXML(self, unstructured_xml):
        self.xml = ''
        if not len(unstructured_xml) == 1:
            raise BaseException("simple handler only process one word")
        if self.isTarget(unstructured_xml):
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])
            return self.toXML()
        else:
            raise BaseException("something wrong with {0}".format(unstructured_xml))

class SupportHandler(SimpleHandler):
    isTerminal = False
    label = 'support'

    def __init__(self, target_word_and_type):
        if not target_word_and_type or not isinstance(target_word_and_type, tuple) or len(target_word_and_type) != 2:
            raise BaseException('SupportHandler must have one word and type and input must be tuple')
        self.target_word_and_type = target_word_and_type
        super().__init__([target_word_and_type])

    def findTarget(self, unstructured_xml):
        if unstructured_xml and unstructured_xml[0] == self.target_word_and_type:
            return 1
        return -1

class NameHandler(BaseHandler):
    isTerminal = False
    label = 'name'

    def processXML(self, unstructured_xml):
        self.xml = ''
        if self.isTarget(unstructured_xml):
            self.xml += common_convert('identifier')(unstructured_xml[0][0])
            return self.toXML()
        else:
            raise BaseException("something wrong with {0}".format(unstructured_xml))
    
    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        if unstructured_xml[0][1] == 'identifier':
            return 1
        return -1

# 这是个辅助的handler 用于处理多种重复的情况
class MultiUnitHandler(BaseHandler):
    isTerminal = False
    label = 'multiUnit'

    def __init__(self, base_handler, options_handlers,unstructed_xml=None):
        self.base_handler = base_handler
        self.options_handlers = options_handlers
        super().__init__(unstructed_xml)
    
    def processXML(self, unstructured_xml):
        self.xml = ''
        if self.isTarget(unstructured_xml):
            find_length = 0
            if self.base_handler:
                find_length = self.findBaseTarget(unstructured_xml)
                self.xml = self.base_handler.processXML(unstructured_xml[:find_length])
                if find_length == len(unstructured_xml):
                    return self.toXML()
            left_xml = unstructured_xml[find_length:]
            while left_xml:
                for handler in self.options_handlers:
                    unit_length = handler.findTarget(left_xml)
                    self.xml += handler.processXML(left_xml[:unit_length])
                    left_xml = left_xml[unit_length:]
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
        left_xml = unstructured_xml
        for handler in self.options_handlers:
            unit_length = handler.findTarget(left_xml)
            if unit_length <0:
                return -1
            find_length += unit_length
            left_xml = left_xml[unit_length:]
        next_find_length = self.findOptionTarget(left_xml)
        return find_length if next_find_length < 0 else find_length + next_find_length
    
class EmptyHandler(BaseHandler):
    isTerminal = False
    label = 'empty'

    def __init__(self, unstructed_xml=None):
        self.xml = ''

    def processXML(self, unstructured_xml):
        self.xml = '' 
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

def check_chain_with_func_list(left_xml, handler_list):
    find_flag = [False] * len(handler_list)
    if not handler_list:
        raise BaseException('check_chain must have at least one function')
    
    for index,handler in enumerate(handler_list):
        find_length = handler.findTarget(left_xml)
        if find_length >=0:
            left_xml = left_xml[find_length:]
            find_flag[index] = True
        else:
            break
    return find_flag


class SequenceHandler(BaseHandler):
    isTerminal = False
    # check_chain 内部是多个handler
    check_chain = []
    valid_num = []

    def __init__(self, unstructed_xml=None):
        super().__init__(unstructed_xml)

    def processXML(self, unstructured_xml):
        self.xml = ''
        if self.isTarget(unstructured_xml):
            find_flag = check_chain_with_func_list(unstructured_xml, [ handler for item_name, handler in self.check_chain])
            for index,function_pair in enumerate(self.check_chain):
                item_name, handler = function_pair
                if find_flag[index]:
                    find_length = handler.findTarget(unstructured_xml)
                    self.xml += handler.processXML(unstructured_xml[:find_length])
                    unstructured_xml = unstructured_xml[find_length:]
                else:
                    break
            return self.toXML()
        else:
            raise BaseException("SequenceHandler: unstructured_xml is not a unit")

    def findTarget(self,unstructured_xml):
        find_flag = check_chain_with_func_list(unstructured_xml, [ handler for item_name, handler in self.check_chain])
        # 如果 find_flag 中的 True 的个数不在 valid_num 中，返回 False
        if find_flag.count(True) not in self.valid_num:
            return -1
        else:
            find_length = 0
            for index,function_pair in enumerate(self.check_chain):
                item_name, handler = function_pair
                if find_flag[index]:
                    find_length += handler.findTarget(unstructured_xml[find_length:])
                else:
                    break
            return find_length   
        
class SelectHandler(BaseHandler):
    isTerminal = False
    label = 'term'

    candidates = {}

    def __init__(self, unstructured_xml=None):
        BaseHandler.__init__(self, unstructured_xml)

    def processXML(self, unstructured_xml):
        self.xml = ''
        if self.isTarget(unstructured_xml):
            for handler in self.candidates.values():
                if handler.isTarget(unstructured_xml):
                    self.xml = handler.processXML(unstructured_xml)
                    return self.toXML()
        else:
            raise BaseException("something wrong with {0}".format(unstructured_xml))
    
    # 如果能从unstructured_xml中提取出一个Term，就返回第一个诊断是Term的end_index, 否则返回0
    def isTarget(self,unstructured_xml):
        for handler in self.candidates.values():
            if handler.isTarget(unstructured_xml):
                return True
        return False
    
    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        for i in range(len(unstructured_xml)+1)[::-1]:
            if self.isTarget(unstructured_xml[0:i]):
                return i
        return -1    