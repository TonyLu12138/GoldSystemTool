#! /usr/bin/env python3
# system_config.py

import os
import subprocess
from log_record import DebugLogger

class SystemConfigModifier:
    def __init__(self, target_mount_point, logical_volume, debug_enabled=False):
        self.logical_volume = logical_volume
        self.target_mount_point = target_mount_point
        self.debug_logger = DebugLogger("SystemConfigModifier", debug_enabled)

    # 返回UUID方法就是获取目标盘设备文件系统 UUID   blkid /dev/ubuntu-vg1/ubuntu-lv1
    def get_root_partition_uuid(self):
        """
        获取目标盘根目录分区的文件系统UUID
        """
        try:
            self.debug_logger.log("开始执行获取UUID方法")
            command = f"blkid {self.logical_volume}"   # 修改，用全局变量
            self.debug_logger.log(f"执行指令 {command}")
            output = subprocess.check_output(command, shell=True, text=True).strip()
            for line in output.splitlines():
                if "UUID=" in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith("UUID="):
                            UUID = part.split("=")[1].strip('"')
                            self.debug_logger.log(f"获取UUID {UUID}")
                            return UUID
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"获取UUID失败：{e}")
            return None

    # 
    def modify_fstab_file(self,UUID):
        """
        修改/etc/fstab文件
        """
        fstab_path = f"{self.target_mount_point}/etc/fstab"

        # 修改权限
        subprocess.run(["sudo", "chmod", "666", fstab_path], check=True)

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
                            break  # 替换完后退出循环
                    modified_lines.append(" ".join(parts) + "\n")
                else:
                    modified_lines.append(line)

        # 将修改后的内容写回fstab文件
            with open(fstab_path, 'w') as f:
                f.writelines(modified_lines)
            print("成功修改/etc/fstab文件")
            return True
        except Exception as e:
            print(f"修改/etc/fstab文件失败：{e}")
            return False
        finally:
            # 恢复文档权限
            subprocess.run(["sudo", "chmod", "644", fstab_path], check=True)

    def modify_resolv_conf_file(self):   # 修改：先删除文件，在创建一个新的
        """
        修改/etc/resolv.conf文件
        """
        resolv_conf_path = f"{self.target_mount_point}/etc/resolv.conf"

        # 删除原有的 resolv.conf 文件
        subprocess.run(["sudo", "rm", resolv_conf_path], check=True)
        
        # 使用sudo命令创建resolv.conf文件
        subprocess.run(["sudo", "touch", resolv_conf_path], check=True)

        # 修改权限为666
        subprocess.run(["sudo", "chmod", "666", resolv_conf_path], check=True)

        # 新的 DNS 服务器地址列表
        new_dns_servers = ["nameserver 8.8.8.8", "nameserver 114.114.114.114"]

        # 写入新的 DNS 服务器地址
        with open(resolv_conf_path, 'w') as f:
            f.writelines('\n'.join(new_dns_servers) + '\n')

        # 恢复文档权限为644
        subprocess.run(["sudo", "chmod", "644", resolv_conf_path], check=True)