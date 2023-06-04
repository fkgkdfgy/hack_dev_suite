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

class MultiVarNameHandler(MultiUnitHandler):
    isTerminal = False
    label = 'multi_varName'
    empty_allowed = False

    @property
    def base_handler(self):
        if not hasattr(self,'_base_handler'):
            self._base_handler = VarNameHandler()
        return self._base_handler
    
    @property
    def options_handlers(self):
        if not hasattr(self,'_options_handlers'):
            self._options_handlers = [SupportHandler((',', 'symbol')),VarNameHandler()]
        return self._options_handlers


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
                ('mutli_varName',MultiVarNameHandler()),
                (';',SupportHandler((';', 'symbol')))
            ]
        return self._check_chain

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
                ('mutli_varName',MultiVarNameHandler()),
                (';',SupportHandler((';', 'symbol')))
            ]
        return self._check_chain

class ParameterListHandler(MultiStatementHandler):
    isTerminal = True
    label = 'parameterList'
    empty_allowed = True
    @property
    def base_handler(self):
        if not hasattr(self,'_base_handler'):
            self._base_handler = [TypeHandler(),VarNameHandler()]
        return self._base_handler
    
    @property
    def options_handlers(self):
        if not hasattr(self,'_options_handlers'):
            self._options_handlers = [SupportHandler((',', 'symbol')),TypeHandler(),VarNameHandler()]
        return self._options_handlers
    
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

class MultiVarDecHandler(MultiUnitHandler):
    isTerminal = False
    label = 'multi_varDec'
    empty_allowed = True
    @property
    def base_handler(self):
        if not hasattr(self,'_base_handler'):
            self._base_handler = VarDecHandler()
        return self._base_handler
    
    @property
    def options_handlers(self):
        if not hasattr(self,'_options_handlers'):
            self._options_handlers = [VarDecHandler()]
        return self._options_handlers

class SubroutineBodyHandler(SequenceHandler):
    isTerminal = True
    label = 'subroutineBody'
    @property
    def check_chain(self):
        if not hasattr(self,'_check_chain'):
            self._check_chain = [
                ('{',SupportHandler(('{', 'symbol'))),
                ('mutli_varDec',MultiVarDecHandler()),
                ('statements',MultiStatementHandler()),
                ('}',SupportHandler(('}', 'symbol')))
            ]
        return self._check_chain

class MultiClassVarDecHandler(MultiUnitHandler):
    isTerminal = False
    label = 'multi_classVarDec'
    empty_allowed = True
    @property
    def base_handler(self):
        if not hasattr(self,'_base_handler'):
            self._base_handler = ClassVarDecHandler()
        return self._base_handler
    
    @property
    def options_handlers(self):
        if not hasattr(self,'_options_handlers'):
            self._options_handlers = [ClassVarDecHandler()]
        return self._options_handlers

class MultiSubroutineDecHandler(MultiUnitHandler):
    isTerminal = False
    label = 'multi_subroutineDec'
    empty_allowed = True
    @property
    def base_handler(self):
        if not hasattr(self,'_base_handler'):
            self._base_handler = SubroutineDecHandler()
        return self._base_handler
    
    @property
    def options_handlers(self):
        if not hasattr(self,'_options_handlers'):
            self._options_handlers = [SubroutineDecHandler()]
        return self._options_handlers

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
                ('mutli_classVarDec',MultiClassVarDecHandler()),
                ('mutli_subroutineDec',MultiSubroutineDecHandler()),
                ('}',SupportHandler(('}', 'symbol')))
            ]
        return self._check_chain
