from utils import * 
import copy

class BaseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class BaseHandler:

    isTerminal = False
    label = ''

    def __init__(self, unstructed_xml=None):
        self.xml = ''
        self.symbol_table = {}
        self.parent_handler = None
        self.children = []
        if unstructed_xml:
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
    
    def toCode(self):
        return ''

    def registrateSymbolTable(self):
        for child in self.children:
            child.registrateSymbolTable()

    def searchVariable(self,symbol):
        if self.symbol_table and symbol in self.symbol_table:
            return self.symbol_table[symbol]
        
        if not self.parent_handler:
            raise BaseException('can not find symbol {0} in symbol table chain'.format(symbol))
        
        return self.parent_handler.searchVariable(symbol)

    def addChildren(self,children):
        for child in children:
            child.parent_handler = self
        self.children.extend(children)

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
            raise BaseException("something wrong with {0}, SimpleHandler can not process this, the word_and_type is {1}."\
                                .format(None if not unstructured_xml else unstructured_xml[0:5],self.word_and_type))

    def toXML(self):
        if self.word_and_type:
            return common_convert(self.word_and_type[1])(self.word_and_type[0])
        raise BaseException("self.word_and_type is not defined in SimpleHandler")
    
    def getWord(self):
        if self.word_and_type:
            return self.word_and_type[0]
        raise BaseException("self.word_and_type is not defined in SimpleHandler")
    
    def getWordType(self):
        if self.word_and_type:
            return self.word_and_type[1]
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
        BaseHandler.__init__(self,unstructed_xml)
    
    def toXML(self):
        self.xml = ''
        for child in self.children:
            self.xml += child.toXML()
        return BaseHandler.toXML(self)
    
    def toCode(self):
        code = ''
        for child in self.children:
            code += child.toCode()
        return code

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
        for index, check_component in enumerate(self.check_chain):
            item_name, handler = check_component
            try:
                original_unstructured_xml = unstructured_xml
                unstructured_xml = handler.processXML(unstructured_xml)
            except Exception as e:
                check_chain_item_names = [ '{0}: {1}'.format(index, check_component[0]) for index, check_component in enumerate(self.check_chain)]
                check_chain_to_show = '\n'.join(check_chain_item_names)
                error_component_to_show = '{0}: {1}'.format(index, item_name)
                process_unstructured_xml = ' '.join([item[0] for item in original_unstructured_xml][0:10])
                error_description = '\n'
                error_description += 'Handler Module: {0} \n'.format(self.label)
                error_description += 'DeeperError({1}): \n{0} \n'.format(e,self.label)
                error_description += 'DeeperError({0}) End \n'.format(self.label)
                error_description += 'Check Chains: \n{0} \n'.format(check_chain_to_show)
                error_description += 'Failed Component: \n{0} \n'.format(error_component_to_show)
                error_description += 'Process Unstructured XML: \n{0} \n'.format(process_unstructured_xml)
                raise BaseException(error_description)
            self.addChildren([handler])
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

        error_list = {}
        for handler in not_simple_handlers:
            try: 
                left_xml = handler.processXML(unstructured_xml)
                self.selected_candidate = handler
                self.addChildren([self.selected_candidate])
                return left_xml
            except Exception as e:
                error_list[handler.label] = e
                continue
        for handler in simple_handlers:
            try: 
                left_xml = handler.processXML(unstructured_xml)
                self.selected_candidate = handler
                self.addChildren([self.selected_candidate])
                return left_xml
            except Exception as e:
                error_list[handler.label] = e
                continue
        error_description = '\n'
        error_description += 'Handler Module: {0} \n'.format(self.label)
        error_description += 'Candidates Modules: \n{0} \n'.format('\n'.join([handler.label for handler in self.candidates.values()]))
        error_description += 'Error List: \n{0} \n'.format('\n'.join(['{0}: {1}'.format(label, error) for label, error in error_list.items()]))
        raise BaseException(error_description)

    def toXML(self):
        self.xml=''
        if self.selected_candidate:
            self.xml = self.selected_candidate.toXML()
            return BaseHandler.toXML(self)
        raise BaseException("SelectHandler has not selected a candidate")
    
    def toCode(self):
        return self.selected_candidate.toCode()