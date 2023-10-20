
#! /usr/bin/env python3

import os
import subprocess

class Base:
    def __init__(self, task_logger, debug_logger):
        self.task_logger = task_logger
        self.debug_logger = debug_logger
        
        
    def check_path(self, path):
        buffer = os.path.exists(path)
        if buffer:
            print(f"{path} 存在")
            self.debug_logger.log(f"检查：{path}是否存在。执行结果：{buffer}")
            return buffer
        else:
            print(f"{path} 不存在")
            self.debug_logger.log(f"检查：{path}是否存在。执行结果：{buffer}")
            return buffer
    
    def com(self, command):
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, shell=True, check=True, text=True).stdout 
            self.task_logger.log("INFO", f"执行命令：{command}")
            self.debug_logger.log(f"执行命令：{command}，执行结果：{result}")
            return result
        except subprocess.CalledProcessError as e:
            self.debug_logger.log(f"命令 {command} 执行失败 {e}")
            return f"命令执行失败: {str(e)}"
    
        