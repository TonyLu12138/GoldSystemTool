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
            progress_bar = ProgressBar(1)
            command = f"sudo mount {target_path} {mount_point}"
            result = self.base.com(command).strip()
            if "失败" not in str(result):
                buffer = True
                progress_bar.update()
                self.debug_logger.log("挂载目标盘完成")
                print(f"挂载目标盘完成")
            else:
                for i in range(4):
                    result = self.base.com(command).strip()
                    if "失败" not in str(result):
                        buffer = True
                        progress_bar.update()
                        print(f"第{i+1}次尝试，挂载目标盘完成")
                        break
                    print(f"第{i+1}次尝试，挂载目标盘失败")
            if buffer is False:
                self.error_handling.check_execution_result(False)
            self.debug_logger.log("")
            progress_bar.close()  # 关闭进度条
            return buffer
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
            if "失败" not in str(result):
                buffer = True
                progress_bar.update()
                self.debug_logger.log("挂载源盘完成")
                print(f"挂载源盘完成")
            else:
                for i in range(4):
                    result = self.base.com(command).strip()
                    if "失败" not in str(result):
                        buffer = True
                        progress_bar.update()
                        print(f"第{i+1}次尝试，挂载源盘完成")
                        break
                    print(f"第{i+1}次尝试，挂载源盘失败")
            if buffer is False:
                self.error_handling.check_execution_result(False) # 修改
            self.debug_logger.log("")
            progress_bar.close()  # 关闭进度条
            return buffer
        else:
            self.task_logger.log("ERROR", f"未找到配置项 'source_path' 中的路径")
            self.debug_logger.log("未找到配置项 'source_path' 中的路径")
            self.debug_logger.log("")
            progress_bar.close()  # 关闭进度条
            return False

    def unmount_device(self, mount_point):
        print(f"执行挂载{mount_point}方法")
        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"执行卸载{mount_point}方法")
            self.debug_logger.log(f"执行卸载{mount_point}方法")
            command = f"sudo umount {mount_point}"
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
    def delete_path_file(self, path):
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
                self.task_logger.log("ERROR", f"无法清空目标盘挂载路径")
                self.debug_logger.log(f"无法清空目标盘挂载路径")
                return False
        except subprocess.CalledProcessError as e:
            print(f"删除路径失败：{e}")
            self.debug_logger.log(f"删除路径失败：{e}")
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
                sudo_command = f"sudo rm -rf {path}"
                self.base.com(sudo_command).strip()
                print(f"临时路径{path}已删除")
                if not self.base.check_path(path):
                    progress_bar.update()
                    return True
                else:
                    self.task_logger.log("WARNING", f"删除 {path} 失败")
                    return False
            else:
                print(f"无法删除路径{path}")
                self.task_logger.log("ERROR", f"删除路径{path}失败，路径不存在")
                self.debug_logger.log(f"删除路径{path}失败，路径不存在")
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

    def enter_chroot(self, target_mount_point):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"检查是否进入chroot环境")
            self.debug_logger.log(f"检查是否进入chroot环境")
            
            # 检查是否进入chroot环境
            chroot_command = f"sudo chroot {target_mount_point} /bin/bash -c 'pwd; exit'"
            for i in range(4):
                current_dir_result = self.base.com(chroot_command).strip()
                if current_dir_result == "/":
                    break
                elif i == 3:
                    print(f"第{i+1}次尝试，无法进入chroot环境: {current_dir_result}")
                    return False  # 返回错误
                else:
                    print(f"第{i+1}次尝试，无法进入chroot环境, 重新尝试进入") 
                progress_bar.update()
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"进入chroot环境失败：{e}")
            self.task_logger.log("ERROR", f"进入chroot环境失败：{e}")
            self.debug_logger.log(f"进入chroot环境失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行
    
    def install_packages(self, target_mount_point):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"安装软件包：")
            self.debug_logger.log(f"安装软件包：")

            # 安装软件包
            apt_install_command = "apt install -y grub2-common grub-pc-bin"
            chroot_command = f"sudo chroot {target_mount_point} /bin/bash -c '{apt_install_command}; echo -e \'\\n\\n\'; exit'"
            apt_install_result = self.base.com(chroot_command)

            if ("Setting up grub2-common" in apt_install_result and "Setting up grub-pc-bin" in apt_install_result) or "grub2-common is already" in apt_install_result:
                print("已成功安装软件包")
                self.debug_logger.log(f"已成功安装软件包")
                progress_bar.update()
                return True
            else:
                print("安装软件包失败")
                self.debug_logger.log(f"安装软件包失败: {apt_install_result}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"软件包安装失败：{e}")
            self.task_logger.log("ERROR", f"软件包安装失败：{e}")
            self.debug_logger.log(f"软件包安装失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行

    def install_grub(self, target_mount_point, disk_path):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"安装grub")
            self.debug_logger.log(f"安装grub")
            7
            # 安装grub
            grub_install_command = f"grub-install --recheck --no-floppy {disk_path}"
            chroot_command = f"sudo chroot {target_mount_point} /bin/bash -c '{grub_install_command} 2>&1; echo -e \'\\n\\n\'; exit'"
            grub_install_result = self.base.com(chroot_command)
            if ("Installing for" in grub_install_result) or "No error reported" in grub_install_result:
                print("已成功安装grub")
                self.debug_logger.log(f"已成功安装grub")
                progress_bar.update()
                return True
            else:
                print("安装grub失败")
                self.debug_logger.log(f"安装grub失败: {grub_install_result}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"grub安装失败：{e}")
            self.task_logger.log("ERROR", f"grub安装失败：{e}")
            self.debug_logger.log(f"grub安装失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行

    def exit_chroot(self, target_mount_point):
        # 使用ProgressBar显示创建目录进度
        progress_bar = ProgressBar(1)
        try:
            self.task_logger.log("INFO", f"退出chroot环境")
            self.debug_logger.log(f"退出chroot环境")

            # 退出chroot环境
            exit_command = "exit"
            chroot_command = f"sudo chroot {target_mount_point} /bin/bash -c '{exit_command}'"
            self.base.com(chroot_command)

            progress_bar.update()

            return True
        except subprocess.CalledProcessError as e:
            print(f"执行退出chroot的exit指令失败：{e}")
            return False
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行
