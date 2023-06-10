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
        self.symbol_table = {}
        var_dec_type = self.children[1].getWord()
        index = 0
        for child in self.children[2].children:
            if isinstance(child,VarNameHandler):
                var_name = child.getWord()                
                self.symbol_table[var_name] = ['local',var_dec_type,index]
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
        self.symbol_table = {}
        var_dec_attr = self.children[0].getAttr()
        var_dec_type = self.children[1].getWord()
        index = 0
        for child in self.children[2].children:
            if isinstance(child,VarNameHandler):
                var_name = child.getWord()                
                self.symbol_table[var_name] = [var_dec_attr,var_dec_type,index]
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
        var_types = [child for child in self.children if isinstance(child,TypeHandler)]
        var_names = [child for child in self.children if isinstance(child,VarNameHandler)]
        if len(var_types) != len(var_names):
            raise ClassException('var_types: {0} and var_names: {1} are not equal'.format(var_types,var_names))
        self.symbol_table = {}
        index = 0
        for index in range(len(var_types)):
            var_type = var_types[index].getWord()
            var_name = var_names[index].getWord()
            self.symbol_table[var_name] = ['argument',var_type,index] 
            index += 1

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

    def toConstructor(self,class_name, object_member_variable_size):
        return_code = ''
        subroutine_name = self.children[2].getWord()
        local_var_num = self.children[6].getLocalVarNum()
        return_code += 'function {}.{} {}\n'.format(class_name,subroutine_name,local_var_num)
        return_code += 'push constant {}\n'.format(object_member_variable_size)
        return_code += 'call Memory.alloc 1\n'
        return_code += 'pop pointer 0\n'
        return_code += self.children[6].toCode()
        return return_code

    def toFunction(self,class_name):
        return_code = ''
        subroutine_name = self.children[2].getWord()
        local_var_num = self.children[6].getLocalVarNum()
        return_code += 'function {}.{} {}\n'.format(class_name,subroutine_name,local_var_num)
        return_code += self.children[6].toCode()
        return return_code

    def toMethod(self,class_name):
        return_code = ''
        subroutine_name = self.children[2].getWord()
        local_var_num = self.children[6].getLocalVarNum()
        return_code += 'function {}.{} {}\n'.format(class_name,subroutine_name,local_var_num)
        return_code += 'push argument 0\n'
        return_code += 'pop pointer 0\n'
        return_code += self.children[6].toCode()
        return return_code

    def registrateSymbolTable(self):
        self.symbol_table = {}
        BaseHandler.registrateSymbolTable(self)        
        parameter_list = self.children[4]
        self.symbol_table = parameter_list.symbol_table
        # 将type 更改为 argument
        for var_name in self.symbol_table:
            self.symbol_table[var_name] = ['argument',self.symbol_table[var_name][1],self.symbol_table[var_name][2]]

    def toCode(self):
        self.registrateSymbolTable()
        parent_class = self.getParentClass()
        if not parent_class:
            raise ClassException('parent_class is not defined')
        class_name = parent_class.getClassName()
        result_code = ''
        subroutine_type = self.getAttr()
        if subroutine_type == 'constructor':
            member_variable_size = len(parent_class.getMemberVariableList())
            result_code = self.toConstructor(class_name,member_variable_size)
        elif subroutine_type == 'function':
            result_code = self.toFunction(class_name)
        elif subroutine_type == 'method':
            result_code = self.toMethod(class_name)
        else:
            raise ClassException('subroutine_type: {} is not supported'.format(subroutine_type))
        return result_code

    def getParentClass(self):
        handler_might_be_class = self.parent_handler
        while handler_might_be_class and not isinstance(handler_might_be_class,ClassHandler):
            handler_might_be_class = handler_might_be_class.parent_handler
        if not handler_might_be_class:
            raise ClassException('parent_class is not define, so the search stoped with not handler_might_be_class')
        return handler_might_be_class

    def getAttr(self):
        attr_handler = self.children[0]
        return attr_handler.selected_candidate.getWord()
    
    def getName(self):
        return self.children[2].getWord()

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
        self.symbol_table = {}
        
        for child in self.children:
            child.registrateSymbolTable()
        
        # symbol_table ::= 'varname':(attr,type,index) 三个属性
        # 这里需要把相同attr 的 variable 对应的index 进行累加来形成新的symbol table
        for child in self.children:
            for var_name in child.symbol_table:
                if var_name in self.symbol_table:
                    raise ClassException('var_name: {} has been defined'.format(var_name))
                self.symbol_table[var_name] = copy.deepcopy(child.symbol_table[var_name])
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
        self.symbol_table = {}
        multi_var_dec = self.children[1]
        multi_var_dec.registrateSymbolTable()
        self.symbol_table = copy.deepcopy(multi_var_dec.symbol_table)

    def toCode(self):
        self.registrateSymbolTable()
        result_code = ''
        result_code =  self.children[2].toCode()
        return result_code

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
        self.symbol_table={}
        for child in self.children:
            child.registrateSymbolTable()
        
        # symbol_table ::= 'varname':(attr,type,index) 三个属性
        # 这里需要把相同attr 的 variable 对应的index 进行累加来形成新的symbol table
        for child in self.children:
            for var_name in child.symbol_table:
                if var_name in self.symbol_table:
                    raise ClassException('var_name: {} has been defined'.format(var_name))
                self.symbol_table[var_name] = copy.deepcopy(child.symbol_table[var_name])
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
    
    def toCode(self):
        result_code = ''
        for child in self.children:
            result_code += child.toCode()
        return result_code

class ClassHandler(SequenceHandler):
    isTerminal = True
    label = 'class'

    def __init__(self, unstructed_xml=None):
        self.function_list = {}
        SequenceHandler.__init__(self,unstructed_xml)

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
            tmp_code = child.toCode()
            print(tmp_code)
            class_code += tmp_code
        return class_code

    def registrateSymbolTable(self):
        self.symbol_table = {}
        class_var_dec = self.children[3]
        class_var_dec.registrateSymbolTable()
        self.symbol_table = copy.deepcopy(class_var_dec.symbol_table)
        for name , info_tuple in self.symbol_table.items():
            if info_tuple[0] == 'field':
                self.symbol_table[name][0] = 'this'
        self.symbol_table['this'] = ['self',self.getClassName(),-1]
    
    def getClassName(self):
        return self.children[1].getWord()
    
    def getMemberVariableList(self):
        member_variable = []
        for name , info_tuple in self.symbol_table.items():
            if info_tuple[0] == 'this':
                member_variable.append([name,info_tuple])
        return member_variable

    def getStaticVariableList(self):
        static_variable = []
        for name , info_tuple in self.symbol_table.items():
            if info_tuple[0] == 'static':
                static_variable.append([name,info_tuple])
        return static_variable

    def getMemberFunctionList(self):
        member_function = []
        multi_subroutine_dec = self.children[4]
        for subroutine_dec in multi_subroutine_dec.children:
            if subroutine_dec.children[0].getSubroutineAttr() == 'method':
                member_function.append(subroutine_dec.getName())
        return member_function

    def getStaticFunctionList(self):
        static_function = []
        multi_subroutine_dec = self.children[4]
        for subroutine_dec in multi_subroutine_dec.children:
            if subroutine_dec.children[0].getSubroutineAttr() == 'function':
                static_function.append(subroutine_dec.getName())
        return static_function

    def getConstructor(self):
        multi_subroutine_dec = self.children[4]
        for subroutine_dec in multi_subroutine_dec.children:
            if subroutine_dec.children[0].getSubroutineAttr() == 'constructor':
                return subroutine_dec.getName()
        return []