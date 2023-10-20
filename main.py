#! /usr/bin/env python3
import os
import subprocess
from configuration_system_file import SystemConfigModifier
from error_handling import ErrorHandling
from file_management import DirectoryFileManager, InstallationManager, MountUnmountManager, TarExtractor
from input_validator import InputValidator
from disk_management import TargetDiskAnalyzer

DEBUG = False
logical_volume = ""
source_mount_point = "/mnt/source"
target_mount_point = "/mnt/target"


# 输入与验证
def input_and_verification(validator):
    global DEBUG  # 声明要使用的全局变量 DEBUG
    # 读取
    if (str(validator.read_config()) == 'False'):
        print("配置文件读取失败，程序中断")
        exit()
    
    # 查询debug按钮信息
    validator.check_debug_switch()

    # 验证设备路径的有效性
    if str(validator.validate_device_path()) == 'False':
        print("设备路径无效，程序中断")
        exit()

    DEBUG = validator.get_debug_info().get('debug_button')
    # print("打印debug信息: " + str(validator.get_debug_info().get('debug_button')))
    # print("全局: " + str(DEBUG))
    # 查询错误处理配置信息
    true_error_handling_config = validator.check_error_handling_config()
    print("错误处理配置信息: " + str(true_error_handling_config))
    # return 

# 磁盘分析与管理
def manage_and_analyze_disks(validator, task_logger, debug_logger):
    global logical_volume
    # 指定目标盘
    target_disk = validator.paths.get('target_path')

    # 创建目标盘分析类
    target_disk_analyzer = TargetDiskAnalyzer(target_disk, task_logger, debug_logger)

    # 获取目标盘分区结构
    partition_structure = target_disk_analyzer.get_partition_structure()
  
    # 获取目标盘根目录所在分区
    logical_volume = "/dev/" + target_disk_analyzer.get_root_partition(partition_structure)

# 临时路径创建与挂载
def create_and_mount_paths(directory_manager, mount_manager, error_handling):
    # 创建临时目录
    directory_manager.create_directory("/mnt", "/source") 
    directory_manager.create_directory("/mnt", "/target")

    # 挂载源盘和目标盘
    if not mount_manager.mount_source_path(source_mount_point):
        error_handling.check_execution_result(False)
    if not mount_manager.mount_target_path(target_mount_point):
        error_handling.check_execution_result(False)


# 文件与目录管理
def manage_files_and_directories(mount_manager, error_handling_bool, backup, directory_manager, tar_extractor, error_handling):
    # 清空挂载目标盘的路径下的所有文件
    if not directory_manager.delete_path_file(target_mount_point):
        # 根据用户设定，决定是否 umount 相关目录
        umount(mount_manager, error_handling_bool, error_handling, directory_manager)

    # 解压备份包到目标盘的挂载点中
    tar_gz_file = os.path.join(source_mount_point, backup)
    if not tar_extractor.extract_tar_gz(tar_gz_file, target_mount_point):
        error_handling.handle_extraction_failure(tar_gz_file, target_mount_point)
                
# 创建四个需要的目录
def create_file(directory_manager):
    print("开始创建")
    # 定义需要创建的目录列表
    directories_to_create = ["/proc", "/sys", "/mnt", "/media", "/tmp", "/dev", "/run"]
    for directory in directories_to_create:
        directory_manager.create_directory(target_mount_point, directory)
    print("创建结束")

# 修改系统配置文件
def modifying_configuration_file(task_logger, debug_logger):
    systemconfigmodifier = SystemConfigModifier(target_mount_point, logical_volume, task_logger, debug_logger)
    UUID = systemconfigmodifier.get_root_partition_uuid()

    systemconfigmodifier.modify_fstab_file(UUID)
    systemconfigmodifier.modify_resolv_conf_file()

# 绑定文件路径
def bind_file_path(mount_manager):
    # 定义需要绑定的文件路径列表
    paths_to_bind = ["/dev", "/dev/pts", "/proc", "/sys"]
    for path in paths_to_bind:
        mount_manager.bind_temporary_directory(path, f"{target_mount_point}/{path[1:]}")

