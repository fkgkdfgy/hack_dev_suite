# coding=UTF-8
from utilis import VMTranslatorException

def is_memory_instruction(segments):
    return 'pop' == segments[0] or 'push' == segments[0]

def add_comment(comment):
    def inner_add_comment(func):
        def inner_function(*args,**kwargs):
            result = comment
            result += func(*args,**kwargs)
            return result
        return inner_function
    return inner_add_comment

# 目前仅用于检查offset 是否是正数，之后可能会用于添加BuiltInFunction
def basic_check(f):
    def inner_function(obj,input):
        if not input.isdigit():
            raise VMTranslatorException('offset({0}) of function({1}) is not a integrator'.format(input,str(f)))
        return f(obj,input)
    return inner_function

# 新的地址保存在D中
# @add_comment(comment='// get base_addr + offset into D registor')
def get_label_addr(builtin_label,offset):
    int_offset = int(offset)
    description = '''@{1}
                     D=A
                     @{0}
                     D=M{2}D
    '''.format(builtin_label,str(abs(int_offset)),'+' if int_offset>0 else '-')
    return description


# 默认需要保存的数据存储在D中
# @add_comment(comment='// push data in D reg into stack')
def push_stack():
    description='''@SP
                    A=M
                    M=D
                    @SP
                    M=M+1
    '''
    return description

# 默认pop 的弹出的数据保存在 D 寄存器
# @add_comment(comment='// pop data in stack into D reg')
def pop_stack():
    description='''@SP  
                    A=M-1
                    D=M
                    @SP
                    M=M-1
    '''
    return description

# @add_comment(comment='// save the data of addr stored in D registor into D')
def get_value():
    description='''A=D
                   D=M
    '''
    return description

def move_constant_to_D(value):
    description ='''@{0}
                     D=A
                     '''.format(value)
    return description

# @add_comment(comment='// move data stored in Reg into D reg')
def move_reg_to_D(reg):
    description='''@{0}
                   D=M
    '''.format(reg)
    return description

# @add_comment(comment='// move data stored in D into other Reg')
def move_D_to_reg(reg):
    description='''@{0}
                   M=D
    '''.format(reg)
    return description

def basic_code_template_for_push(base_addr,offset):
    description = ''
    description += get_label_addr(base_addr,offset)
    description += get_value()
    description += push_stack()
    return description

def basic_code_template_for_pop(base_addr,offset):
    description = ''
    description += get_label_addr(base_addr,offset)
    description += move_D_to_reg('R13')
    description += pop_stack()
    description += '''@R13
                      A=M
                      M=D
    '''
    return description

def basic_code_template_for_push_pure_value(pure_value):
    description = ''
    description += move_constant_to_D(pure_value)
    description += push_stack()
    return description

def basic_code_template_alg_with_2arg(alg):
    description = ''
    description += pop_stack()
    description += move_D_to_reg('R13')
    description += pop_stack()
    description += '''@R13
                      {0}
                      '''.format(alg)
    description += push_stack()
    return description

def basic_code_template_alg_with_1arg(alg):
    description = ''
    description += pop_stack()
    description += '''{0}
    '''.format(alg)
    description += push_stack()
    return description

def get_standard_code_block(code):
    result = ''
    while code :
        index = code.find('\n')
        index = index if index >=0 else len(code)-1
        target_line = code[0:index+1]
        while target_line and target_line[0] == ' ':
            target_line =target_line[1:]
        result += target_line
        code = code[index+1:]
    return result
        
def insert_comment_to_n_line(code,comment):
    index = code.find('\n')
    index = index if index>=0 else len(code)
    return code[0:index]+'// {0}'.format(comment) + code[index:]

MemoryInsBuiltInKeyWords=['pop','push']
MemorySegmentsBuiltInKeyWords=['local','argument','this','that','temp','pointer','static','constant']
AlgInsBuiltInKeyWords=['add','sub','neg','eq','gt','lt','and','or','not']
BranchInsBuiltInKeyWords=['label','goto','if-goto']
FunctionInsBuiltInKeyWords = ['function','call','return']

function_count = 0

