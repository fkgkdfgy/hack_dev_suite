import os
import sys
import argparse

from application import *

if __name__ == '__main__':

    # 获取输入参数, 只需要dir 和 output_path两个参数
    # dir 是必须有的参数，output_path 是可选参数
    # 如果没有指定output_path, 那么默认的output_path 是dir/output
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='the dir of jack files')
    parser.add_argument('-o', '--output_path', help='the output path of vm and xml files')
    args = parser.parse_args()

    # 获取 dir_path 的绝对路线
    dir_path = os.path.abspath(args.dir)
    output_path = args.output_path
    if not output_path:
        output_path = os.path.join(dir_path,'output')
        if not os.path.exists(output_path):
            os.makedirs(output_path)

    # 检查dir_path 是否存在
    if not os.path.exists(dir_path):
        raise Exception('dir_path {0} does not exist'.format(dir_path))
    
    # 处理dir_path 下的所有jack 文件
    try:
        processDir(dir_path,output_path)
    except Exception as e:
        print('error: {0}'.format(e))
        sys.exit(1)
