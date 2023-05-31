
from base import *
from utils import *

class ExpressionException(Exception):
    pass







class SubroutineCallHandler(BaseHandler):
    isTerminal = True
    label = 'subroutineCall'
    def processXML(self, unstructured_xml):
        # 1. 处理 subroutineName ( expressionList )
        if VarNameHandler.isVarName(unstructured_xml[0:1]) and unstructured_xml[1][0] == '(' and unstructured_xml[-1][0] == ')':
            self.xml = VarNameHandler(unstructured_xml[0:1]).toXML()
            self.xml += common_convert('symbol')('(') +"\n"
            if not ExpressionListHandler.isExpressionList(unstructured_xml[2:-1]):
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))
            self.xml += ExpressionListHandler(unstructured_xml[2:-1]).toXML()
            self.xml += common_convert('symbol')(')')+ "\n"
        # 2. 处理 className . subroutineName ( expressionList )
        elif VarNameHandler.isVarName(unstructured_xml[0:1]) and unstructured_xml[1][0] == '.' and VarNameHandler.isVarName(unstructured_xml[2:3]) and unstructured_xml[3][0] == '(' and unstructured_xml[-1][0] == ')':
            self.xml = VarNameHandler(unstructured_xml[0:1]).toXML()
            self.xml += common_convert('symbol')('.') +"\n"
            self.xml += VarNameHandler(unstructured_xml[2:3]).toXML()
            self.xml += common_convert('symbol')('(') +"\n"
            if not ExpressionListHandler.isExpressionList(unstructured_xml[4:-1]):
                raise ExpressionException("something wrong with {0}".format(unstructured_xml))
            self.xml += ExpressionListHandler(unstructured_xml[4:-1]).toXML()
            self.xml += common_convert('symbol')(')')+ "\n"

    def isSubroutineCall(unstructured_xml):
        if not unstructured_xml:
            return 0
        # 1. 处理 subroutineName ( expressionList )
        if VarNameHandler.isVarName(unstructured_xml[0:1]) \
            and unstructured_xml[1][0] == '(':
            expressionList_end_index = ExpressionListHandler.isExpressionList(unstructured_xml[2:])
            if expressionList_end_index ==0  or unstructured_xml[expressionList_end_index+2][0] != ')':
                return 0
            return expressionList_end_index+3
        # 2. 处理 className . subroutineName ( expressionList )
        elif VarNameHandler.isVarName(unstructured_xml[0:1]) \
            and unstructured_xml[1][0] == '.' \
            and VarNameHandler.isVarName(unstructured_xml[2:3]) \
            and unstructured_xml[3][0] == '(':
            expressionList_end_index = ExpressionListHandler.isExpressionList(unstructured_xml[4:])
            if expressionList_end_index==0 or unstructured_xml[expressionList_end_index+4][0] != ')':
                return 0
            return expressionList_end_index+5
        return 0