class Translator:

    def __init__(self,frame_name):
        self.frame_name = frame_name
        self.eq_count = 0
        self.gt_count = 0
        self.lt_count = 0
        self.memory_ins = {'push_local':self.push_local,
                           'push_argument':self.push_argument,
                           'push_this':self.push_this,
                           'push_that':self.push_that,
                           'push_static':self.push_static,
                           'push_constant':self.push_constant,
                           'push_pointer':self.push_pointer,
                           'push_temp':self.push_temp,
                           'pop_local':self.pop_local,
                           'pop_argument':self.pop_argument,
                           'pop_this':self.pop_this,
                           'pop_that':self.pop_that,
                           'pop_static':self.pop_static,
                           'pop_pointer':self.pop_pointer,
                           'pop_temp':self.pop_temp,
                           }
        self.algorithm_ins = {
                            'add':self.alg_add,
                            'sub':self.alg_sub,
                            'neg':self.alg_neg,
                            'eq':self.alg_eq,
                            'gt':self.alg_gt,
                            'lt':self.alg_lt,
                            'and':self.alg_and,
                            'or':self.alg_or,
                            'not':self.alg_not,
                            }
        self.branch_ins = {'goto':self.branch_goto,
                           'label':self.branch_label,
                           'if-goto':self.branch_if_goto}
        self.function_ins = {'function':self.function_function,
                             'call':self.function_call,
                             }
        self.functions = {}
        self.function_in_process=None

    def process(self,segments):
        if not segments:
            return None
        print('segments:',segments)
        if segments[0] in MemoryInsBuiltInKeyWords:
            if segments[1] in MemorySegmentsBuiltInKeyWords:
                message_label=segments[0]+'_'+segments[1]
                result = self.memory_ins[message_label](segments[2])
            else:
                raise VMTranslatorException('Unkown instruction label{0} is not find in MemorySegmentsBuiltInKeyWords'.format(segments[1]))
        elif segments[0] in AlgInsBuiltInKeyWords:
            message_label = segments[0]
            result = self.algorithm_ins[message_label]()
        elif segments[0] in BranchInsBuiltInKeyWords:
            message_label = segments[0]
            result = self.branch_ins[message_label](segments[1])
        elif segments[0] in FunctionInsBuiltInKeyWords:
            message_label = segments[0]
            if message_label == 'return':
                result = self.function_return()
            else:
                result = self.function_ins[message_label](segments[1],segments[2])    
        else:
            raise VMTranslatorException('Unkown instruction label{0}'.format(segments))

        if result:
            standard_result = get_standard_code_block(result)
            standard_result_with_code_as_comment = insert_comment_to_n_line(standard_result,'[ {0} ]'.format(' '.join(segments)))
            return standard_result_with_code_as_comment
        return None
    
    @basic_check
    def push_local(self,offset):
        return basic_code_template_for_push('LCL',offset)

    @basic_check
    def push_argument(self,offset):
        return basic_code_template_for_push('ARG',offset)

    @basic_check
    def push_this(self,offset):
        return basic_code_template_for_push('THIS',offset)

    @basic_check
    def push_that(self,offset):
        return basic_code_template_for_push('THAT',offset)

    @basic_check
    def pop_local(self,offset):
        return basic_code_template_for_pop('LCL',offset)

    @basic_check
    def pop_argument(self,offset):
        return basic_code_template_for_pop('ARG',offset)

    @basic_check
    def pop_this(self,offset):
        return basic_code_template_for_pop('THIS',offset)

    @basic_check
    def pop_that(self,offset):
        return basic_code_template_for_pop('THAT',offset)

    @basic_check
    def push_constant(self,offset):
        return basic_code_template_for_push_pure_value(offset)

    @basic_check
    def push_temp(self,offset):
        if int(offset)>7:
            raise VMTranslatorException('offset({0}) for temp is larger than 7'.format(offset))
        target_reg = 'R{0}'.format(5+int(offset))
        description=''
        description+=move_reg_to_D(target_reg)
        description+=push_stack()
        return description

    @basic_check
    def pop_temp(self,offset):
        if int(offset)>7:
            raise VMTranslatorException('offset({0}) for temp is larger than 7'.format(offset))
        target_reg = 'R{0}'.format(5+int(offset))
        description =''
        description += pop_stack()
        description += move_D_to_reg(target_reg)
        return description

    @basic_check
    def push_pointer(self,offset):
        if int(offset) not in [0,1]:
            raise VMTranslatorException('offset({0}) for pointer is not 0 or 1'.format(offset))
        target_reg = 'THIS' if int(offset)==0 else 'THAT'
        description=''
        description+=move_reg_to_D(target_reg)
        description+=push_stack()
        return description

    @basic_check
    def pop_pointer(self,offset):
        if int(offset) not in [0,1]:
            raise VMTranslatorException('offset({0}) for pointer is not 0 or 1'.format(offset))
        target_reg = 'THIS' if int(offset)==0 else 'THAT'
        description =''
        description += pop_stack()
        description += move_D_to_reg(target_reg)
        return description
        
    @basic_check
    def push_static(self,offset):
        target_reg = self.frame_name+'.'+offset
        description=''
        description+=move_reg_to_D(target_reg)
        description+=push_stack()
        return description

    @basic_check
    def pop_static(self,offset):
        target_reg = self.frame_name+'.'+offset
        description =''
        description += pop_stack()
        description += move_D_to_reg(target_reg)
        return description

    # alg 中默认M保存的是第一个从栈中提取的参数
    #     如果需要两个参数 D 中保留最后一个从栈中提取的参数
    #     最终结果保存在D寄存器中
    def alg_add(self):
        return basic_code_template_alg_with_2arg('D=D+M')

    def alg_sub(self):
        return basic_code_template_alg_with_2arg('D=D-M')

    def alg_neg(self):
        return basic_code_template_alg_with_1arg('D=-D')

    def alg_eq(self):
        alg = '''D=D-M
                @{1}_EQTrue_{0}
                D;JEQ
                @{1}_EQTrueEnd_{0}
                D=0
                0;JMP
                ({1}_EQTrue_{0})
                D=-1
                ({1}_EQTrueEnd_{0})
        '''.format(self.eq_count,self.frame_name.upper())
        self.eq_count +=1
        return basic_code_template_alg_with_2arg(alg)

    def alg_gt(self):
        alg = '''D=D-M
                @{1}_GTTrue_{0}
                D;JGT
                @{1}_GTTrueEnd_{0}
                D=0
                0;JMP
                ({1}_GTTrue_{0})
                D=-1
                ({1}_GTTrueEnd_{0})
        '''.format(self.gt_count,self.frame_name.upper())
        self.gt_count +=1
        return basic_code_template_alg_with_2arg(alg)

    def alg_lt(self):
        alg = '''D=D-M
                @{1}_LTTrue_{0}
                D;JLT
                @{1}_LTTrueEnd_{0}
                D=0
                0;JMP
                ({1}_LTTrue_{0})
                D=-1
                ({1}_LTTrueEnd_{0})
        '''.format(self.lt_count,self.frame_name.upper())
        self.lt_count +=1
        return basic_code_template_alg_with_2arg(alg)

    def alg_and(self):
        return basic_code_template_alg_with_2arg('D=M&D')

    def alg_or(self):
        return basic_code_template_alg_with_2arg('D=M|D')

    def alg_not(self):
        return basic_code_template_alg_with_1arg('D=!D')
    
    def branch_label(self,label):
        return '''({0})
        '''.format(self.frame_name+'$'+label)  

    def branch_goto(self,label):
        description = '''@{0}${1}
                         0;JMP
        '''.format(self.frame_name,label) 
        return description

    def branch_if_goto(self,label):
        description = ''
        description += pop_stack()
        description += '''@{0}${1}
                          D;JNE
        '''.format(self.frame_name,label)
        return description
    
    def function_call(self,label,args_num):

        global function_count
        ret_label = '{0}$ret.{1}'.format(label,function_count)
        
        description =''
        description += basic_code_template_for_push_pure_value(ret_label)
        description += get_label_addr('LCL',0)
        description += push_stack()
        description += get_label_addr('ARG',0)
        description += push_stack()
        description += get_label_addr('THIS',0)
        description += push_stack()
        description += get_label_addr('THAT',0)
        description += push_stack()
        description += get_label_addr('SP',-5-int(args_num))
        description += move_D_to_reg('ARG')
        description += get_label_addr('SP',0)
        description += move_D_to_reg('LCL')
        description +='''@{0}
                         0;JMP
        '''.format(label) 
        description += '''({0})
        '''.format(ret_label)

        function_count+=1
        return description

    def function_function(self,label,nvars):
        function_name = label
        description = ''
        description += '''({0})
        '''.format(function_name) 
        for i in range(int(nvars)):
            description += basic_code_template_for_push_pure_value('0')
        self.frame_name = label
        return description    

    def function_return(self):
        description = ''
        description += get_label_addr('LCL',-5)
        description += get_value()
        description += move_D_to_reg('R14') # 保存return.addr 
        description += self.pop_argument('0')
        description += get_label_addr('ARG',1)
        description += move_D_to_reg('SP')
        description += get_label_addr('LCL',-1)
        description += get_value()
        description += move_D_to_reg('THAT')
        description += get_label_addr('LCL',-2)
        description += get_value()
        description += move_D_to_reg('THIS')
        description += get_label_addr('LCL',-3)
        description += get_value()
        description += move_D_to_reg('ARG')
        description += get_label_addr('LCL',-4)
        description += get_value()
        description += move_D_to_reg('LCL')
        description += move_reg_to_D('R14')
        description += '''A=D
                          0;JMP
        '''
        return description

