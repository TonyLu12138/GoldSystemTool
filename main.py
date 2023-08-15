#! /usr/bin/env python3
import cmath
import logging
from tqdm import tqdm
import configparser
from input_validator import InputValidator
from disk_management import TargetDiskAnalyzer
DEBUG = False

# 输入与验证
def input_and_verification(validator):
    global DEBUG  # 声明要使用的全局变量 DEBUG
    # 读取
    if not validator.read_config():
        print("配置文件读取失败，程序中断")
        exit()
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
    DEBUG = validator.get_debug_info().get('debug_button')
    print("打印debug信息: " + str(validator.get_debug_info().get('debug_button')))
    print("全局: " + str(DEBUG))
    # 查询错误处理配置信息
    true_error_handling_config = validator.check_error_handling_config()
    print("错误处理配置信息: " + str(true_error_handling_config))
    # return 

# 磁盘分析与管理
def manage_and_analyze_disks():
    # 指定目标盘
    target_disk = 'sdc'

    # 创建目标盘分析类
    target_disk_analyzer = TargetDiskAnalyzer(target_disk)

    # 获取目标盘分区结构
    partition_structure = target_disk_analyzer.get_partition_structure()
    if partition_structure is not None:
        print("目标盘分区结构：")
        print(partition_structure)
    else:
        print("无法获取目标盘分区结构")

    # 获取目标盘根目录所在分区
    root_partition = target_disk_analyzer.get_root_partition()
    if root_partition is not None:
        print(f"目标盘根目录所在分区：{root_partition}")
    else:
        print("无法确定目标盘根目录所在分区")

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
    print("全局: " + str(DEBUG))

    manage_and_analyze_disks()

if __name__ == '__main__':
    main()
