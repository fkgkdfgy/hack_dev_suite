from utils import *

class GrammarException(Exception):
    pass


class ExpressionListHandler:
    def __init__(self) -> None:
        self.xml = ''
    def processXML(self,unstructured_xml):
        self.xml = '<expressionList>\n'
        # 1. 从XML中提取出expression
        expression_handlers=[]
        expression_indice = [index for index ,element in enumerate(unstructured_xml) if element[0] in ['+','-','*','/','&','|','<','>','=']]
        for start_index,end_index in zip(expression_indice,expression_indice[1:]+[len(unstructured_xml)]):
            expression_handler = ExpressionHandler()
            expression_handler.processXML(unstructured_xml[start_index:end_index])
            expression_handlers.append(expression_handler)
        # 2. 将expression的结果转换为XML
        for expression_handler in expression_handlers:
            self.xml += expression_handler.toXML()
        # 3. 在末尾添加</expressionList>
        self.xml += "</expressionList>\n"
        pass
    def toXML(self):
        return self.xml

class SubroutineCallHandler:
    def __init__(self) -> None:
        self.xml = ''
    def processXML(self,unstructured_xml):
        self.xml = '<subroutineCall>\n'
        # 1. 从XML中提取出subroutineName
        subroutine_name = unstructured_xml[0][0]
        name_type = unstructured_xml[0][1]
        self.xml += common_convert(name_type)(subroutine_name) + "\n"
        # 2. 从XML中提取出'('和')',没有其中一个就报错，然后依靠'('和')'来提取expressionList
        start_index = [index for index ,element in enumerate(unstructured_xml) if element[0] == '(']
        end_index = [index for index ,element in enumerate(unstructured_xml) if element[0] == ')']
        if not start_index and 0 not in start_index:
            raise GrammarException("subroutineCall must have '('")
        if not end_index:
            raise GrammarException("subroutineCall must have ')'")
        if not unstructured_xml[1][0] == '(':
            raise GrammarException("subroutineCall must have '('")
        self.xml += common_convert('symbol')('(') + "\n"
        #3. 从XML中提取出expressionList, 这里有些问题, 因为expressionList中可能没有参数
        end_index = end_index[0]
        expression_list_handler = ExpressionListHandler()
        expression_list_handler.processXML(unstructured_xml[2:end_index])
        self.xml += expression_list_handler.toXML()
        #4. 从XML中提取出')'
        self.xml += common_convert('symbol')(')') + "\n"
        #5. 在末尾添加</subroutineCall>
        self.xml += "</subroutineCall>\n"
    
    def toXML(self):
        return self.xml
    
    # TODO 应该最终变成保存term 、expression、 计算符号的 正则表达式
    def issubroutineCall(unstructured_xml):
        # 1. unstructured_xml 必须大于 2
        if len(unstructured_xml) < 2:
            return False
        # 2. unstructured_xml[0] 必须是identifier
        if not unstructured_xml[0][1] == 'identifier':
            return False
        # 3. unstructured_xml[1] 必须是'(' 或者 '.'
        if not unstructured_xml[1][0] in ['(','.']:
            return False
        # 4. '(' 必须在第二个或者第四个位置
        if not (unstructured_xml[1][0] == '(' and len(unstructured_xml) >= 4) or (unstructured_xml[3][0] == '(' and len(unstructured_xml) >= 6):
            return False
        # 5. 如果'.'存在必须在第二个位置
        if unstructured_xml[1][0] == '.' and len(unstructured_xml) < 6:
            return False
        # 6. ')' 必须在最后一个位置 
        if not unstructured_xml[-1][0] == ')':
            return False
        return True
