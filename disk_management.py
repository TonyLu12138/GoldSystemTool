#! /usr/bin/env python3
import os

class TargetDiskAnalyzer:
    def __init__(self, target_disk):
        self.target_disk = target_disk

    def get_partition_structure(self):
        try:
            # 使用Linux的'lsblk'命令来获取目标盘分区结构
            command = f'lsblk -o NAME,MOUNTPOINT {self.target_disk}'
            partition_structure = os.popen(command).read()
            return partition_structure
        except Exception as e:
            print(f"获取目标盘分区结构时发生错误：{e}")
            return None

    def get_root_partition(self):
        try:
            # 获取目标盘分区结构
            partition_structure = self.get_partition_structure()

            # 解析分区结构，查找根目录所在的分区
            root_partition = None
            for line in partition_structure.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == '/':
                    root_partition = parts[0]
                    break

            return root_partition
        except Exception as e:
            print(f"获取目标盘根目录所在分区时发生错误：{e}")
            return None
