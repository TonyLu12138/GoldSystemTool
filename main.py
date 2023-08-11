#! /usr/bin/env python3
import cmath
import logging
from tqdm import tqdm
import configparser
from input_validator import InputValidator

# 输入与验证
def input_and_verification(validator):
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
def manage_and_analyze_disks():
    return

# 临时路径创建与挂载
def create_and_mount_paths():
    return

# 文件与目录管理
def manage_files_and_directories():
    return

# 权限升级
def upgrade_permission():
    return

# 修改系统配置文件
def modifying_configuration_file():
    return

# 绑定文件路径
def bind_file_path():
    return

# 转入chroot环境
def enter_chroot():
    return

# 安装相关软件包
def install_software_packages():
    return

# 转出chroot环境
def quit_chroot():
    return

def main():
    input_validator = InputValidator()
    input_and_verification(input_validator)

if __name__ == '__main__':
    main()