class TermHandler:
    def __init__(self) -> None:
        self.xml = ''

    def processXML(self,unstructured_xml):
        self.xml = '<term>\n'
        # 1. 如果unstructured_xml的长度为1, 那么就是inteConst|stringConstant|keyword|varName, 直接转换为XML
        if len(unstructured_xml) == 1 and unstructured_xml[0][1] in ['intConst','stringConst','keyword','identifier']:
            name_type = unstructured_xml[0][1]
            self.xml += common_convert(name_type)(unstructured_xml[0][0]) + "\n"
        # 2. 如果unstructured_xml的第一个字符是一元运算符, 那么就是 unaryOp term, 直接转换为XML
        elif unstructured_xml[0][0] in ['~','-']:
            name_type = unstructured_xml[0][1]
            self.xml += common_convert(name_type)(unstructured_xml[0][0]) + "\n"
            term_handler = TermHandler()
            term_handler.processXML(unstructured_xml[1:])
            self.xml += term_handler.toXML()
        # 3. 如果开头和结尾字符分别为'(' 和')', 那么就是一个'('expression')', 直接转换为XML
        elif unstructured_xml[0][0] == '(' and unstructured_xml[-1][0] == ')':
            self.xml += common_convert('symbol')('(') + "\n"
            expression_handler = ExpressionHandler()
            expression_handler.processXML(unstructured_xml[1:-1])
            self.xml += expression_handler.toXML()
            self.xml += common_convert('symbol')(')') + "\n"
        # 4. 如果第一个字符是identifier 且第二个字符和最后一个字符分别'['和']', 那么就是一个varName '[' expression ']', 直接转换为XML
        elif unstructured_xml[0][1] == 'identifier' and unstructured_xml[1][0] == '[' and unstructured_xml[-1][0] == ']':
            name_type = unstructured_xml[0][1]
            self.xml += common_convert(name_type)(unstructured_xml[0][0]) + "\n"
            self.xml += common_convert('symbol')('[') + "\n"
            expression_handler = ExpressionHandler()
            expression_handler.processXML(unstructured_xml[2:-1])
            self.xml += expression_handler.toXML()
            self.xml += common_convert('symbol')(']') + "\n"
        # 5. 那么就是一个subroutineCall, 直接转换为XML
        elif SubroutineCallHandler.issubroutineCall(unstructured_xml):
            subroutine_call_handler = SubroutineCallHandler()
            subroutine_call_handler.processXML(unstructured_xml)
            self.xml += subroutine_call_handler.toXML()
        # 7. 末尾添加</term>
        self.xml += "</term>\n"
        
    def toXML(self):
        return self.xml

class ExpressionHandler:
    def __init__(self) -> None:
        self.xml = ''
    def processXML(self,unstructured_xml):
        self.xml = '<expression>\n'
        # 1. 从XML中提取出op (如果有的话), 并记录下index
        op_indice = [index for index ,element in enumerate(unstructured_xml) if element[0] in ['+','-','*','/','&','|','<','>','=']]
        # 2. 从XML中提取出term
        term_handlers=[]
        term_start_indice = [0]+[ index +1 for index in op_indice]
        term_end_indice = op_indice+[len(unstructured_xml)] 
        for start_index,end_index in zip(term_start_indice,term_end_indice):
            term_handler = TermHandler()
            term_handler.processXML(unstructured_xml[start_index:end_index])
            term_handlers.append(term_handler)
        # 3. 将term的结果转换为XML
        # 3.1. 第一个term 一定存在所以转换先转换第一个term
        self.xml += term_handlers[0].toXML()
        # 3.2. 如果有op, 那么就转换op和term
        for index in range(1,len(term_handlers)):
            op = unstructured_xml[op_indice[index-1]][0]
            name_type = unstructured_xml[op_indice[index-1]][1]
            self.xml += common_convert(name_type)(op) + "\n"
            self.xml += term_handlers[index].toXML()

        # 4. 在末尾添加</expression>
        self.xml += "</expression>\n"
        pass

    def toXML(self):
        return self.xml

class ReturnHandler:
    def __init__(self) -> None:
        self.xml = ''
    def processXML(self,unstructured_xml):
        self.xml = '<returnStatement>\n'
        # 1. 从XML中提取出return
        if not unstructured_xml[0][0] == 'return':
            raise GrammarException("returnStatement must have 'return'")
        self.xml += common_convert('keyword')('return') + "\n"
        # 2. 从XML中提取出expression
        expression_handler = ExpressionHandler()
        expression_handler.processXML(unstructured_xml[1:])
        self.xml += expression_handler.toXML()
        # 3. 从XML中提取出';'
        if not unstructured_xml[-1][0] == ';':
            raise GrammarException("returnStatement must have ';' at the end")
        self.xml += common_convert('symbol')(';') + "\n"
        # 4. 在末尾添加</returnStatement>
        self.xml += "</returnStatement>\n"
        pass
    def toXML(self):
        return self.xml

