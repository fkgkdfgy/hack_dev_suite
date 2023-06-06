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
    
    def registrateSymbolTable(self):
        pass

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
    
    def registrateSymbolTable(self):
        var_dec_type = self.children[1].getWord()
        index = 0
        for var_name in self.children[2].children:
            var_name = var_name.getWord()                
            self.symbol_table[var_name] = ('local',var_dec_type,index)
            index += 1

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
    
    def getAttr(self):
        return self.selected_candidate.getWord()


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

    def registrateSymbolTable(self):
        var_dec_attr = self.children[0].getAttr()
        var_dec_type = self.children[1].getWord()
        index = 0
        for var_name in self.children[2].children:
            var_name = var_name.getWord()                
            self.symbol_table[var_name] = (var_dec_attr,var_dec_type,index)
            index += 1

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
    
    def registrateSymbolTable(self):
        for child in self.children:
            child.registrateSymbolTable()
        
        child_symbol_table = {}
        for child in self.chuildren:
            child_symbol_table[child] = child.symbol_table
        
        # symbol_table ::= 'varname':(attr,type,index) 三个属性
        # 这里需要把相同attr 的 variable 对应的index 进行累加来形成新的symbol table
        for child in self.children:
            for var_name in child.symbol_table:
                if var_name in self.symbol_table:
                    raise ClassException('var_name: {} has been defined'.format(var_name))
                self.symbol_table[var_name] = child.symbol_table[var_name]
        
        # 更新 argument 的index
        argument_index = 0
        for var_name in self.symbol_table:
            if self.symbol_table[var_name][0] == 'argument':
                self.symbol_table[var_name][2] = argument_index
                argument_index += 1

    def getParameterNum(self):
        count = 0
        for child in self.children:
            if isinstance(child,VarNameHandler):
                count += 1
        return count

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

    def getSubroutineAttr(self):
        return self.selected_candidate.getWord()

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

    def toConstructor(self, class_name, object_inner_size):
        return_code = ''
        subroutine_name = self.children[2].getWord()
        local_var_num = self.children[6].getLocalVarNum()
        return_code += 'function {}.{} {}\n'.format(class_name,subroutine_name,local_var_num)
        return_code += 'push constant {}\n'.format(object_inner_size)
        return_code += 'call Memory.alloc 1\n'
        return_code += 'pop pointer 0\n'
        return_code += self.children[7].toCode(class_name)
        return return_code

    def toFunction(self, class_name):
        return_code = ''
        subroutine_name = self.children[2].getWord()
        local_var_num = self.children[6].getLocalVarNum()
        return_code += 'function {}.{} {}\n'.format(class_name,subroutine_name,local_var_num)
        return_code += self.children[7].toCode(class_name)
        return return_code

    def toMethod(self, class_name):
        return_code = ''
        subroutine_name = self.children[2].getWord()
        local_var_num = self.children[6].getLocalVarNum()
        return_code += 'function {}.{} {}\n'.format(class_name,subroutine_name,local_var_num)
        return_code += 'push argument 0\n'
        return_code += 'pop pointer 0\n'
        return_code += self.children[7].toCode(class_name)
        return return_code

    def registrateSymbolTable(self):
        parameter_list = self.children[4]
        parameter_list.registrateSymbolTable()
        self.symbol_table = parameter_list.symbol_table
        # 将type 更改为 argument
        for var_name in self.symbol_table:
            self.symbol_table[var_name] = ('argument',self.symbol_table[var_name][1],self.symbol_table[var_name][2])

    def toCode(self, class_name):
        self.registrateSymbolTable()
        result_code = ''
        subroutine_type = self.children[0].getSubroutineAttr()
        if subroutine_type == 'constructor':
            result_code = self.toConstructor(class_name)
        elif subroutine_type == 'function':
            result_code = self.toFunction(class_name)
        elif subroutine_type == 'method':
            result_code = self.toMethod(class_name)
        else:
            raise ClassException('subroutine_type: {} is not supported'.format(subroutine_type))
        return result_code


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
    
    def registrateSymbolTable(self):
        for child in self.children:
            child.registrateSymbolTable()
        
        # symbol_table ::= 'varname':(attr,type,index) 三个属性
        # 这里需要把相同attr 的 variable 对应的index 进行累加来形成新的symbol table
        for child in self.children:
            for var_name in child.symbol_table:
                if var_name in self.symbol_table:
                    raise ClassException('var_name: {} has been defined'.format(var_name))
                self.symbol_table[var_name] = child.symbol_table[var_name]
        # 更新local 的index
        local_index = 0
        for var_name in self.symbol_table:
            if self.symbol_table[var_name][0] == 'local':
                self.symbol_table[var_name][2] = local_index
                local_index += 1

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

    def getLocalVarNum(self):
        return len(self.symbol_table)    

    def registrateSymbolTable(self):
        multi_var_dec = self.children[1]
        multi_var_dec.registrateSymbolTable()
        self.symbol_table = multi_var_dec.symbol_table

    def toCode(self, *args, **kwargs):
        self.registrateSymbolTable()
        return_code = ''
        for child in self.children[2].children:
            return_code += child.toCode(*args, **kwargs)
        return return_code

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
    
    def registrateSymbolTable(self):
        for child in self.children:
            child.registrateSymbolTable()
        
        # symbol_table ::= 'varname':(attr,type,index) 三个属性
        # 这里需要把相同attr 的 variable 对应的index 进行累加来形成新的symbol table
        for child in self.children:
            for var_name in child.symbol_table:
                if var_name in self.symbol_table:
                    raise ClassException('var_name: {} has been defined'.format(var_name))
                self.symbol_table[var_name] = child.symbol_table[var_name]
        # 更新static 的index
        static_index = 0
        for var_name in self.symbol_table:
            if self.symbol_table[var_name][0] == 'static':
                self.symbol_table[var_name][2] = static_index
                static_index += 1
        # 更新field 的index
        field_index = 0
        for var_name in self.symbol_table:
            if self.symbol_table[var_name][0] == 'field':
                self.symbol_table[var_name][2] = field_index
                field_index += 1

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
    
    def toCode(self, class_name):
        result_code = ''
        for child in self.children:
            result_code += child.toCode(class_name)
        return result_code

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

    def toCode(self):
        self.registrateSymbolTable()
        class_code = ''
        for child in self.children:
            class_code += child.toCode(self.getClassName())
        return class_code

    def registrateSymbolTable(self):
        class_var_dec = self.children[3]
        class_var_dec.registrateSymbolTable()
        self.symbol_table = class_var_dec.symbol_table
    
    def getClassName(self):
        return self.children[1].getWord()
        