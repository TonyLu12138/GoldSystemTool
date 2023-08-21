import os
import subprocess
import time
from log_record import DebugLogger
from input_validator import InputValidator

# 挂在和卸载类
class MountUnmountManager:
    def __init__(self, input_validator, debug_enabled=False):
        self.input_validator = input_validator
        self.debug_logger = DebugLogger("MountUnmountManager", debug_enabled)
        self.target_mount_point = ""
        self.source_mount_point = ""

    #输入需要的挂载点，就是要先创建对应的目录
    def mount_target_path(self, mount_point, max_retries=4, retry_delay=5):
        target_path = self.input_validator.get_paths().get('target_path')
        if target_path:
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
            self.debug_logger.log("多次挂载失败，进入错误处理")
            return False
        else:
            self.debug_logger.log("未找到配置项 'target_path' 中的路径")
            return False

    def mount_source_path(self, mount_point, max_retries=4, retry_delay=5):
        source_path = self.input_validator.get_paths().get('source_path')
        if source_path:
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
            self.debug_logger.log("多次挂载失败，进入错误处理")
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

    def delete_path(self, path):
        try:
            if os.path.exists(path):
                sudo_command = f"sudo rm -rf {path}"
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
        
# 解压类
class TarExtractor:
    def __init__(self, debug_enabled=False):
        self.debug_logger = DebugLogger("TarExtractor", debug_enabled)

    def extract_tar_gz(self, tar_gz_file, target_path):
        try:
            self.debug_logger.log(f"开始解压 {tar_gz_file} 到 {target_path}")

            # 执行解压命令
            command = f"tar -xzvf {tar_gz_file} -C {target_path}"
            self.debug_logger.log(f"执行解压命令：{command}")
            subprocess.run(command, shell=True, check=True)

            self.debug_logger.log(f"成功解压 {tar_gz_file} 到 {target_path}")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"解压失败：{e}")
            return False