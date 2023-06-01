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

class TypeHandler(BaseHandler):
    isTerminal = True
    label = 'type'

    def processXML(self, unstructured_xml):
        self.xml =''
        if TypeHandler.isType(unstructured_xml):
            self.xml = common_convert(unstructured_xml[0][1])(unstructured_xml[0][0])
        else:
            raise ClassException("TypeHandler: unstructured_xml is not a type")
        
    @common_empty_check
    def isType(unstructured_xml):
        if TypeHandler.findType(unstructured_xml) == len(unstructured_xml):
            return True
        return False
    
    # 如果第一个tuple内的label 是 'int'|'char'|'boolean'| VarName.isName
    # 因为只使用了unstructured_xml[0] 所以返回的find_length为1
    # 如果以上条件不满足返回-1
    def findType(unstructured_xml):
        if not unstructured_xml:
            return -1
        if unstructured_xml[0][0] in ['int','char','boolean'] or NameHandler.isName(unstructured_xml[0]):
            return 1
        return -1

comma_support_handler = SupportHandler((',' , 'symbol'))
comma_unit = Unit('comma',comma_support_handler.findTarget,lambda x: comma_support_handler.isTarget(x),lambda x: comma_support_handler.toXML())
varName_unit = Unit('varName',VarNameHandler.findName,VarNameHandler.isName,lambda x: VarNameHandler.isName(x),lambda x: VarNameHandler(x).toXML())
type_unit = Unit('type',TypeHandler.findType,TypeHandler.isType,lambda x: TypeHandler.isType(x),lambda x: TypeHandler(x).toXML())

# verDec 的结构是 type varName (, varName)* ;
class VarDecHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'varDec'
    check_chain = [
        ('var',SupportHandler(('var', 'keyword')).findTarget, lambda x: SupportHandler(('var', 'keyword')).toXML()),
        ('type',TypeHandler.findType, lambda x: TypeHandler(x).toXML()),
        ('mutli_varName',MultiUnitHandler(base_unit=varName_unit,option_units=[comma_unit,varName_unit]))
        (';',SupportHandler((';', 'symbol')).findTarget, lambda x: SupportHandler((';', 'symbol')).toXML())
    ]
    valid_num = [4]

static_support_handler = SupportHandler(('static','keyword'))
static_support_unit = Unit( 'static',static_support_handler.findTarget,lambda x: static_support_handler.isTarget(x),lambda x: static_support_handler.toXML())
field_support_handler = SupportHandler(('field','keyword'))
field_support_unit = Unit( 'field',field_support_handler.findTarget,lambda x: field_support_handler.isTarget(x),lambda x: field_support_handler.toXML())
static_or_field_handler = OrHanlder(static_support_unit,field_support_unit)

# classVarDec 的结构是 (static|field) type varName (, varName)* ;
class ClassVarDecHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'classVarDec'
    check_chain = [
        ('static_or_field',static_or_field_handler.findUnit,lambda x : static_or_field_handler.processXML(x)),
        ('type',TypeHandler.findType, lambda x: TypeHandler(x).toXML()),
        ('mutli_varName',MultiUnitHandler(base_unit=varName_unit,option_units=[comma_unit,varName_unit]))
        (';',SupportHandler((';', 'symbol')).findTarget, lambda x: SupportHandler((';', 'symbol')).toXML())
    ]
    valid_num = [4]

class VoidParameterListHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'parameterList'
    check_chain = [
        ('empty',EmptyHandler.findEmpty,lambda x: EmptyHandler(x).toXML())
    ]
    valid_num = [0]

class ParameterListHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'parameterList'
    check_chain = [
        ('type',TypeHandler.findType, lambda x: TypeHandler(x).toXML()),
        ('varName',VarNameHandler.findName,lambda x: VarNameHandler.isName(x),lambda x: VarNameHandler(x).toXML()),
        ('mutli_parameter',MultiUnitHandler(base_unit=None,option_units=[comma_unit,type_unit,varName_unit]))
    ]
    valid_num = [2,3]

varDec_unit = Unit('varDec',VarDecHandler.findStatement,VarDecHandler.isStatement,lambda x: VarDecHandler(x).toXML())
multi_varDec_handler = MultiUnitHandler(base_unit=None,option_units=[varDec_unit])
empty_or_multi_varDec_handler = OrHanlder(EmptyHandler(),multi_varDec_handler)

class NoneVarDecSubroutineBOdyHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'subroutineBody'
    check_chain = [
        ('{',SupportHandler(('{', 'symbol')).findTarget, lambda x: SupportHandler(('{', 'symbol')).toXML()),
        ('empty_or_multi_varDec',),
        ('statements',StatementHandler.findStatement,lambda x: StatementHandler.isStatement(x),lambda x: StatementHandler(x).toXML()),
        ('}',SupportHandler(('}', 'symbol')).findTarget, lambda x: SupportHandler(('}', 'symbol')).toXML())
    ]
    valid_num = [3]

class SubroutineBodyHandler(TemplateStatmentHandler):
    isTerminal = False
    label = 'subroutineBody'
    check_chain = [
        ('{',SupportHandler(('{', 'symbol')).findTarget, lambda x: SupportHandler(('{', 'symbol')).toXML()),
        ('statements',StatementHandler.findStatement,lambda x: StatementHandler.isStatement(x),lambda x: StatementHandler(x).toXML()),
        ('}',SupportHandler(('}', 'symbol')).findTarget, lambda x: SupportHandler(('}', 'symbol')).toXML())
    ]
    valid_num = [4]

class 