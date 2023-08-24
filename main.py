#! /usr/bin/env python3
import cmath
import logging
import os
import subprocess
from tqdm import tqdm
import configparser
from configuration_system_file import SystemConfigModifier
from error_handling import ErrorHandling
from file_management import DirectoryFileManager, InstallationManager, MountUnmountManager, TarExtractor
from input_validator import InputValidator
from disk_management import TargetDiskAnalyzer

DEBUG = False
source_mount_point = "/mnt/source"
target_mount_point = "/mnt/target"

# 输入与验证
def input_and_verification(validator):
    global DEBUG  # 声明要使用的全局变量 DEBUG
    # 读取
    if str(validator.read_config()) == 'False':
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
def manage_and_analyze_disks(validator):
    # 指定目标盘
    target_disk = validator.paths.get('target_path')

    # 创建目标盘分析类
    target_disk_analyzer = TargetDiskAnalyzer(target_disk, DEBUG)

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
def create_and_mount_paths(validator):
    # 创建临时目录
    directory_manager = DirectoryFileManager()
    if directory_manager.create_directory("/mnt", "source") and directory_manager.create_directory("/mnt", "target"):
        print("临时目录创建成功")
    else:
        print("临时目录创建失败")

    # 挂载源盘和目标盘
    mount_manager = MountUnmountManager(validator, DEBUG)
    if mount_manager.mount_source_path(source_mount_point) and mount_manager.mount_target_path(target_mount_point):
        print("源盘和目标盘挂载成功")
    else:
        print("源盘和目标盘挂载失败")


# 文件与目录管理
def manage_files_and_directories(mount_manager, directory_manager, tar_extractor, error_handling):
    
    # 清空挂载目标盘的路径下的所有文件
    if target_mount_point:
        if directory_manager.delete_path(target_mount_point):
            print("目标盘挂载路径已清空")
        else:
            print("无法清空目标盘挂载路径")

    # 获取源盘挂载路径
    # source_mount_point = mount_manager.get_source_mount_point()

    # 解压备份包到目标盘的挂载点中
    if source_mount_point and target_mount_point:
        tar_gz_file = os.path.join(source_mount_point, "backup.tar.gz")
        if os.path.exists(tar_gz_file):
            if tar_extractor.extract_tar_gz(tar_gz_file, target_mount_point):
                print("备份包已解压到目标盘挂载点")
            else:
                print("无法解压备份包到目标盘挂载点")
                error_handling.handle_extraction_failure(tar_gz_file, target_mount_point)
        else:
            print("源盘挂载路径中未找到备份包")
            error_handling.handle_extraction_failure(tar_gz_file, target_mount_point)
    else:
        print("未找到源盘挂载路径或目标盘挂载路径")
        error_handling.handle_extraction_failure(tar_gz_file, target_mount_point)

# 创建四个需要的目录
def create_file(directory_manager):
    directory_manager.create_directory({target_mount_point}, "proc")
    directory_manager.create_directory({target_mount_point}, "sys")
    directory_manager.create_directory({target_mount_point}, "mnt")
    directory_manager.create_directory({target_mount_point}, "media")
    directory_manager.create_directory({target_mount_point}, "tmp")
    directory_manager.create_directory({target_mount_point}, "dev")
    directory_manager.create_directory({target_mount_point}, "run")

# 修改系统配置文件
def modifying_configuration_file():
    systemconfigmodifier = SystemConfigModifier(target_mount_point, DEBUG)
    UUID = systemconfigmodifier.get_root_partition_uuid()
    systemconfigmodifier.modify_fstab_file(UUID)
    systemconfigmodifier.modify_resolv_conf_file()

# 绑定文件路径
def bind_file_path(mount_manager):
    mount_manager.bind_temporary_directory("/dev", f"{target_mount_point}/dev")
    mount_manager.bind_temporary_directory("/dev/pts", f"{target_mount_point}/dev/pts")
    mount_manager.bind_temporary_directory("/proc", f"{target_mount_point}/proc")
    mount_manager.bind_temporary_directory("/sys", f"{target_mount_point}/sys")

# 转入chroot环境
def enter_chroot(installation_manager, target_mount_point):
    if installation_manager.enter_chroot_environment(target_mount_point):
        print("已成功进入chroot环境")
        return True
    else:
        print("无法进入chroot环境")
        return False

# 安装相关软件包
def install_software_packages(installation_manager, disk_path, error_handling):
    if installation_manager.install_packages():
        print("已成功安装相关软件包")
        if installation_manager.install_grub_to_disk(disk_path):
            print("已成功安装grub软件包")
            return True
        else:
            print("无法安装软件包")
            error_handling.handle_grub_installation_failure("无法安装软件包", target_mount_point, source_mount_point)
            return False
    else:
        print("无法安装软件包")
        error_handling.handle_grub_installation_failure("无法安装软件包", target_mount_point, source_mount_point)
        return False

# 转出chroot环境
def quit_chroot(installation_manager, mount_manager, input_validator, error_handling):
    if installation_manager.exit_chroot_environment():
        print("已成功退出chroot环境")

        # 解绑文件路径  
        mount_manager.unbind_temporary_directory(f"{target_mount_point}/dev")
        mount_manager.unbind_temporary_directory(f"{target_mount_point}/dev/pts")
        mount_manager.unbind_temporary_directory(f"{target_mount_point}/proc")
        mount_manager.unbind_temporary_directory(f"{target_mount_point}/sys")

        # 根据用户设定，决定是否 umount 相关目录
        if input_validator.get_error_handling().get('umount_on_error'):
            # 进行 umount 相关目录的操作
            unmount_target_result = mount_manager.unmount_device(target_mount_point)
            unmount_soucer_result = mount_manager.unmount_device(source_mount_point)
            # 判断卸载目标盘路径
            if not unmount_target_result:
                 error_handling.handle_umount_failure(target_mount_point)
            # 判断卸载源盘路径
            if not unmount_soucer_result:
                error_handling.handle_umount_failure(source_mount_point)

        # 显示安装完成
        print("安装完成")   
        return True
    else:
        print("无法退出chroot环境")
        return False


def main():
    input_validator = InputValidator()
    mount_manager = MountUnmountManager(input_validator, debug_enabled=DEBUG)
    directory_manager = DirectoryFileManager()
    tar_extractor = TarExtractor(debug_enabled=DEBUG)
    error_handling = ErrorHandling(input_validator, mount_manager)

    input_and_verification(input_validator)
    #print("全局: " + str(DEBUG))

    manage_and_analyze_disks(input_validator)

    create_and_mount_paths(input_validator)

    # 创建对应文件夹，挂载文件，删除目标盘源文件，解压压缩包
    manage_files_and_directories(mount_manager, directory_manager, tar_extractor, error_handling)

    # 创建目录：mkdir proc sys mnt media tmp dev run
    create_file(directory_manager)

    # 修改系统配置文件
    modifying_configuration_file()

    # 绑定文件路径
    bind_file_path(mount_manager)

    # 这里存在一个问题，就是进入chroot转换的时候，需要手动输入指令exit之后，程序才会继续响应。
    installation_manager = InstallationManager(debug_enabled=DEBUG)
    target_disk = input_validator.paths.get('target_path') 
    if enter_chroot(installation_manager, target_mount_point):
        install_software_packages(installation_manager, target_disk, error_handling)# 获取目标盘的对应磁盘
        quit_chroot(installation_manager, mount_manager, input_validator, error_handling)


if __name__ == '__main__':
    main()
