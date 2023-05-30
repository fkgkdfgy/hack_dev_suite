from utils import *

class BaseHandler:

    isTerminal = False
    label = ''

    def __init__(self, parser):
        self.xml = ''
    
    def toXML(self):
        result_xml = ''
        if not self.isTerminal:
            result_xml = '<{0}>\n'.format(self.label)
            result_xml += self.xml
            result_xml += '</{0}>\n'.format(self.label)
        else:
            result_xml = self.xml
        return result_xml
    
    def processXML(self,unstructured_xml):
        pass