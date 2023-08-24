#! /usr/bin/env python3
import os
import subprocess
import time
from error_handling import ErrorHandling
from log_record import DebugLogger
from input_validator import InputValidator
from process import ProgressBar

# 挂在和卸载类
class MountUnmountManager:
    def __init__(self, input_validator, debug_enabled=False):
        self.input_validator = input_validator
        self.error_handling = ErrorHandling()
        self.debug_logger = DebugLogger("MountUnmountManager", debug_enabled)
        self.target_mount_point = ""
        self.source_mount_point = ""

    #输入需要的挂载点，就是要先创建对应的目录
    def mount_target_path(self, mount_point, max_retries=4, retry_delay=5):
        target_path = "/dev/ubuntu-vg1/ubuntu-lv1" # 修改 目标盘逻辑卷
        if target_path:

            # 使用ProgressBar显示挂载进度
            progress_bar = ProgressBar()

            for _ in range(max_retries):
                self.debug_logger.log(f"开始挂载 target_path 到 {mount_point}")
                result_bool, result_string = self.mount_path(target_path, mount_point)
                if result_bool:
                    self.debug_logger.log("target_path 挂载成功")
                    self.target_mount_point = result_string
                    return True
                else:
                    self.debug_logger.log("target_path 挂载失败，将在 {retry_delay} 秒后重试")
                    # 让程序暂停retry_delay秒
                    time.sleep(retry_delay)
                progress_bar.update()  # 更新进度条

            progress_bar.close()  # 关闭进度条

            self.debug_logger.log("多次挂载失败，进入错误处理")
            self.error_handling.check_execution_result("多次挂载失败，进入错误处理")   # 修改
            return False
        else:
            self.debug_logger.log("未找到配置项 'target_path' 中的路径")
            return False

    def mount_source_path(self, mount_point, max_retries=4, retry_delay=5):
        source_path = self.input_validator.get_paths().get('source_path')
        if source_path:

            # 使用ProgressBar显示挂载进度
            progress_bar = ProgressBar()

            for _ in range(max_retries):
                self.debug_logger.log(f"开始挂载 source_path 到 {mount_point}")
                result_bool, result_string = self.mount_path(source_path, mount_point)
                if result_bool:
                    self.debug_logger.log("source_path 挂载成功")
                    self.source_mount_point = result_string
                    return True
                else:
                    self.debug_logger.log("source_path 挂载失败，将在 {retry_delay} 秒后重试")
                    # 让程序暂停retry_delay秒
                    time.sleep(retry_delay)
                progress_bar.update()  # 更新进度条

            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("多次挂载失败，进入错误处理")
            self.error_handling.check_execution_result("多次挂载失败，进入错误处理") # 修改
            return False
        else:
            self.debug_logger.log("未找到配置项 'source_path' 中的路径")
            return False

    def mount_path(self, path, mount_point):
        try:
            command = f"sudo mount {path} {mount_point}"
            self.debug_logger.log(f"执行挂载命令：{command}")
            subprocess.run(command, shell=True, check=True)
            self.debug_logger.log(f"已成功挂载 {path} 到 {mount_point}")
            return True, mount_point
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"挂载失败：{e}")
            return False, mount_point

    def unmount_device(self, mount_point):
        try:
            command = f"sudo umount {mount_point}"
            self.debug_logger.log(f"执行卸载命令：{command}")
            subprocess.run(command, shell=True, check=True)
            self.debug_logger.log(f"已成功卸载 {mount_point}")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"卸载失败：{e}")
            self.error_handling.handle_umount_failure(mount_point) # 错误处理
            return False

    def bind_temporary_directory(self, source_directory, target_directory):
        try:
            command = f"sudo mount --bind {source_directory} {target_directory}"
            self.debug_logger.log(f"执行绑定临时目录命令：{command}")
            subprocess.run(command, shell=True, check=True)
            self.debug_logger.log(f"已成功将 {source_directory} 绑定到 {target_directory}")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"绑定临时目录失败：{e}")
            return False
        
    def unbind_temporary_directory(self, target_directory):
        try:
            command = f"sudo umount {target_directory}"
            self.debug_logger.log(f"执行解绑临时目录命令：{command}")
            subprocess.run(command, shell=True, check=True)
            self.debug_logger.log(f"已成功解绑 {target_directory}")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"解绑临时目录失败：{e}")
            return False

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
    def __init__(self):
        pass

    def create_directory(self, path, dir_name):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar()
        try:
            full_path = os.path.join(path, dir_name)
            sudo_command = f"sudo mkdir -p {full_path}"
            subprocess.run(sudo_command, shell=True, check=True)
            if os.path.exists(full_path):
                return True
            else:
                return False
        except subprocess.CalledProcessError as e:
            print(f"创建目录失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条

    def delete_path(self, path):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar()
        try:
            if os.path.exists(path):
                sudo_command = f"sudo rm -rf {path}/*"
                subprocess.run(sudo_command, shell=True, check=True)
                if not os.path.exists(path):
                    return True
                else:
                    return False
            else:
                return False
        except subprocess.CalledProcessError as e:
            print(f"删除路径失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
        
# 解压类
class TarExtractor:
    def __init__(self, debug_enabled=False):
        self.debug_logger = DebugLogger("TarExtractor", debug_enabled)

    def extract_tar_gz(self, tar_gz_file, target_path):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar()
        try:
            self.debug_logger.log(f"开始解压 {tar_gz_file} 到 {target_path}")

            # 执行解压命令
            command = f"sudo tar -xzpvf {tar_gz_file} -C {target_path} --numeric-owner"
            self.debug_logger.log(f"执行解压命令：{command}")
            subprocess.run(command, shell=True, check=True)

            self.debug_logger.log(f"成功解压 {tar_gz_file} 到 {target_path}")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"解压失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
        
# 安装类
class InstallationManager:
    def __init__(self, debug_enabled=False):
        self.debug_logger = DebugLogger("InstallationManager", debug_enabled)

    def enter_chroot_environment(self, target_mount_point):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar()
        try:
            command = f"sudo chroot {target_mount_point}"
            self.debug_logger.log(f"进入chroot环境，执行命令：{command}")
            subprocess.run(command, shell=True, check=True)

            # 修改 


            self.debug_logger.log("成功进入chroot环境")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"进入chroot环境失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条

    def exit_chroot_environment(self):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar()
        try:
            self.debug_logger.log("退出chroot环境")
            subprocess.run("exit", shell=True, check=True)
            self.debug_logger.log("成功退出chroot环境")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"退出chroot环境失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条

    def install_packages(self):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar()
        try:
            command = "sudo apt install grub2-common grub-pc-bin"
            self.debug_logger.log(f"在chroot环境内安装软件包，执行命令：{command}")
            subprocess.run(command, shell=True, check=True)
            self.debug_logger.log("软件包安装成功")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"软件包安装失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条

    def install_grub_to_disk(self, disk_path):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar()
        try:
            command = f"sudo grub-install --recheck --no-floppy {disk_path}"
            self.debug_logger.log(f"在chroot环境内安装grub到硬盘，执行命令：{command}")
            subprocess.run(command, shell=True, check=True)
            self.debug_logger.log("grub安装成功")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"grub安装失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条