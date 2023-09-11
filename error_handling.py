#! /usr/bin/env python3
import datetime
import os
import sys
import subprocess

class ErrorHandling:
    def __init__(self, error_handling_bool, task_logger, debug_logger):
        # 实例化任务日志记录器
        self.task_logger = task_logger
        self.debug_logger = debug_logger
        self.error_handling_bool = error_handling_bool
        
    def handle_next_step_failure(self, error_message, target_mount_point, source_mount_point):
        """
        处理无法执行下一步操作的问题
        """
        # 记录错误信息到任务日志
        self.task_logger.log("ERROR", error_message)

        try:
            # 将后台命令的完整报错输出到 log 日志中
            completed_process = subprocess.run(["command_that_failed"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout_and_stderr = completed_process.stdout + completed_process.stderr

            # 根据用户设定，决定是否 umount 相关目录
            if self.error_handling_bool:
                # 进行 umount 相关目录的操作
                unmount_target_result = self.mount_manager.unmount_device(target_mount_point)
                unmount_soucer_result = self.mount_manager.unmount_device(source_mount_point)
                # 判断卸载目标盘路径
                if unmount_target_result:
                    self.task_logger.log("INFO", "已尝试 umount 相关目录")
                else:
                    self.task_logger.log("ERROR", "umount 相关目录失败")
                # 判断卸载源盘路径
                if unmount_soucer_result:
                    self.task_logger.log("INFO", "已尝试 umount 相关目录")
                else:
                    self.task_logger.log("ERROR", "umount 相关目录失败")

        except Exception as e:
            error_message = f"处理失败：{e}"
            self.task_logger.log("ERROR", error_message)

        # 结束程序
        self.task_logger.log("INFO", "程序结束")
        sys.exit(1)

    # 为了防止循环调用的定义，就在这里再次写一遍解压方法
    def extract_tar_gz(self, tar_gz_file, target_path):
        try:
            # 执行解压命令
            command = f"sudo tar -xzpvf {tar_gz_file} -C {target_path} --numeric-owner"
            subprocess.run(command, shell=True, check=True)

            self.debug_logger.log(f"成功解压 {tar_gz_file} 到 {target_path}")
            return True
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"解压失败：{e}")
            return False
        finally:
            self.debug_logger.log("")  # 输出一个空白行
        
    def handle_extraction_failure(self, tar_gz_file, target_path):
        """
        处理解压失败的情况
        """
        # 记录错误信息到任务日志
        self.task_logger.log("ERROR", error_message)

        try:
            # 记录解压过程中的错误和异常情况到 log 日志中
            log_filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_unzip.log"
            log_filepath = f"/path/to/log/directory/{log_filename}"
            with open(log_filepath, "w") as log_file:
                success = self.extract_tar_gz(tar_gz_file, target_path)
                if not success:
                    self.task_logger.log("ERROR", "解压失败")

            # 回滚操作：删除解压目录 (=将系统恢复到解压前的状态)
            self.delete_unzip_directory(target_path)

            # 重试
            retry_count = 0
            max_retries = 3  # 根据需要调整重试次数
            while retry_count < max_retries:
                retry_count += 1
                self.task_logger.log("INFO", f"正在尝试第 {retry_count} 次重试")
                success = self.extract_tar_gz(tar_gz_file, target_path)
                if success:
                    self.task_logger.log("INFO", "解压成功")
                    return True
                else:
                    self.task_logger.log("WARNING", "解压失败")

            # 重试多次后仍然失败，作为 ”无法执行下一步的问题“ 处理
            self.handle_next_step_failure("重试多次后解压仍然失败")

        except Exception as e:
            error_message = f"处理失败：{e}"
            self.task_logger.log("ERROR", error_message)

        # 结束程序
        self.task_logger.log("INFO", "程序结束")
        sys.exit(1)

    def handle_grub_installation_failure(self, error_message, target_mount_point, source_mount_point):
        """
        处理grub2软件包安装失败的情况
        """
        print("grub2相关软件包安装失败")
        # 退出当前 chroot 环境
        self.installation_manager.exit_chroot_environment()

        # 调用 "无法执行下一步的问题" 的处理方法
        self.handle_next_step_failure(error_message, target_mount_point, source_mount_point)

    def handle_umount_failure(self, mount_point):
        """
        处理卸载挂载点失败的情况
        """
        self.debug_logger.log(f"无法卸载挂载点：{mount_point}")
        
        # 检查当前路径是否在要卸载的路径内
        current_path = os.getcwd()
        if current_path.startswith(mount_point):
            self.debug_logger.log("当前路径在 umount 路径内，无法执行 umount")
            return False

        try:
            # 执行 sync 操作，确保文件系统同步
            subprocess.run("sync", shell=True, check=True)

            # 执行 umount -l，强制卸载
            subprocess.run(f"sudo umount -l {mount_point}", shell=True, check=True)
            self.debug_logger.log(f"已成功强制卸载 {mount_point}")

            # 执行 df -h 检查是否卸载成功
            df_output = subprocess.run("df -h", shell=True, capture_output=True, text=True)
            if mount_point not in df_output.stdout:
                self.debug_logger.log(f"卸载后挂载点 {mount_point} 不再存在")
            else:
                self.debug_logger.log(f"卸载后挂载点 {mount_point} 仍然存在")
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"卸载失败：{e}")

    def check_execution_result(self, success_condition):
        """
        检查执行的任务结果是否符合预期
        """
        if not success_condition:
            print("任务执行结果不符合预期")
            sys.exit(1)
        else:
            print("任务执行成功")