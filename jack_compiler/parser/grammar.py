from utils import *

class GrammarException(Exception):
    pass

class ClassVarDecHandler:
    def __init__(self) -> None:
        self.xml = ''
    
    def processXML(self,unstructured_xml):
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

    def toXML(self):
        return self.xml
    
class ParameterListHandler:
    def __init__(self) -> None:
        self.xml = ''
    
    def processXML(self,unstructured_xml):
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

    def toXML(self):
        return self.xml
    
class SubroutineBodyHandler:
    def __init__(self) -> None:
        self.xml = ''
    
    def processXML(self,unstructured_xml):
        # 1. 从XML中提取出'{'
        # 2. 从XML中提取出varDec
        # 3. 从XML中提取出statements
        # 4. 从XML中提取出'}'
        pass

    def toXML(self):
        return self.xml

class SubroutineDecHandler:
    def __init__(self) -> None:
        self.xml = ''

    def processXML(self,unstructured_xml):
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
        #4. 从XML中提取出'('
        if not unstructured_xml[3][0] == '(':
            raise GrammarException("subroutineDec must have '('")
        self.xml += common_convert('symbol')('(') + "\n"
        #5. 从XML中提取出parameterList, 这里有些问题, 因为parameterList中可能没有参数
        param_list_handler = ParameterListHandler()
        param_list_handler.processXML(unstructured_xml[4:-1])
        self.xml += param_list_handler.toXML()
        #6. 从XML中提取出')'
        if not unstructured_xml[-1][0] == ')':
            raise GrammarException("subroutineDec must have ')'")
        self.xml += common_convert('symbol')(')') + "\n"
        #7. 从XML中提取出subroutineBody
        subroutine_body_handler = SubroutineBodyHandler()
        subroutine_body_handler.processXML(unstructured_xml[5:-1])
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