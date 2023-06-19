import sys
import os

dir_name = os.path.dirname(__file__)
sys.path.append(dir_name)

import application

if __name__ == '__main__':
    # 对 dir_name 下的test_material/BugReport 文件夹进行测试
    target_dir = os.path.join(dir_name,'test_material','BugReport')
    output_dir = os.path.join(target_dir,'output')
    application.processDir(target_dir,output_dir)
  