if __name__ == '__main__':
    translator = Translator('Foo')
    
    import translator_parser
    test_parser = translator_parser.Parser()

    def example_test(inputs):
        print('TEST A NEW EXAMPLE: \n {0}'.format(inputs))
        for ins in inputs:
            segments = test_parser.Process(ins)
            print(segments)
            result = translator.process(segments)
            print(result)

    example1 = ['push constant 0']
    example_test(example1)

    example2 = ['function main 2',
                'push constant 1',
                'push local 1',
                'add',
                'return']
    example_test(example2)

    example3 = ['push constant 17',
                'push constant 555',
                'add',
                'function not_built_in_add 2',
                'pop argument 0',
                'pop argument 1',
                'add',
                'return',
                'function main 2',
                'push constant 1',
                'push constant 4',
                'pop argument 1',
                'pop argument 0',
                'call not_built_in_add 2',
                'push constant 17',
                'call not_built_in_add 2',
                'return']
    example_test(example3)

    example4 = ['function main 0',
                'push constant 1',
                'if-goto DO_SOMETHING',
                'push constant 100',
                'goto DO_SOMETHING_END',
                'label DO_SOMETHING',
                'push constant 999',
                'label DO_SOMETHING_END',
                'push constant 1',
                'add',
                'return']
    example_test(example4)