from base_module import *
from expression_modules import *

class StatementException(Exception):
    pass


class LetStatementHandler(BaseHandler):
    isTerminal = False
    label = 'letStatement'

    def processXML(self, unstructured_xml):
        self.xml = ''
        for word_and_type in unstructured_xml:
            word = word_and_type[0]
            word_type = word_and_type[1]
            if word_type == 'keyword':
                self.xml += PsedoHandler(word_and_type).toXML()
            elif word_type == 'identifier':
                self.xml += PsedoHandler(word_and_type).toXML()
            elif word_type == 'symbol':
                if word == '=':
                    self.xml += PsedoHandler(word_and_type).toXML()
                    self.xml += ExpressionHandler(unstructured_xml[unstructured_xml.index(word_and_type)+1:]).toXML()
                elif word == '[':
                    self.xml += PsedoHandler(word_and_type).toXML()
                    self.xml += ExpressionHandler(unstructured_xml[unstructured_xml.index(word_and_type)+1:]).toXML()
                elif word == ';':
                    self.xml += PsedoHandler(word_and_type).toXML()
                else:
                    raise StatementException('Unknown symbol: {0}'.format(word))
            else:
                raise StatementException('Unknown word type: {0}'.format(word_type))

    
class StatementHandler(BaseHandler):    
    isTerminal = False
    label = 'statement'

    check_function = {
        'letStatement': ()
    }

    def processXML(self, unstructured_xml):
        self.xml = ''
        for statement in unstructured_xml:
            statement_type = statement[0].text
            if statement_type == 'letStatement':
                self.xml += LetHandler(statement).toXML()
            elif statement_type == 'ifStatement':
                self.xml += IfHandler(statement).toXML()
            elif statement_type == 'whileStatement':
                self.xml += WhileHandler(statement).toXML()
            elif statement_type == 'doStatement':
                self.xml += DoHandler(statement).toXML()
            elif statement_type == 'returnStatement':
                self.xml += ReturnHandler(statement).toXML()
            else:
                raise StatementException('Unknown statement type: {0}'.format(statement_type))