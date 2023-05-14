# coding=UTF-8
from utilis import VMTranslatorException

def is_memory_instruction(segments):
    return 'pop' == segments[0] or 'push' == segments[0]

# 目前仅用于检查offset 是否是正数，之后可能会用于添加BuiltInFunction
def basic_check(f):
    def inner_function(obj,input):
        if not input.isdigit():
            raise VMTranslatorException('offset({0}) of function({1}) is not a integrator'.format(input,str(f)))
        return f(obj,input)
    return inner_function

# 新的地址保存在D中
def get_label_addr(builtin_label,offset):
    int_offset = int(offset)
    description = '''
    @{1}
    D=A

    @{0}
    D=M{2}D
    '''.format(builtin_label,str(abs(int_offset)),'+' if int_offset>0 else '-')
    return description

def get_value_of_reg():
    description='''
    A=D
    D=M
    '''
    return description

# 默认需要保存的数据存储在D中
def push_stack():
    description='''
    @SP
    A=M
    M=D

    @SP
    M=M+1
    '''
    return description

# 默认pop 的目标地址保存在 D 寄存器
def pop_stack():
    description='''
    @R13
    M=D

    @SP
    A=M-1
    D=M

    @SP
    M=M-1

    @R13
    A=M
    M=D
    '''
    return description

def get_value():
    description='''
    A=D
    D=M
    '''

def move_reg_to_D(reg):
    description='''
    @{reg}
    D=M
    '''.format(reg)
    return description

def move_D_to_reg(reg):
    description='''
    @{reg}
    M=D
    '''.format(reg)
    return description

def basic_code_template_for_push(base_addr,offset):
    description = ''
    description += get_label_addr(base_addr,offset)
    description += get_value_of_reg()
    description += push_stack()
    return description

def basic_code_template_for_pop(base_addr,offset):
    description = ''
    description += get_label_addr(base_addr,offset)
    description += pop_stack()
    return description

def basic_code_template_for_push_pure_value(pure_value):
    description = ''
    description +='''
    @{0}
    D=A
    '''.format(pure_value)
    description += push_stack()
    return description

def basic_code_template_alg_with_2arg(alg):
    description = ''
    description += pop_stack()
    description += move_D_to_reg('R13')
    description += pop_stack()
    description += '''
    @R13
    {0}
    '''.format(alg)
    description += push_stack()
    return description

def basic_code_template_alg_with_1arg(alg):
    description = ''
    description += pop_stack()
    description += '''
    {0}
    '''.format(alg)
    description += push_stack()
    return description

MemoryInsBuiltInKeyWords=['pop','push']
MemorySegmentsBuiltInKeyWords=['local','argument','this','that','temp','pointer','static','constant']
AlgInsBuiltInKeyWords=['add','sub','neg','eq','gt','lt','and','or','not']
BranchInsBuiltInKeyWords=['label','goto','if-goto']
FunctionInsBuiltInKeyWords = ['function','call','return']

