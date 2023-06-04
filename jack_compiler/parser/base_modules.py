from utils import * 
import copy

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
        if not unstructured_xml:
            return -1
        try:
            left_xml = self.processXML(unstructured_xml)
        except Exception as e:
            return -1
        return len(unstructured_xml) - len(left_xml)

    def isTarget(self,unstructured_xml):
        if not unstructured_xml:
            return False
        try:
            left_xml = self.processXML(unstructured_xml)
        except Exception as e:
            return False
        if not left_xml:
            return True
        
class SimpleHandler(BaseHandler):
    isTerminal = False
    label = 'simple'
    
    def __init__(self, unstructed_xml=None):
        self.word_and_type = None
        BaseHandler.__init__(self,unstructed_xml)

    def processXML(self, unstructured_xml):
        if self.findTarget(unstructured_xml)>0:
            self.word_and_type = unstructured_xml[0]
            return unstructured_xml[1:]
        else:
            raise BaseException("something wrong with {0}, SimpleHandler can not process this.".format(None if not unstructured_xml else unstructured_xml[0]))

    def toXML(self):
        if self.word_and_type:
            return common_convert(self.word_and_type[1])(self.word_and_type[0])
        raise BaseException("self.word_and_type is not defined in SimpleHandler")


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

class NameHandler(SimpleHandler):
    isTerminal = False
    label = 'name'

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

    empty_allowed = False    

    def __init__(self,unstructed_xml=None):
        self.children = []
        if isinstance(self.base_handler,list):
            for handler in self.base_handler:
                if isinstance(handler,EmptyHandler):
                    raise BaseException('base_handler can not be EmptyHandler')
        if isinstance(self.base_handler,EmptyHandler):
            raise BaseException('base_handler can not be EmptyHandler')
        if len(self.options_handlers) == 0:
            raise BaseException('options_handlers can not be empty')
        for handler in self.options_handlers:
            if isinstance(handler,EmptyHandler):
                raise BaseException('options_handlers can not have EmptyHandler')
        super().__init__(unstructed_xml)
    
    def processXML(self, unstructured_xml):
        self.children = []
        if isinstance(self.base_handler,list):
            pair_children = []
            unprocessed_xml = unstructured_xml
            for handler in self.base_handler:
                try:
                    unstructured_xml = handler.processXML(unstructured_xml)
                    pair_children.append(handler)
                except Exception as e:
                    if not self.empty_allowed:
                        raise BaseException('MultiUnitHandler can not find base_handler in {0}'.format(unstructured_xml))
                    return unprocessed_xml
            self.children.extend(pair_children)
        else:
            try:
                base_handler = copy.deepcopy(self.base_handler)
                unstructured_xml = base_handler.processXML(unstructured_xml)
                self.children.append(base_handler)
            except Exception as e:
                if not self.empty_allowed:
                    raise BaseException('MultiUnitHandler can not find base_handler in {0}'.format(unstructured_xml))
                return unstructured_xml
        while unstructured_xml:
            try:
                pair_children = []
                unprocessed_xml = unstructured_xml
                for option_handler in self.options_handlers:
                    handler = copy.deepcopy(option_handler)
                    unstructured_xml = handler.processXML(unstructured_xml)
                    pair_children.append(handler)
                self.children.extend(pair_children)
            except Exception as e:
                unstructured_xml = unprocessed_xml
                break
        return unstructured_xml
    
    def toXML(self):
        self.xml = ''
        for child in self.children:
            self.xml += child.toXML()
        return BaseHandler.toXML(self)

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

class SequenceHandler(BaseHandler):
    isTerminal = False
    # check_chain 内部是多个handler
    check_chain = []
    valid_num = []
    children = []

    def __init__(self, unstructed_xml=None):
        super().__init__(unstructed_xml)

    def processXML(self, unstructured_xml):
        self.children = []
        for check_component in self.check_chain:
            item_name, handler = check_component
            try:
                unstructured_xml = handler.processXML(unstructured_xml)
            except Exception as e:
                raise BaseException('Sequence Component {0} processXML error: {0} '.format(item_name, e))
            self.children.append(handler)
        return unstructured_xml

    def toXML(self):
        self.xml = ''
        for child in self.children:
            self.xml += child.toXML()
        return BaseHandler.toXML(self)
    
class SelectHandler(BaseHandler):
    isTerminal = False
    label = 'term'

    candidates = {}

    def __init__(self, unstructured_xml=None):
        self.selected_candidate = None
        BaseHandler.__init__(self, unstructured_xml)

    def processXML(self, unstructured_xml):
        self.selected_candidate = None
        
        simple_handlers = [ handler for handler in self.candidates.values() if isinstance(handler,SimpleHandler)]
        not_simple_handlers = [ handler for handler in self.candidates.values() if not isinstance(handler,SimpleHandler)]

        for handler in not_simple_handlers:
            try: 
                left_xml = handler.processXML(unstructured_xml)
                self.selected_candidate = handler
                return left_xml
            except Exception as e:
                continue
        for handler in simple_handlers:
            try: 
                left_xml = handler.processXML(unstructured_xml)
                self.selected_candidate = handler
                return left_xml
            except Exception as e:
                continue

        raise BaseException("SelectHandler can not find a valid candidate")

    def toXML(self):
        self.xml=''
        if self.selected_candidate:
            self.xml = self.selected_candidate.toXML()
            return BaseHandler.toXML(self)
        raise BaseException("SelectHandler has not selected a candidate")