class StatementHanlder:
    def __init__(self) -> None:
        self.xml = ''
    def processXML(self,unstructured_xml):
        self.xml = '<statement>\n'
        # 1. 从XML中提取出let|if|while|do|return
        statement_type = unstructured_xml[0][0]
        name_type = unstructured_xml[0][1]
        self.xml += common_convert(name_type)(statement_type) + "\n"
        # 2. 提取符合['let','if','while','do','return']的index
        statement_indice = [index for index ,element in enumerate(unstructured_xml) if element[0] in ['let','if','while','do','return']]
        for index in statement_indice:
            if unstructured_xml[index][0] == 'let':
                let_handler = LetHandler()
                let_handler.processXML(unstructured_xml[index:])
                self.xml += let_handler.toXML()
            elif unstructured_xml[index][0] == 'if':
                if_handler = IfHandler()
                if_handler.processXML(unstructured_xml[index:])
                self.xml += if_handler.toXML()
            elif unstructured_xml[index][0] == 'while':
                while_handler = WhileHandler()
                while_handler.processXML(unstructured_xml[index:])
                self.xml += while_handler.toXML()
            elif unstructured_xml[index][0] == 'do':
                do_handler = DoHandler()
                do_handler.processXML(unstructured_xml[index:])
                self.xml += do_handler.toXML()
            elif unstructured_xml[index][0] == 'return':
                return_handler = ReturnHandler()
                return_handler.processXML(unstructured_xml[index:])
                self.xml += return_handler.toXML()        
        # 7. 在末尾添加</statement>
        self.xml += "</statement>\n"
        pass
    def toXML(self):
        return self.xml

class StatementsHandler:
    def __init__(self) -> None:
        self.xml = ''
    def processXML(self,unstructured_xml):
        self.xml = '<statements>\n'
        # 1. 从XML中提取出statement
        statement_handlers=[]
        statement_indice = [index for index ,element in enumerate(unstructured_xml) if element[0] in ['let','if','while','do','return']]
        for start_index,end_index in zip(statement_indice,statement_indice[1:]+[len(unstructured_xml)]):
            statement_handler = StatementHandler()
            statement_handler.processXML(unstructured_xml[start_index:end_index])
            statement_handlers.append(statement_handler)
        # 2. 将statement的结果转换为XML
        for statement_handler in statement_handlers:
            self.xml += statement_handler.toXML()
        # 3. 在末尾添加</statements>
        self.xml += "</statements>\n"
        pass
    
    def toXML(self):
        return self.xml

class VarDecHandler:
    def __init__(self) -> None:
        self.xml = ''
    def processXML(self,unstructured_xml):
        self.xml = '<varDec>\n'
        # 1. 从XML中提取出var
        if not unstructured_xml[0][0] == 'var':
            raise GrammarException("varDec must have 'var'")
        self.xml += common_convert('keyword')('var') + "\n"
        # 2. 从XML中提取出type
        var_type = unstructured_xml[1][0]
        name_type = unstructured_xml[1][1]
        self.xml += common_convert(name_type)(var_type) + "\n"
        # 3. 从XML中提取出varName
        var_name = unstructured_xml[2][0]
        name_type = unstructured_xml[2][1]
        self.xml += common_convert(name_type)(var_name) + "\n"
        # 4. 从XML中提取出','varName (如果有的话)
        for index in range(3,len(unstructured_xml)):
            if unstructured_xml[index][0] == ',':
                var_name = unstructured_xml[index+1][0]
                name_type = unstructured_xml[index+1][1]
                self.xml += common_convert(name_type)(var_name) + "\n"
        #5. 在末尾添加</varDec>
        self.xml += "</varDec>\n"
    
    def toXML(self):
        return self.xml