function_call = 0

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
        self.functions = {}
        self.function_in_process=None

    def process(self,segments):
        if not segments:
            return None

        if self.function_in_process:
            result = self.function_in_process.process(segments)
            return result
        if segments[0] in MemoryInsBuiltInKeyWords:
            if segments[1] in MemorySegmentsBuiltInKeyWords:
                message_label=segments[0]+'_'+segments[1]
                return self.memory_ins[message_label](segments[3])
            raise VMTranslatorException('Unkown instruction label{0} is not find in MemorySegmentsBuiltInKeyWords'.format(segments[1]))
        if segments[0] in AlgInsBuiltInKeyWords:
            message_label = segments[0]
            return self.algorithm_ins[message_label]()
        if segments[0] in BranchInsBuiltInKeyWords:
            message_label = segments[0]
            return self.branch_ins[message_label]
        if segments[0] == 'function':
            self.function_in_process = FunctionTranslator(self.frame_name+'.'+segments[1],segments[2])
            self.functions[self.frame_name+'.'+segments[1]] = self.function_in_process
            return None
        raise VMTranslatorException('Unkown instruction label{0}'.format(segments))
    
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
        if offset>7:
            raise VMTranslatorException('offset({0}) for temp is larger than 7'.format(offset))
        pure_value = 'R{0}'.format(5+offset)
        return basic_code_template_for_push(pure_value,0)

    @basic_check
    def pop_temp(self,offset):
        if int(offset)>7:
            raise VMTranslatorException('offset({0}) for temp is larger than 7'.format(offset))
        pure_value = 'R{0}'.format(5+offset)
        return basic_code_template_for_pop(pure_value,0)

    @basic_check
    def push_pointer(self,offset):
        if int(offset) not in [0,1]:
            raise VMTranslatorException('offset({0}) for pointer is not 0 or 1'.format(offset))
        return basic_code_template_for_push('THIS' if 0 else 'THAT',0)

    @basic_check
    def pop_pointer(self,offset):
        if int(offset) not in [0,1]:
            raise VMTranslatorException('offset({0}) for pointer is not 0 or 1'.format(offset))
        return basic_code_template_for_pop('THIS' if 0 else 'THAT',0)

    @basic_check
    def push_static(self,offset):
        return basic_code_template_for_push(self.frame_name+'.'+offset,0)

    @basic_check
    def pop_static(self,offset):
        return basic_code_template_for_push(self.frame_name+'.'+offset,0)

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
        alg = '''
              @{1}_EQTrue_{0}
              D=D-M;JEQ
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
        alg = '''
              @{1}_GTTrue_{0}
              D=D-M;JGT
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
        alg = '''
              @{1}_LTTrue_{0}
              D=D-M;JLT
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
        return basic_code_template_alg_with_2arg('D=!M')
    
    def branch_label(self,label):
        return '({0})'.format(self.frame_name+'$'+label)  

    def branch_goto(self,label):
        description = '''
        @{0}${1}
        0;JMP
        '''.format(self.frame_name,label) 
        return description

    def branch_if_goto(self,label):
        description = ''
        description += pop_stack()
        description += '''
        @{0}${1}
        D;JNE
        '''.format(self.frame_name,label)
        return description
    
    def function_call(self,label,args_num):
        
        label = '{0}$ret.{1}'.format(self.frame_name,function_call)
        
        description =''
        description += get_label_addr(label,0)
        description += push_stack()
        description += get_label_addr('LCL',0)
        description += push_stack()
        description += get_label_addr('ARG',0)
        description += push_stack()
        description += get_label_addr('THIS',0)
        description += push_stack()
        description += get_label_addr('THAT',0)
        description += push_stack()
        description += get_label_addr('SP',-5-args_num)
        description += move_D_to_reg('ARG')
        description += get_label_addr('SP',0)
        description += move_D_to_reg('LCL')
        description += self.branch_label('$ret.{}'.format(function_call))

        function_call+=1
        return description

class FunctionTranslator(Translator):
    def __init__(self, frame_name,vars_num):
        Translator.__init__(self,frame_name)
        self.total_codes='''({0})'''.format(frame_name) 
        self.vars_num = vars_num
        self.have_complete_code = False
        self.init_local_segment()

    def init_local_segment(self):
        description=''
        for i in range(self.vars_num):
            description += basic_code_template_for_push_pure_value('0')
        self.total_codes += description
    
    def process(self,segements):
        if not self.function_in_process:
            if segements[0]=='return':
                self.total_codes += self.function_return()
                return self.get_all_codes()
            result = Translator.process(self,segements)
            return result
        else:
            result = self.function_in_process.process(self,segements)
            if result:
                self.total_codes += result
                self.function_in_process = None
            return None
    def get_all_codes(self):
        return self.total_codes

    def function_return(self):
        description = ''
        description += get_label_addr('LCL',-5)
        description += get_value()
        description += move_D_to_reg('R13') # 保存return.addr 
        description += self.pop_argument(0)
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
        description += move_reg_to_D('R13')
        description += '''
        A=D
        0;JMP
        '''
        return description

if __name__ == '__main__':
    translator = Translator('Foo')
    
    