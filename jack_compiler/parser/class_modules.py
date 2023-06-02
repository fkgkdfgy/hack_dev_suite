from utils import *
from base_modules import *
from expression_modules import *
from statement_modules import *

class ClassException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ClassNameHandler(NameHandler):
    label = 'className'

class SubroutineNameHandler(NameHandler):
    label = 'subroutineName'

class TypeHandler(SimpleHandler):
    isTerminal = False
    label = 'type'

    def findTarget(self,unstructured_xml):
        if not unstructured_xml:
            return -1
        if unstructured_xml[0][0] in ['int','char','boolean'] or VarNameHandler().isTarget(unstructured_xml[0:1]):
            return 1
        return -1

# verDec 的结构是 type varName (, varName)* ;
class VarDecHandler(SequenceHandler):
    isTerminal = True
    label = 'varDec'

    @property
    def check_chain(self):
        if not hasattr(self,'_check_chain'):
            self._check_chain = [
                ('var',SupportHandler(('var', 'keyword'))),
                ('type',TypeHandler()),
                ('mutli_varName',MultiUnitHandler(base_handler=VarNameHandler(),options_handlers=[SupportHandler((',','symbol')),VarNameHandler()])),
                (';',SupportHandler((';', 'symbol')))
            ]
        return self._check_chain

    @property
    def valid_num(self):
        if not hasattr(self,'_valid_num'):
            self._valid_num = [4]
        return self._valid_num

class StaticOrFieldHandler(SelectHandler):
    isTerminal = False
    label = 'static_or_field'
    @property
    def candidates(self):
        if not hasattr(self,'_candidates'):
            self._candidates = {
                'static':SupportHandler(('static', 'keyword')),
                'field':SupportHandler(('field', 'keyword'))
            }
        return self._candidates

# classVarDec 的结构是 (static|field) type varName (, varName)* ;
class ClassVarDecHandler(SequenceHandler):
    isTerminal = True
    label = 'classVarDec'
    @property
    def check_chain(self):
        if not hasattr(self,'_check_chain'):
            self._check_chain = [
                ('static_or_field',StaticOrFieldHandler()),
                ('type',TypeHandler()),
                ('mutli_varName',MultiUnitHandler(base_handler=VarNameHandler(),options_handlers=[SupportHandler((',', 'symbol')), VarNameHandler()])),
                (';',SupportHandler((';', 'symbol')))
            ]

        return self._check_chain

    @property
    def valid_num(self):
        if not hasattr(self,'_valid_num'):
            self._valid_num = [4]
        return self._valid_num

class VoidParameterListHandler(EmptyHandler):
    isTerminal = False
    label = 'parameterList'

class CommonParameterListHandler(SequenceHandler):
    isTerminal = False
    label = 'parameterList'

    @property
    def check_chain(self):
        if not hasattr(self,'_check_chain'):
            self._check_chain = [
                ('type',TypeHandler()),
                ('varName',VarNameHandler()),
                ('mutli_parameter',MultiUnitHandler(base_handler=None,options_handlers=[SupportHandler((',', 'symbol')),TypeHandler(),VarNameHandler()]))
            ]
        return self._check_chain
    @property
    def valid_num(self):
        if not hasattr(self,'_valid_num'):
            self._valid_num = [2,3]
        return self._valid_num
    
class ParameterListHandler(SelectHandler):
    isTerminal = True
    label = 'parameterList'
    @property
    def candidates(self):
        if not hasattr(self,'_candidates'):
            self._candidates = {
                'void':VoidParameterListHandler(),
                'common':CommonParameterListHandler()
            }
        return self._candidates

class ConstructorOrFunctionOrMethodHandler(SelectHandler):
    isTerminal = False
    label = 'constructor_or_function_or_method'
    @property
    def candidates(self):
        if not hasattr(self,'_candidates'):
            self._candidates = {
                'constructor':SupportHandler(('constructor', 'keyword')),
                'function':SupportHandler(('function', 'keyword')),
                'method':SupportHandler(('method', 'keyword'))
            }
        return self._candidates
    
class VoidOrTypeHandler(SelectHandler):
    isTerminal = False
    label = 'void_or_type'
    @property
    def candidates(self):
        if not hasattr(self,'_candidates'):            
            self._candidates =  {
                'void':SupportHandler(('void', 'keyword')),
                'type':TypeHandler()
            }
        return self._candidates

class SubroutineDecHandler(SequenceHandler):
    isTerminal = True
    label = 'subroutineDec'
    @property
    def check_chain(self):
        if not hasattr(self,'_check_chain'):
            self._check_chain = [
                ('constructor_or_function_or_method',ConstructorOrFunctionOrMethodHandler()),
                ('void_or_type',VoidOrTypeHandler()),
                ('subroutineName',SubroutineNameHandler()),
                ('(',SupportHandler(('(', 'symbol'))),
                ('parameterList',ParameterListHandler()),
                (')',SupportHandler((')', 'symbol'))),
                ('subroutineBody',SubroutineBodyHandler())
            ]
        return self._check_chain
    @property
    def valid_num(self):
        if not hasattr(self,'_valid_num'):
            self._valid_num = [7]
        return self._valid_num

class SimpleSubroutineBodyHandler(SequenceHandler):
    isTerminal = False
    label = 'subroutineBody'
    @property
    def check_chain(self):
        if not hasattr(self,'_check_chain'):
            self._check_chain = [
                ('{',SupportHandler(('{', 'symbol'))),
                ('statements',MultiStatementHandler()),
                ('}',SupportHandler(('}', 'symbol')))
            ]
        return self._check_chain
    @property
    def valid_num(self):
        if not hasattr(self,'_valid_num'):
            self._valid_num = [3]
        return self._valid_num

class CommonSubroutineBodyHandler(SequenceHandler):
    isTerminal = False
    label = 'subroutineBody'
    @property
    def check_chain(self):
        if not hasattr(self,'_check_chain'):
            self._check_chain = [
                ('{',SupportHandler(('{', 'symbol'))),
                ('mutli_varDec',MultiUnitHandler(base_handler=VarDecHandler(),options_handlers=[VarDecHandler()])),
                ('statements',MultiStatementHandler()),
                ('}',SupportHandler(('}', 'symbol')))
            ]
        return self._check_chain
    @property
    def valid_num(self):
        if not hasattr(self,'_valid_num'):
            self._valid_num = [4]
        return self._valid_num

class SubroutineBodyHandler(SelectHandler):
    isTerminal = True
    label = 'subroutineBody'
    
    @property
    def candidates(self):
        if not hasattr(self,'_candidates'):
            self._candidates = {
                'simple':SimpleSubroutineBodyHandler(),
                'common':CommonSubroutineBodyHandler()
            }
        return self._candidates

class ClassHandler(SequenceHandler):
    isTerminal = True
    label = 'class'
    @property
    def check_chain(self):
        if not hasattr(self,'_check_chain'):
            self._check_chain = [
                ('class',SupportHandler(('class', 'keyword'))),
                ('className',ClassNameHandler()),
                ('{',SupportHandler(('{', 'symbol'))),
                ('mutli_classVarDec',MultiUnitHandler(base_handler=None,options_handlers=[ClassVarDecHandler()])),
                ('mutli_subroutineDec',MultiUnitHandler(base_handler=None,options_handlers=[SubroutineDecHandler()])),
                ('}',SupportHandler(('}', 'symbol')))
            ]
        return self._check_chain
    @property
    def valid_num(self):
        if not hasattr(self,'_valid_num'):
            self._valid_num = [6]
        return self._valid_num