# 转入chroot环境、安装相关软件包、转出chroot环境
def enter_chroot(installation_manager, target_mount_point, target_disk, error_handling):
    print(f"检查：{installation_manager.enter_chroot(target_mount_point)}")
    if installation_manager.enter_chroot(target_mount_point):
        print("成功进入chroot环境")
        if installation_manager.install_packages(target_mount_point):
            print("成功安装软件包")
            if installation_manager.install_grub(target_mount_point, target_disk):
                print("成功安装grub")
                exit_chroot(installation_manager, target_mount_point)
            else:
                print("安装grub失败，退出chroot环境")
                exit_chroot(installation_manager, target_mount_point)
                error_handling.handle_next_step_failure("安装grub失败", target_mount_point, source_mount_point)
        else:
            print("安装软件包失败，退出chroot环境")
            exit_chroot(installation_manager, target_mount_point)
            error_handling.handle_next_step_failure("安装软件包失败", target_mount_point, source_mount_point)
    else:
        print("进入chroot环境失败，执行错误处理")
        error_handling.handle_next_step_failure("进入chroot环境失败", target_mount_point, source_mount_point)
        # 错误处理

def exit_chroot(installation_manager, target_mount_point):
    if installation_manager.exit_chroot(target_mount_point):
        print("成功退出chroot")
    else:
        print("退出chroot失败")
        exit()

# 
def unbind_and_umount(mount_manager):
    mount_manager.unbind_temporary_directory(f"{target_mount_point}/dev/pts")
    mount_manager.unbind_temporary_directory(f"{target_mount_point}/dev")
    mount_manager.unbind_temporary_directory(f"{target_mount_point}/proc")
    mount_manager.unbind_temporary_directory(f"{target_mount_point}/sys")

def umount(mount_manager, error_handling_bool, error_handling, directory_manager):
    # 根据用户设定，决定是否 umount 相关目录
    if error_handling_bool:
        # 进行 umount 相关目录的操作
        if not mount_manager.unmount_device(target_mount_point):
            error_handling.handle_umount_failure(target_mount_point)
        if not mount_manager.unmount_device(source_mount_point):
            error_handling.handle_umount_failure(source_mount_point)
        
        directory_manager.delete_path(target_mount_point)
        directory_manager.delete_path(source_mount_point)

def main():
    input_validator = InputValidator()
    
    # 执行读取配置文件
    input_and_verification(input_validator)

    # 获取目标盘路径
    target_disk = input_validator.get_paths().get('target_path')

    # 获取源爿路径
    source_path = input_validator.get_paths().get('source_path')

    # 获取错误处理配置
    error_handling_bool = input_validator.get_error_handling().get('umount_on_error')
    
    # 获取备份包名称
    backup = input_validator.get_backup_info().get('backup_name')

    task_logger = input_validator.get_log_object()
    debug_logger = input_validator.get_debug_object()
    
    error_handling = ErrorHandling(error_handling_bool, task_logger, debug_logger)
    
    directory_manager = DirectoryFileManager(task_logger, debug_logger) 
    tar_extractor = TarExtractor(error_handling, task_logger, debug_logger)
    installation_manager = InstallationManager(task_logger, debug_logger)
    
    
    # 磁盘分析与管理
    manage_and_analyze_disks(input_validator, task_logger, debug_logger)
    mount_manager = MountUnmountManager(source_path, logical_volume, error_handling, task_logger, debug_logger)

    # 创建对应文件夹，挂载文件
    create_and_mount_paths(directory_manager, mount_manager, error_handling)

    # 验证备份包名称有效性
    is_backup_name_valid = input_validator.validate_backup_name(source_mount_point)
    if is_backup_name_valid:
        print("备份包名称验证通过！")
    else:
        print("备份包名称验证未通过！")
        umount(mount_manager, error_handling_bool, error_handling, directory_manager)
        exit()

    # 删除目标盘源文件，解压压缩包
    manage_files_and_directories(mount_manager, error_handling_bool, backup, directory_manager, tar_extractor, error_handling)

    # 创建目录：mkdir proc sys mnt media tmp dev run
    create_file(directory_manager)

    # 修改系统配置文件
    modifying_configuration_file(task_logger, debug_logger)

    # 绑定文件路径
    bind_file_path(mount_manager)

    # 进入chroot环境安装相关软件包
    enter_chroot(installation_manager, target_mount_point, target_disk, error_handling)
    
    unbind_and_umount(mount_manager)

    umount(mount_manager, error_handling_bool, error_handling, directory_manager)

    # 显示安装完成
    print("安装完成") 
if __name__ == '__main__':
    main()
