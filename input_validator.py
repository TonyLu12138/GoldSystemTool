#! /usr/bin/env python3
import configparser
import os
from base import Base
from log_record import TaskLogger, DebugLogger
from process import ProgressBar  # 导入TaskLogger类

class InputValidator:
    def __init__(self, config_file='input.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        self.paths = {} #路径   
        self.backup_info = {} #备份包名称 
        self.error_handling = {} #错误处理配置
        self.debug_info = {"debug_button" : False} #debug开关

        self.task_logger = TaskLogger("InputValidator")  # 创建任务日志记录器
        self.debug_logger = DebugLogger("InputValidator")
     
    #读取input.ini配置文件信息
    def read_config(self):
        try:
            # 读取 Paths 部分
            if self.config.has_section('Paths'):
                self.paths = {
                    'source_path': self.config.get('Paths', 'source_path'),
                    'target_path': self.config.get('Paths', 'target_path')
                }
                print(f"读取paths部分：{self.paths}")
                self.task_logger.log("INFO", f"获取路径信息: {self.paths}")
            else:
                print("未找到[Paths]章节，配置文件格式有误")
                self.task_logger.log("ERROR",f"未找到[Paths]章节，配置文件格式有误")
                return False
            
            # 读取 Backup 部分
            if self.config.has_section('Backup'):
                self.backup_info = {
                    'backup_name': self.config.get('Backup', 'backup_name')
                }
                self.task_logger.log("INFO", f"获取备份包信息: {self.backup_info}")
            else:
                print("未找到[Backup]章节，配置文件格式有误")
                self.task_logger.log("ERROR",f"未找到[Backup]章节，配置文件格式有误")
                return False

            # 检查是否存在[ErrorHandling]部分
            if self.config.has_section('ErrorHandling'):
                umount_on_error = self.config.get('ErrorHandling', 'umount_on_error')
                if umount_on_error.lower() == 'true':
                    self.error_handling = {
                        'umount_on_error': True
                    }
                    self.task_logger.log("INFO", f"获取ErrorHandling信息: {self.error_handling}")
                elif umount_on_error.lower() == 'false':
                    self.error_handling = {
                        'umount_on_error': False
                    }
                    self.task_logger.log("INFO", f"获取ErrorHandling信息: {self.error_handling}")
                else:
                    print("ErrorHandling配置中的umount_on_error不是布尔值")
                    #进错误处理部分
                    return False
            else:
                print("未找到[ErrorHandling]章节，将默认ErrorHandling配置为False")
                self.error_handling = {
                    'umount_on_error' : False
                }
                self.task_logger.log("ERROR",f"未找到[ErrorHandling]章节，配置文件格式有误，将默认ErrorHandling配置为False {self.error_handling}")
            # 检查是否存在[Debug]部分
            if self.config.has_section('Debug'):
                debug_button = self.config.get('Debug', 'debug_button')
                if debug_button.lower() == 'true':
                    self.debug_info = {
                        'debug_button': True
                    }
                    self.debug_logger.set_debug(self.debug_info['debug_button'])
                    self.debug_logger.setup_file_handler()
                elif debug_button.lower() == 'false':
                    self.debug_info = {
                        'debug_button': False
                    }
                else:
                    print("debug配置中的debug_button不是布尔值")
                    return False
                
        except configparser.NoSectionError as invalid_section_error:
            self.task_logger.log("ERROR",f"获取章节名错误: {invalid_section_error}")
            print(f"填写错误的章节名，请重新填写: {invalid_section_error}")
            return False
            
    #验证备份包名称有效性
    def validate_backup_name(self, source_mount_point):
        self.task_logger.log("INFO",f"执行验证备份包名称有效性方法")
        self.debug_logger.log(f"执行验证备份包名称有效性方法") #debug
        if 'backup_name' not in self.backup_info:
            self.debug_logger.log(f"未找到{self.backup_info}备份包") #debug
            print("验证备份包名称有效性方法中，未找到备份包名称，请检查配置文件")
            
            return False
    
        source_path = source_mount_point
        
        specified_backup_name = self.backup_info.get('backup_name')  # 备份包名称
        self.debug_logger.log(f"获取备份包名称 {specified_backup_name}") #debug

        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(1)

        # 遍历整个目录，查找备份包
        for root, dirs, files in os.walk(source_path):

            if specified_backup_name in files:
                self.debug_logger.log(f"查找备份包成功") #debug
                progress_bar.update()  # 更新进度条
                progress_bar.close()  # 关闭进度条
                return True
            self.debug_logger.log(f"查找备份包失败") #debug
            
        progress_bar.close()  # 关闭进度条
        self.debug_logger.log("")  # 输出一个空白行
        return False

    #验证设备路径的有效性
    def validate_device_path(self):
        base = Base(self.get_log_object(), self.get_debug_object())
        self.task_logger.log("INFO",f"执行验证设备路径的有效性方法")
        self.debug_logger.log(f"执行验证设备路径的有效性方法") #debug
        # 获取字典里的信息
        source_path_value = self.paths.get('source_path')
        target_path_value = self.paths.get('target_path')
        self.debug_logger.log(f"获取字典信息 source_path_value: {source_path_value}，target_path_value: {target_path_value}") #debug
        
        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(2)

        source = False
        target = False
        
        # 验证源路径
        if source_path_value:
            if base.check_path(source_path_value):
                self.debug_logger.log(f"源路径 '{source_path_value}' 存在，验证通过") #debug
                self.task_logger.log("INFO", f"源路径 '{source_path_value}' 存在，验证通过")
                print(f"源路径 '{source_path_value}' 存在，验证通过")
                progress_bar.update()
                source = True
            else:
                self.task_logger.log("ERROR",f"源路径 '{source_path_value}' 不存在")
                self.debug_logger.log(f"源路径 '{source_path_value}' 不存在，验证失败") #debug
                print(f"源路径 '{source_path_value}' 不存在，请检查配置项'source_path'中的路径")
        else:
            self.debug_logger.log(f"未找到配置项 'source_path' 中的路径") #debug
            print("未找到配置项 'source_path' 中的路径")

        # 验证目标路径
        if target_path_value:
            if base.check_path(target_path_value):
                self.debug_logger.log(f"目标路径 '{target_path_value}' 存在，验证通过")
                self.task_logger.log("INFO", f"目标路径 '{target_path_value}' 存在，验证通过")
                print(f"目标路径 '{target_path_value}' 存在，验证通过")
                progress_bar.update()
                target = True
            else:
                self.task_logger.log("ERROR",f"目标路径 '{target_path_value}' 不存在")
                self.debug_logger.log(f"目标路径 '{target_path_value}' 不存在，请检查配置项'target_path'中的路径")
                print(f"目标路径 '{target_path_value}' 不存在，请检查配置项'target_path'中的路径")
        else:
            self.debug_logger.log(f"未找到配置项 'target_path' 中的路径")
            print("未找到配置项 'target_path' 中的路径")

        progress_bar.close()  # 关闭进度条
        self.debug_logger.log("")  # 输出一个空白行

        if target and source:
            return True
        else:
            return False

    # 验证debug按钮
    def check_debug_switch(self):

        self.debug_logger.log(f"执行验证debug按钮方法") #debug

        # 使用ProgressBar显示进度条
        progress_bar = ProgressBar(1)

        config = configparser.ConfigParser()
        config.read('input.ini')
        if config.has_section('Debug'):
            # 将 [debug] 章节中的配置信息存储到self.debug_info中
            self.debug_info['debug_button'] = config.getboolean('Debug', 'debug_button')
            self.task_logger.log("INFO", f"获取[debug] 章节中的信息: {self.debug_info['debug_button']}")
            self.debug_logger.log("[debug] 章节中的debug_button配置项已存储到self.debug_info中") #debug
            print("[debug] 章节中的debug_button配置项已存储到self.debug_info中")
            progress_bar.update()
        progress_bar.close()  # 关闭进度条
        self.debug_logger.log("")  # 输出一个空白行

    def check_error_handling_config(self):
        if self.error_handling.get('umount_on_error'):
            return True
        else:
            return False
    
    #以字典形式返回路径信息
    def get_paths(self): 
        return self.paths

    #以字典形式返回备份包信息
    def get_backup_info(self):
        return self.backup_info

    #以字典形式返回错误处理配置信息
    def get_error_handling(self):
        return self.error_handling

    #以字典形式返回debug信息
    def get_debug_info(self):
        return self.debug_info
        
    def get_log_object(self):
        return self.task_logger
    
    def get_debug_object(self):
        return self.debug_logger
