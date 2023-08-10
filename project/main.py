#! usr/bin/env python3
import cmath
import logging
from tqdm import tqdm
import configparser
from Input_Analyze import InputValidator

# 输入与验证
def Input_and_Verification(validator):
    # 读取
    validator.read_config()
    
    # 验证备份包名称有效性
    is_backup_name_valid = validator.validate_backup_name()
    if is_backup_name_valid:
        print("备份包名称验证通过！")
    else:
        print("备份包名称验证未通过！")

    # 验证设备路径的有效性
    validator.validate_device_path()

    # 查询debug按钮信息
    validator.check_debug_switch()
    print("打印debug信息: " + str(validator.get_debug_info().get('debug_button')))
    
    # 查询错误处理配置信息
    true_error_handling_config = validator.check_error_handling_config()
    print("错误处理配置信息: " + str(true_error_handling_config))
    # return 

# 磁盘分析与管理
def Manage_and_Analyze_Disks():
    return

# 临时路径创建与挂载
def Create_and_Mount_Paths():
    return

# 文件与目录管理
def Manage_Files_and_Directories():
    return

# 权限升级
def Upgrade_Permission():
    return

# 修改系统配置文件
def Modifying_Configuration_File():
    return

# 绑定文件路径
def Bind_File_Path():
    return

# 转入chroot环境
def Enter_chroot():
    return

# 安装相关软件包
def Install_Software_Packages():
    return

# 转出chroot环境
def Quit_chroot():
    return

def main():
    input_validator = InputValidator()
    Input_and_Verification(input_validator)

if __name__ == '__main__':
    main()
