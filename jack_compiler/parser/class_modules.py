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
    
    def processXML(self, unstructured_xml):
        self.xml = ''
        if StaticOrFieldHandler().isTarget(unstructured_xml[0:1]) > 0:
            self.xml += StaticOrFieldHandler().processXML(unstructured_xml[0:1])
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('static or field is not found')
        if TypeHandler().isTarget(unstructured_xml[0:1]) > 0:
            self.xml += TypeHandler().processXML(unstructured_xml[0:1])
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('type is not found')
        var_name_length = VarNameHandler().findTarget(unstructured_xml)
        if var_name_length > 0:
            self.xml += VarNameHandler().processXML(unstructured_xml[:var_name_length])
            unstructured_xml = unstructured_xml[var_name_length:]
        else:
            raise ClassException('varName is not found')
        while SupportHandler((',', 'symbol')).isTarget(unstructured_xml[0:1]) > 0:
            self.xml += common_convert('symbol')(',')
            unstructured_xml = unstructured_xml[1:]
            var_name_length = VarNameHandler().findTarget(unstructured_xml)
            if var_name_length > 0:
                self.xml += VarNameHandler().processXML(unstructured_xml[:var_name_length])
                unstructured_xml = unstructured_xml[var_name_length:]
            else:
                raise ClassException('varName is not found')
        if SupportHandler((';', 'symbol')).isTarget(unstructured_xml[0:1]) > 0:
            self.xml += common_convert('symbol')(';')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('; is not found')

    def findTarget(self, unstructured_xml):
        try:
            try:
                last_semicolon_index = unstructured_xml.index((';', 'symbol'))
            except ValueError:
                raise ClassException('; is not found')
            self.processXML(unstructured_xml[:last_semicolon_index + 1])
        except ClassException as e:
            return -1
        return last_semicolon_index + 1
    
    def isTarget(self, unstructured_xml):
        try:
            self.processXML(unstructured_xml)
        except ClassException as e:
            print(e)
            return False
        return True


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
    
    def processXML(self, unstructured_xml):
        self.xml = ''
        if not unstructured_xml:
            return 
        if CommonParameterListHandler().isTarget(unstructured_xml[0:1]) > 0:
            self.xml += CommonParameterListHandler().processXML(unstructured_xml[0:1])
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('common parameterList is not found')
        
    def isTarget(self, unstructured_xml):
        try:
            self.processXML(unstructured_xml)
        except ClassException as e:
            print(e)
            return False
        return True
    
    def findTarget(self, unstructured_xml):
        try:
            # \
            try:
                brace_index = unstructured_xml.index(('}', 'symbol'))
            except ValueError:
                raise ClassException('} is not found')
            self.processXML(unstructured_xml[:brace_index-1])
        except ClassException as e:
            print(e)
            return -1
        return brace_index-1        

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

    def processXML(self, unstructured_xml):
        self.xml = ''
        if ConstructorOrFunctionOrMethodHandler().isTarget(unstructured_xml[0:1]) > 0:
            self.xml += ConstructorOrFunctionOrMethodHandler().processXML(unstructured_xml[0:1])
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('constructor or function or method is not found')
        if VoidOrTypeHandler().isTarget(unstructured_xml[0:1]) > 0:
            self.xml += VoidOrTypeHandler().processXML(unstructured_xml[0:1])
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('void or type is not found')
        if SubroutineNameHandler().isTarget(unstructured_xml[0:1]) > 0:
            self.xml += SubroutineNameHandler().processXML(unstructured_xml[0:1])
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('subroutineName is not found')
        if SupportHandler(('(', 'symbol')).isTarget(unstructured_xml[0:1]) > 0:
            self.xml += common_convert('symbol')('(')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('( is not found')
        param_list_length = ParameterListHandler().findTarget(unstructured_xml)
        if param_list_length >= 0:
            self.xml += ParameterListHandler().processXML(unstructured_xml[:param_list_length])
            unstructured_xml = unstructured_xml[param_list_length:]
        else:
            raise ClassException('parameterList is not found')
        if SupportHandler((')', 'symbol')).isTarget(unstructured_xml[0:1]) > 0:
            self.xml += common_convert('symbol')(')')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException(') is not found')
        subroutine_body_length = SubroutineBodyHandler().findTarget(unstructured_xml)
        if subroutine_body_length >= 0:
            self.xml += SubroutineBodyHandler().processXML(unstructured_xml[:subroutine_body_length])
            unstructured_xml = unstructured_xml[subroutine_body_length:]
        else:
            raise ClassException('subroutineBody is not found')

    def isTarget(self, unstructured_xml):
        try:
            self.processXML(unstructured_xml)
        except ClassException as e:
            print(e)
            return False
        return True

    def findTarget(self, unstructured_xml):
        try:
            next_subroutineDec_index = len(unstructured_xml)
            for word in unstructured_xml:
                if word[0] in ['constructor', 'function', 'method']:
                    next_subroutineDec_index = unstructured_xml.index(word)
                    break
            self.processXML(unstructured_xml[0:next_subroutineDec_index])
        except ClassException as e:
            print(e)
            return -1
        return next_subroutineDec_index
    