class ClassVarDecHandler:
    def __init__(self) -> None:
        self.xml = ''
    
    def processXML(self,unstructured_xml):
        self.xml = '<classVarDec>\n'
        # 1. 从XML中提取出static|field
        static_or_field = unstructured_xml[0][0]
        name_type = unstructured_xml[0][1]
        self.xml += common_convert(name_type)(static_or_field) + "\n"
        # 2. 从XML中提取出type
        var_type = unstructured_xml[2][0]
        name_type = unstructured_xml[2][1]        
        self.xml += common_convert(name_type)(var_type) + "\n"
        # 3. 从XML中提取出varName
        var_name = unstructured_xml[3][0]
        name_type = unstructured_xml[3][1]
        self.xml += common_convert(name_type)(var_name) + "\n"
        # 4. 从XML中提取出','varName (如果有的话)
        for index in range(4,len(unstructured_xml)):
            if unstructured_xml[index][0] == ',':
                var_name = unstructured_xml[index+1][0]
                name_type = unstructured_xml[index+1][1]
                self.xml += common_convert(name_type)(var_name) + "\n"
        #5. 在末尾添加</classVarDec>
        self.xml += "</classVarDec>\n"
    def toXML(self):
        return self.xml
    
class ParameterListHandler:
    def __init__(self) -> None:
        self.xml = ''
    
    def processXML(self,unstructured_xml):
        self.xml = '<parameterList>\n'
        # 0. 如果没有参数，直接返回</parameterList>
        if not unstructured_xml:
            self.xml += "</parameterList>\n"
            return
        # 1. 从XML中提取出type
        param_type = unstructured_xml[0][0]
        name_type = unstructured_xml[0][1]
        self.xml += common_convert(name_type)(param_type) + "\n"
        # 2. 从XML中提取出varName
        param_name = unstructured_xml[1][0]
        name_type = unstructured_xml[1][1]
        self.xml += common_convert(name_type)(param_name) + "\n"
        # 3. 从XML中提取出','type varName (如果有的话)
        for index in range(2,len(unstructured_xml)):
            if unstructured_xml[index][0] == ',':
                param_type = unstructured_xml[index+1][0]
                name_type = unstructured_xml[index+1][1]
                self.xml += common_convert(name_type)(param_type) + "\n"
                param_name = unstructured_xml[index+2][0]
                name_type = unstructured_xml[index+2][1]
                self.xml += common_convert(name_type)(param_name) + "\n"

        #4. 在末尾添加</parameterList>
        self.xml += "</parameterList>\n"
        return
        
    def toXML(self):
        return self.xml
    
class SubroutineBodyHandler:
    def __init__(self) -> None:
        self.xml = ''
    
    def processXML(self,unstructured_xml):
        self.xml = '<subroutineBody>\n'
        # 1. 从XML中提取出'{'
        if not unstructured_xml[0][0] == '{':
            raise GrammarException("subroutineBody must have '{'")
        self.xml += common_convert('symbol')('{') + "\n"
        # 2. 从XML中提取出varDec
        var_dec_handlers=[]
        var_dec_indice = [index for index ,element in enumerate(unstructured_xml) if element[0] == 'var']
        for start_index,end_index in zip(var_dec_indice,var_dec_indice[1:]+[len(unstructured_xml)]):
            var_dec_handler = VarDecHandler()
            var_dec_handler.processXML(unstructured_xml[start_index:end_index])
            var_dec_handlers.append(var_dec_handler)
        # 3. 从XML中提取出statements
        statements_handler = StatementsHandler()
        # 4. 从XML中提取出'}'
        if not unstructured_xml[-1][0] == '}':
            raise GrammarException("subroutineBody must have '}'")
        self.xml += common_convert('symbol')('}') + "\n"
        # 5. 在末尾添加</subroutineBody>
        self.xml += "</subroutineBody>\n"
        pass

    def toXML(self):
        return self.xml

