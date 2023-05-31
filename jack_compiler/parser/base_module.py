from utils import * 


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
