#! /usr/bin/env python3
# system_config.py

import os
import subprocess
from base import Base
from process import ProgressBar

class SystemConfigModifier:
    def __init__(self, target_mount_point, logical_volume, task_logger, debug_logger):
        self.logical_volume = logical_volume
        self.target_mount_point = target_mount_point
        self.task_logger = task_logger
        self.debug_logger = debug_logger
        self.base = Base(task_logger, debug_logger)

    # 返回UUID方法就是获取目标盘设备文件系统 UUID   blkid /dev/ubuntu-vg1/ubuntu-lv1
    def get_root_partition_uuid(self):
        """
        获取目标盘根目录分区的文件系统UUID
        """
        print("开始执行获取UUID方法")
        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(1)
        
        try:
            self.task_logger.log("INFO", f"执行获取UUID方法")
            self.debug_logger.log("开始执行获取UUID方法")
            command = f"sudo blkid {self.logical_volume}"   # 修改，用全局变量
            result = self.base.com(command)
            output_lines = result.strip().splitlines()
            for line in output_lines:
                if "UUID=" in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith("UUID="):
                            UUID = part.split("=")[1].strip('"')
                            self.task_logger.log("INFO", f"获取UUID {UUID}")
                            self.debug_logger.log(f"获取UUID {UUID}")
                            progress_bar.update()
                            return UUID
        except subprocess.CalledProcessError as e:
            self.task_logger.log("ERROR", f"获取UUID失败：{e}")
            self.debug_logger.log(f"获取UUID失败：{e}")
            return None
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行

    # 修改/etc/fstab文件
    def modify_fstab_file(self,UUID):
        """
        修改/etc/fstab文件
        """
        self.task_logger.log("INFO", f"执行执行修改/etc/fstab文件方法")
        self.debug_logger.log("开始执行修改/etc/fstab文件方法")
        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(1)

        fstab_path = f"{self.target_mount_point}/etc/fstab"
        self.task_logger.log("INFO", f"fstab文件路径: {self.target_mount_point}/etc/fstab")
        # 修改权限
        command = (f"sudo chmod 666 {fstab_path}")
        self.base.com(command)
        self.debug_logger.log("修改/etc/fstab文件权限")
        try:
            with open(fstab_path, 'r') as f:
                lines = f.readlines()

            modified_lines = []
            for line in lines:
                if "/dev/disk/by-uuid" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.startswith("/dev/disk/by-uuid"):
                            uuid = part.split("/")[-1]
                            parts[i] = part.replace(uuid, UUID)
                            progress_bar.update()
                            self.debug_logger.log("替换对位的UUID")
                            break  # 替换完后退出循环
                    modified_lines.append(" ".join(parts) + "\n")
                else:
                    modified_lines.append(line)

        # 将修改后的内容写回fstab文件
            with open(fstab_path, 'w') as f:
                f.writelines(modified_lines)
            print("成功修改/etc/fstab文件")
            self.debug_logger.log("成功修改/etc/fstab文件")
            return True
        except Exception as e:
            print(f"修改/etc/fstab文件失败：{e}")
            self.task_logger.log("ERROR", f"修改/etc/fstab文件失败：{e}")
            self.debug_logger.log(f"修改/etc/fstab文件失败：{e}")
            return False
        finally:
            # 恢复文档权限
            command = (f"sudo chmod 644 {fstab_path}")
            self.base.com(command)
            self.debug_logger.log("")  # 输出一个空白行

    def modify_resolv_conf_file(self):   # 修改：先删除文件，在创建一个新的
        """
        修改/etc/resolv.conf文件
        """
        self.task_logger.log("INFO", f"执行执行修改/etc/resolv.conf文件方法")
        self.debug_logger.log("开始执行修改/etc/resolv.conf文件方法")
        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(6)

        resolv_conf_path = f"{self.target_mount_point}/etc/resolv.conf"

        # 删除原有的 resolv.conf 文件
        command = (f"sudo rm {resolv_conf_path}")
        self.base.com(command)
        progress_bar.update()
        self.debug_logger.log(f"删除原有的 resolv.conf 文件，执行指令sudo rm {resolv_conf_path}")

        # 使用sudo命令创建resolv.conf文件
        command = (f"sudo touch {resolv_conf_path}")
        self.base.com(command)
        progress_bar.update()
        self.debug_logger.log(f"创建resolv.conf文件，执行指令sudo touch {resolv_conf_path}")

        # 修改权限为666
        command = (f"sudo chmod 666 {resolv_conf_path}")
        self.base.com(command)
        progress_bar.update()
        self.debug_logger.log(f"修改权限为666，执行指令sudo chmod 666 {resolv_conf_path}")

        # 新的 DNS 服务器地址列表
        new_dns_servers = ["nameserver 8.8.8.8", "nameserver 114.114.114.114"]
        progress_bar.update()
        self.task_logger.log("INFO",f"DNS服务器地址 {new_dns_servers}")
        self.debug_logger.log(f"修改DNS服务器地址 {new_dns_servers}")

        # 写入新的 DNS 服务器地址
        with open(resolv_conf_path, 'w') as f:
            f.writelines('\n'.join(new_dns_servers) + '\n')
        progress_bar.update()
        self.debug_logger.log("写入新的 DNS 服务器地址")

        # 恢复文档权限为644
        command = (f"sudo chmod 644 {resolv_conf_path}")
        self.base.com(command)
        print("成功修改/etc/resolv_conf")
        self.debug_logger.log(f"恢复文档权限, 执行指令sudo chmod 644 {resolv_conf_path}")
        progress_bar.update()
        progress_bar.close()  # 关闭进度条
        self.debug_logger.log("")  # 输出一个空白行