class SubroutineDecHandler:
    def __init__(self) -> None:
        self.xml = ''

    def processXML(self,unstructured_xml):

        self.xml = '<subroutineDec>\n'
        #1. 从XML中提取出constructor|function|method
        subroutine_type = unstructured_xml[0][0]
        name_type = unstructured_xml[0][1]
        self.xml += common_convert(name_type)(subroutine_type) + "\n"
        #2. 从XML中提取出void|type
        subroutine_return_type = unstructured_xml[1][0]
        name_type = unstructured_xml[1][1]
        self.xml += common_convert(name_type)(subroutine_return_type) + "\n"
        #3. 从XML中提取出subroutineName
        subroutine_name = unstructured_xml[2][0]
        name_type = unstructured_xml[2][1]
        self.xml += common_convert(name_type)(subroutine_name) + "\n"
        #4. 从XML中提取出'('和')',没有其中一个就报错，然后依靠'('和')'来提取parameterList
        start_index = [index for index ,element in enumerate(unstructured_xml) if element[0] == '(']
        end_index = [index for index ,element in enumerate(unstructured_xml) if element[0] == ')']
        if not start_index and 3 not in start_index:
            raise GrammarException("subroutineDec must have '('")
        if not end_index:
            raise GrammarException("subroutineDec must have ')'")
        if not unstructured_xml[3][0] == '(':
            raise GrammarException("subroutineDec must have '('")
        self.xml += common_convert('symbol')('(') + "\n"
        #5. 从XML中提取出parameterList, 这里有些问题, 因为parameterList中可能没有参数
        end_index = end_index[0]
        param_list_handler = ParameterListHandler()
        param_list_handler.processXML(unstructured_xml[4:end_index])
        self.xml += param_list_handler.toXML()
        #6. 从XML中提取出')'
        self.xml += common_convert('symbol')(')') + "\n"
        #7. 从XML中提取出subroutineBody
        subroutine_body_handler = SubroutineBodyHandler()
        subroutine_body_handler.processXML(unstructured_xml[end_index:])
        self.xml += subroutine_body_handler.toXML()

        self.xml += "</subroutineDec>\n"
        pass

    def toXML(self):    
        return self.xml

class ClassHandler:
    def __init__(self) -> None:
        self.xml = ''
        self.structured_dict = {'className':'','classVarDec':[],'subroutineDec':[]}
    
    # unstructured_xml 是一个list ==[(word,identifier|keyword|symbol|stringConst|intConst),...]
    def processXML(self,unstructured_xml):
        if not unstructured_xml[0] == 'class':
            raise GrammarException("class must be the first token in the file")
        self.xml = '<class>\n'

        # 1. 从XML中提取出className,并添加到xml中
        class_name = unstructured_xml[1][0]
        self.xml += common_convert(unstructured_xml[1][0])(class_name) + "\n"

        # 2. 从XML中提取出classVarDec
        var_dec_handlers=[]
        class_var_dec_indice = [index for index ,element in enumerate(unstructured_xml) if element[0] in ['static','field']]
        for start_index,end_index in zip(class_var_dec_indice,class_var_dec_indice[1:]+[len(unstructured_xml)]):
            var_dec_handler = ClassVarDecHandler()
            var_dec_handler.processXML(unstructured_xml[start_index:end_index])
            var_dec_handlers.append(var_dec_handler)

        # 3. 从XML中提取出subroutineDec
        subroutine_dec_handlers=[]
        subroutine_dec_indice = [index for index ,element in enumerate(unstructured_xml) if element[0] in ['constructor','function','method']]
        for start_index,end_index in zip(subroutine_dec_indice,subroutine_dec_indice[1:]+[len(unstructured_xml)]):
            subroutine_dec_handler = SubroutineDecHandler()
            subroutine_dec_handler.processXML(unstructured_xml[start_index:end_index])
            subroutine_dec_handlers.append(subroutine_dec_handler)

        # 4. 将classVarDec和subroutineDec的结果转换为XML
        for var_dec_handler in var_dec_handlers:
            self.xml += var_dec_handler.toXML()
        for subroutine_dec_handler in subroutine_dec_handlers:
            self.xml += subroutine_dec_handler.toXML()
        # 5. 添加</class>结尾
        self.xml += '</class>\n'

    def toXML(self):
        return self.xml
    
class Grammar:
    def __init__(self) -> None:
        pass 
    
    # unstructured_xml 是一个list ==[(word,identifier|keyword|symbol|stringConst|intConst),...]
    def processUnstructuredXML(self,unstructured_xml):
        # 1. 从XML中提取出class
        class_indice = [index for index ,element in enumerate(unstructured_xml) if element[0] == 'class']
        if not class_indice and 0 not in class_indice:
            raise GrammarException("there is not a class in the file And first token must be class")

        class_handlers = []
        # 2. 构建ClassHandler来处理class
        for start_index,end_index in zip(class_indice,class_indice[1:]+[len(unstructured_xml)]):
            class_handler = ClassHandler()
            class_handler.processXML(unstructured_xml[start_index:end_index])
            class_handlers.append(class_handler)

        # 3. 将classHandler的结果转换为XML
        result_xml = ''
        for class_handler in class_handlers:
            result_xml += class_handler.toXML()

        # 4. return XML
        return result_xml