import sys
import os

dir_name = os.path.dirname(__file__)
sys.path.append(dir_name)

import application

# 调用同一个文件夹下的main.py 参数就是输入dir_path
# 检查dir_path下是否存在一个output文件夹
# 对比 output 文件夹和 reference 文件夹下 所有的同名文件
# 如果有不同的就输出文件名，已经对应的行号 
def process_dir(dir_path):
    # 0. 检查dir_path 是否存在
    if not os.path.exists(dir_path):
        raise Exception('dir_path {0} does not exist'.format(dir_path))
    # 1. 调用同一个文件夹下的main.py 参数就是输入dir_path
    output_path = os.path.join(dir_path,'output')
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    reference_path = os.path.join(dir_path,'reference')
    if not os.path.exists(reference_path):
        raise Exception('reference_path {0} does not exist'.format(reference_path))
    application.processDir(dir_path,output_path)
    # 2. 对比 output 文件夹和 reference 文件夹下 所有的同名文件
    file_error={}
    for file_name in os.listdir(reference_path):
        if file_name.endswith('.vm'):
            file_error[file_name] = []
            reference_file_path = os.path.join(reference_path,file_name)
            output_file_path = os.path.join(output_path,file_name)
            if not os.path.exists(output_file_path):
                raise Exception('output_file_path {0} does not exist'.format(output_file_path))
            with open(reference_file_path,'r') as f:
                reference_lines = f.readlines()
            with open(output_file_path,'r') as f:
                output_lines = f.readlines()
            if len(reference_lines) != len(output_lines):
                file_error[file_name].append('file {0} has different lines\n'.format(file_name))
                continue
            for index, (reference_line, output_line) in enumerate(zip(reference_lines,output_lines)):
                if reference_line != output_line:
                    file_error[file_name].append('file {0} has different lines\n'.format(file_name))
                    file_error[file_name].append('line {0} is different\n'.format(index))
                    file_error[file_name].append('reference line is {0}\n'.format(reference_line))
                    file_error[file_name].append('output line is {0}\n'.format(output_line))
                    continue
            if len(file_error[file_name]) == 0:
                print('file {0} is correct\n'.format(file_name))
    # 3. export file_error into output_path/../error.txt
    error_file_path = os.path.join(output_path,'..','error.txt')
    with open(error_file_path,'w') as f:
        for file_name, error_lines in file_error.items():
            f.write('FILE {0} has error\n'.format(file_name))
            f.write('FILE ERROR NUM: {0}\n'.format(len(error_lines)))
            f.write('---------------------\n')
            for error_line in error_lines:
                f.write(error_line)

if __name__ == '__main__':
    # 对 dir_name 下的test_material/Pong 文件夹进行测试
    dir_path = os.path.join(dir_name,'test_material','Pong')
    process_dir(dir_path)
    # 对 dir_name 下的test_material/Square 文件夹进行测试
    dir_path = os.path.join(dir_name,'test_material','Square')
    process_dir(dir_path)