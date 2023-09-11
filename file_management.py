#! /usr/bin/env python3
import os
import subprocess
import time
from base import Base
from process import ProgressBar

# 挂在和卸载类
class MountUnmountManager:
    def __init__(self, source_path, logical_volume, error_handling , task_logger, debug_logger):
        self.logical_volume = logical_volume
        self.source_path = source_path
        self.task_logger = task_logger
        self.debug_logger = debug_logger
        self.base = Base(task_logger, debug_logger)
        self.error_handling = error_handling
        self.target_mount_point = ""
        self.source_mount_point = ""

    #输入需要的挂载点，就是要先创建对应的目录
    def mount_target_path(self, mount_point):
        self.debug_logger.log("执行挂载目标盘方法")
        print("执行挂载目标盘方法")
        target_path = self.logical_volume # 修改 目标盘逻辑卷
        self.task_logger.log("INFO", f"目标路径：{target_path}")
        buffer = False
        # 使用ProgressBar显示挂载进度
        progress_bar = ProgressBar(1)
        if target_path:
            
            command = f"sudo mount {target_path} {mount_point}"
            print(f"挂载目标盘方法de zhiling {command}")
            result = self.base.com(command).strip()
            print(result, f"变量类型 {type(result)}")
            if "失败" not in str(result):
                buffer = True
                progress_bar.update()
                self.debug_logger.log("挂载目标盘完成")
                print(f"挂载目标盘完成")
            else:
                for i in range(3):
                    result = self.base.com(command).strip()
                    if "失败" in str(result):
                        buffer = True
                        progress_bar.update()
                        print(f"第{i}次尝试，挂载目标盘完成")
                        break
            if buffer is False:
                self.error_handling.check_execution_result("多次挂载失败，进入错误处理") # 修改
            self.debug_logger.log("")
            progress_bar.close()  # 关闭进度条
        else:
            self.task_logger.log("ERROR", f"未找到配置项 'target_path' 中的路径")
            self.debug_logger.log("未找到配置项 'target_path' 中的路径")
            self.debug_logger.log("")
            progress_bar.close()  # 关闭进度条
            return False

    def mount_source_path(self, mount_point):
        self.debug_logger.log("执行挂载源盘方法")
        print("执行挂载源盘方法")
        #source_path = self.input_validator.get_paths().get('source_path')
        self.task_logger.log("INFO", f"源盘路径：{self.source_path}")
        buffer = False
        if self.source_path:
            # 使用ProgressBar显示挂载进度
            progress_bar = ProgressBar(1)
            command = f"sudo mount {self.source_path} {mount_point}"
            result = self.base.com(command).strip()
            print(result, f"变量类型 {type(result)}")
            if "失败" not in str(result):
                buffer = True
                progress_bar.update()
                self.debug_logger.log("挂载源盘完成")
                print(f"挂载源盘完成")
            else:
                for i in range(3):
                    result = self.base.com(command).strip()
                    if "失败" in str(result):
                        buffer = True
                        progress_bar.update()
                        print(f"第{i}次尝试，挂载源盘完成")
                        break
            if buffer is False:
                self.error_handling.check_execution_result("多次挂载失败，进入错误处理") # 修改
            self.debug_logger.log("")
            progress_bar.close()  # 关闭进度条
        else:
            self.task_logger.log("ERROR", f"未找到配置项 'source_path' 中的路径")
            self.debug_logger.log("未找到配置项 'source_path' 中的路径")
            self.debug_logger.log("")
            progress_bar.close()  # 关闭进度条
            return False

    def unmount_device(self, mount_point):
        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"执行卸载{mount_point}方法")
            self.debug_logger.log(f"执行卸载{mount_point}方法")
            command = f"sudo umount -l {mount_point}"
            self.base.com(command).strip()
            progress_bar.update()
            return True
        except subprocess.CalledProcessError as e:
            self.task_logger.log("ERROR", f"卸载失败：{e}")
            self.debug_logger.log(f"卸载失败：{e}")
            self.error_handling.handle_umount_failure(mount_point) # 错误处理
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行

    def bind_temporary_directory(self, source_directory, target_directory):
        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"执行绑定{target_directory}方法")
            self.debug_logger.log(f"开始执行绑定{target_directory}方法")
            command = f"sudo mount --bind {source_directory} {target_directory}"
            self.base.com(command)
            # subprocess.run(command, shell=True, check=True)
            print("绑定完成")
            progress_bar.update()
            return True
        except subprocess.CalledProcessError as e:
            self.task_logger.log("ERROR", f"绑定临时目录失败：{e}")
            self.debug_logger.log(f"绑定临时目录失败：{e}")
            print("绑定失败")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行

    def unbind_temporary_directory(self, target_directory):
        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"执行解绑{target_directory}方法")
            self.debug_logger.log(f"开始执行解绑{target_directory}方法")
            command = f"sudo umount {target_directory}"
            self.base.com(command)
            #subprocess.run(command, shell=True, check=True)
            progress_bar.update()
            return True
        except subprocess.CalledProcessError as e:
            self.task_logger.log("ERROR", f"解绑临时目录失败：{e}")
            self.debug_logger.log(f"解绑临时目录失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行

    # 返回目标盘挂载路径
    def get_target_mount_point(self):
        return self.target_mount_point
    
    # 返回源盘挂载路径
    def get_source_mount_point(self):
        return self.source_mount_point
# 创建和删除目录类，这个类有两个方法，
# 分别是创建目录方法和删除目录/文件方法。
# 每个方法都要验证是否成功。
# 针对创建方法，就是输入对应的路径信息和目录名然后创建相应的目录。
# 删除也同理。

class DirectoryFileManager:
    def __init__(self, task_logger, debug_logger):
        self.task_logger = task_logger
        self.debug_logger = debug_logger
        self.base = Base(task_logger, debug_logger)

    # 创建目录
    def create_directory(self, path, dir_name):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"执行创建目录 {path}{dir_name} 方法")
            self.debug_logger.log(f"执行创建目录 {path}{dir_name} 方法")
            sudo_command = f"sudo mkdir -p {path}{dir_name}"
            self.base.com(sudo_command)
            if self.base.check_path(f"{path}{dir_name}"):
                print(f"创建 {path}{dir_name} 成功")
                progress_bar.update()
                return True
            else:
                print(f"创建 {path}{dir_name} 失败")
                self.task_logger.log("WARNING", f"创建目录 {path}{dir_name} 失败")
                return False
        except subprocess.CalledProcessError as e:
            print(f"创建目录失败：{e}")
            self.task_logger.log("ERROR", f"创建目录失败：{e}")
            self.debug_logger.log(f"创建目录失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行

    # 删除目录
    def delete_path(self, path):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"执行删除 {path} 方法")
            self.debug_logger.log(f"开始删除 {path} ")

            if self.base.check_path(path):
                sudo_command = f"sudo rm -rf {path}/*"
                self.base.com(sudo_command).strip()
                print("目标盘挂载路径已清空")
                if not self.base.check_path(path):
                    progress_bar.update()
                    return True
                else:
                    self.task_logger.log("WARNING", f"删除 {path} 失败")
                    return False
            else:
                print("无法清空目标盘挂载路径")
                self.task_logger.log("ERROR", f"删除路径失败，路径不存在")
                self.debug_logger.log(f"删除路径失败，路径不存在")
                return False
        except subprocess.CalledProcessError as e:
            print(f"删除路径失败：{e}")
            self.debug_logger.log(f"删除路径失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行
        
# 解压类
class TarExtractor:
    def __init__(self, error_handling, task_logger, debug_logger):
        self.task_logger = task_logger
        self.debug_logger = debug_logger
        self.base = Base(task_logger, debug_logger)
        self.error_handling = error_handling

    def extract_tar_gz(self, tar_gz_file, target_path):
        print("开始解压备份包")
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar(1)
        # 记录开始时间
        start_time = time.time()
        try:
            self.task_logger.log("INFO", f"执行解压 {tar_gz_file} 方法")
            self.debug_logger.log(f"开始解压 {tar_gz_file} 到 {target_path}")
            
            if self.base.check_path(tar_gz_file):
            # 执行解压命令
                command = f"sudo tar -xzpvf {tar_gz_file} -C {target_path} --numeric-owner"
                self.base.com(command)
                # subprocess.run(command, shell=True, check=True)
                progress_bar.update()
                print("备份包已解压到目标盘挂载点")
                return True
            else:
                print("无法解压备份包到目标盘挂载点")
                self.error_handling.handle_extraction_failure(tar_gz_file, target_path)
        
        except subprocess.CalledProcessError as e:
            self.task_logger.log("ERROR", f"解压失败：{e}")
            self.debug_logger.log(f"解压失败：{e}")
            return False
        finally:
            # 记录结束时间
            end_time = time.time()
            # 计算经过的时间
            elapsed_time = end_time - start_time
            # 打印经过的时间
            print(f"经过的时间（秒）：{elapsed_time}")
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行
        
# 安装类
class InstallationManager:
    def __init__(self, task_logger, debug_logger):
        self.task_logger = task_logger
        self.debug_logger = debug_logger
        self.base = Base(task_logger, debug_logger)

    def install_packages_and_grub(self, target_mount_point, disk_path):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"disk_path: {disk_path}")
            self.debug_logger.log(f"disk_path: {disk_path}")

            print(f"disk_path: {disk_path}")
            commands = [
                "pwd",
                "sudo apt update",
                "apt install sudo",
                "sudo apt install grub2-common grub-pc-bin",
                f"sudo grub-install --recheck --no-floppy {disk_path}",
                "update-initramfs -u",
                "update-grub",
                "exit"
            ]

            combined_command = " && ".join(commands)
            command = f"sudo chroot {target_mount_point} /bin/bash -c 2> /dev/null '{combined_command}' --no-stdio" 

            completed_process = self.base.com(command)
            output_lines = completed_process.split('\n')

            if len(output_lines) > 0 and output_lines[0] == "/":
                print("已成功在chroot环境中安装软件包和grub")
                progress_bar.update()
                self.debug_logger.log("已成功在chroot环境中安装软件包和grub")
                return True
            else:
                print("未能进入chroot环境或软件包安装和grub安装失败")
                self.task_logger.log("WARNING", f"无法进入chroot环境或无法安装相关软件")
                self.debug_logger.log("未能进入chroot环境或软件包安装和grub安装失败")
                return False
        except subprocess.CalledProcessError as e:
            print(f"软件包安装和grub安装失败：{e}")
            self.task_logger.log("ERROR", f"软件包安装和grub安装失败：{e}")
            self.debug_logger.log(f"软件包安装和grub安装失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行