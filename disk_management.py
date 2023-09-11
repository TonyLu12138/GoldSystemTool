#! /usr/bin/env python3
import os
import re
from base import Base
from process import ProgressBar  

class TargetDiskAnalyzer:
    def __init__(self, target_disk, task_logger, debug_logger):
        self.target_disk = target_disk
        self.base = Base(task_logger, debug_logger)
        self.task_logger = task_logger  # 创建任务日志记录器
        # print(f"这是DiskManagement的debug传入值 {debug}")
        self.debug_logger = debug_logger
        # self.debug_logger.set_debug(debug)

     # 使用Linux的'lsblk'命令来获取目标盘分区结构
    def get_partition_structure(self):
        try:
            # 使用ProgressBar显示进度条
            progress_bar = ProgressBar(1)

            self.debug_logger.log(f"开始执行获取目标盘分区结构方法") #debug
            command = f'lsblk -o NAME,MOUNTPOINT {self.target_disk}'
            partition_structure = self.base.com(command)
            progress_bar.update()
            self.task_logger.log("INFO", f"目标盘分区结构：{partition_structure}")
            if partition_structure is not None:
                print("目标盘分区结构：")
                print(partition_structure)
            else:
                print("无法获取目标盘分区结构")
            return partition_structure
        except Exception as e:
            print(f"获取目标盘分区结构时发生错误：{e}")
            self.task_logger.log("ERROR", f"获取目标盘分区结构时发生错误：{e}")
            self.debug_logger.log(f"获取目标盘分区结构时发生错误：{e}") #debug
            return None
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行

    def get_root_partition(self, partition_structure):

        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(1)

        try:
            # 获取目标盘分区结构
            self.debug_logger.log(f"开始执行获取根目录所在分区方法") #debug
            partition_structure = partition_structure

            # 处理分区结构，提取包含字母和数字的分区名
            partition_names = [re.sub(r'[^\w\d]', '', line) for line in partition_structure.splitlines() if re.search(r'\w+\d+', line)]
            print('partition_names' + str(partition_names))   #删除
            self.task_logger.log("DEBUG", 'partition_names' + str(partition_names))
            self.debug_logger.log(f"提取分区结构信息 {partition_names}。") #debug
            
            # 逐个分区进行判断
            for partition_name in partition_names:
                if partition_name == 'sdd2':
                    print(f"根目录所在分区：{partition_name}")
                    self.task_logger.log("INFO", f"根目录所在分区：{partition_name}")
                    self.debug_logger.log(f"输出根目录所在分区 /dev/{partition_name}。") #debug
                    progress_bar.update()
                    print(f"目标盘根目录所在分区：/dev/{partition_name}")
                    return f"/dev/{partition_name}"
                

            print("未找到sdd2 的根分区")
            self.task_logger.log("WARNING", "未找到sdd2的根分区")
            self.debug_logger.log("未找到sdd2的根分区") #debug
            return None
        except Exception as e:
            print(f"查找根目录分区时发生错误：{e}")
            self.task_logger.log("ERROR", f"查找根目录分区时发生错误：{e}")
            self.debug_logger.log(f"查找根目录分区时发生错误：{e}") #debug
            return None
        finally:
            progress_bar.close()  # 关闭进度条
            self.debug_logger.log("")  # 输出一个空白行

    #尝试把它先挂载到/mnt/sdx上，
    # 然后分析里面的文件是否是根目录所包含文件。
    # 如果不是就卸载掉，
    # 然后挂载下一个分区，直到找到对应的分区