class SubroutineBodyHandler(SequenceHandler):
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

    def processXML(self, unstructured_xml):
        self.xml = ''
        if SupportHandler(('{', 'symbol')).isTarget(unstructured_xml[0:1]) > 0:
            self.xml += common_convert('symbol')('{')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('{ is not found')
        find_varDec_length = VarDecHandler().findTarget(unstructured_xml)
        while find_varDec_length > 0:
            self.xml += VarDecHandler().processXML(unstructured_xml[:find_varDec_length])
            unstructured_xml = unstructured_xml[find_varDec_length:]
            find_varDec_length = VarDecHandler().findTarget(unstructured_xml)
        find_statment_length = StatementHandler().findTarget(unstructured_xml)
        while find_statment_length > 0:
            self.xml += StatementHandler().processXML(unstructured_xml[:find_statment_length])
            unstructured_xml = unstructured_xml[find_statment_length:]
            find_statment_length = StatementHandler().findTarget(unstructured_xml)

        if SupportHandler(('}', 'symbol')).isTarget(unstructured_xml[0:1]) > 0:
            self.xml += common_convert('symbol')('}')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('} is not found')

    def isTarget(self, unstructured_xml):
        try:
            self.processXML(unstructured_xml)
        except ClassException as e:
            print(e)
            return False
        return True
    
    def findTarget(self, unstructured_xml):
        try:
            next_subroutineDec_index = len(unstructured_xml)
            for word in unstructured_xml:
                if word[0] in ['constructor', 'function', 'method']:
                    next_subroutineDec_index = unstructured_xml.index(word)
                    break
            self.processXML(unstructured_xml[0:next_subroutineDec_index])
        except ClassException as e:
            print(e)
            return -1
        return next_subroutineDec_index
    

class ClassHandler(SequenceHandler):
    isTerminal = True
    label = 'class'

    def processXML(self,unstructured_xml):
        self.xml = ''
        # 1. 分割并转换XML class keyword
        if SupportHandler(('class', 'keyword')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('keyword')('class')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('class keyword is not found')
        # 2. 分割并转换XML className
        if ClassNameHandler().isTarget(unstructured_xml[:1]):
            self.xml += ClassNameHandler().processXML(unstructured_xml[:1])
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('className is not found')
        # 3. 分割并转换XML {
        if SupportHandler(('{', 'symbol')).isTarget(unstructured_xml[:1]):
            self.xml += common_convert('symbol')('{')
            unstructured_xml = unstructured_xml[1:]
        else:
            raise ClassException('{ is not found')
        # 4. 分割并转换XML mutli_classVarDec
        while ClassVarDecHandler().findTarget(unstructured_xml)>0:
            find_length = ClassVarDecHandler().findTarget(unstructured_xml)
            self.xml += ClassVarDecHandler().processXML(unstructured_xml[:find_length])
            unstructured_xml = unstructured_xml[find_length:]
        # 5. 分割并转换XML mutli_subroutineDec
        while SubroutineDecHandler().findTarget(unstructured_xml)>0:
            find_length = SubroutineDecHandler().findTarget(unstructured_xml)
            self.xml += SubroutineDecHandler().processXML(unstructured_xml[:find_length])
            unstructured_xml = unstructured_xml[find_length:]
        # 6. 分割并转换XML }
        if SupportHandler(('}', 'symbol')).isTarget(unstructured_xml[-1:]):
            self.xml += common_convert('symbol')('}')
            unstructured_xml = unstructured_xml[:-1]
        else:
            raise ClassException('} is not found')
        
    def isTarget(self, unstructured_xml):
        try:
            self.processXML(unstructured_xml)
        except ClassException as e:
            print(e)
            return False
        return True

    def findTarget(self, unstructured_xml):
        # 用class 关键字来判断是否为class
        try:
            next_class_index = len(unstructured_xml)
            try:
                next_class_index = unstructured_xml.index(('class', 'keyword'))
            except ValueError:
                pass
            self.processXML(unstructured_xml[0:next_class_index])
        except ClassException as e:
            print(e)
            return -1
        return next_class_index
