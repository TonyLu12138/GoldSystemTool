#! usr/bin/env python3
import configparser
import os

class InputValidator:
    def __init__(self, config_file='input.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

        self.paths = {} #路径   
        self.backup_info = {} #备份包名称 
        self.error_handling = {} #错误处理配置
        self.debug_info = {"debug_button" : False} #debug开关

    #读取input.ini配置文件信息
    def read_config(self):
        self.paths = {
            'source_path': self.config.get('Paths', 'source_path'),
            'target_path': self.config.get('Paths', 'target_path')
        }
        self.backup_info = {
            'backup_name': self.config.get('Backup', 'backup_name')
        }
        self.error_handling = {
            'umount_on_error': self.config.getboolean('ErrorHandling', 'umount_on_error')
        }
        self.debug_info = {
            'debug_button': self.config.getboolean('debug', 'debug_button')
        }
    #验证备份包名称有效性
    def validate_backup_name(self):
        backup_name = self.backup_info['backup_name']
        specified_backup_name = 'backup.tar.gz'  # 备份包名称
        
        if backup_name == specified_backup_name:
            return True
        else:
            return False

    #验证设备路径的有效性
    def validate_device_path(self):
        # 获取字典里的信息
        source_path_value = self.paths.get('source_path')
        target_path_value = self.paths.get('target_path')

        # 验证源路径
        if source_path_value:
            if os.path.exists(source_path_value):
                print(f"源路径 '{source_path_value}' 存在，验证通过")
            else:
                print(f"源路径 '{source_path_value}' 不存在，请检查配置项 'source_path' 中的路径")
        else:
            print("未找到配置项 'source_path' 中的路径")

        # 验证目标路径
        if target_path_value:
            if os.path.exists(target_path_value):
                print(f"目标路径 '{target_path_value}' 存在，验证通过")
            else:
                print(f"目标路径 '{target_path_value}' 不存在，请检查配置项 'target_path' 中的路径")
        else:
            print("未找到配置项 'target_path' 中的路径")

    # 验证debug按钮
    def check_debug_switch(self):
        config = configparser.ConfigParser()
        config.read('input.ini')
        # 如果debug的section不存在，那就把这个字典直接改成false
        if not config.has_section('debug'):
            self.debug_info = False
        elif config.has_section('debug'):
            # 将 [debug] 章节中的配置信息存储到self.debug_info中
            self.debug_info['debug_button'] = config.getboolean('debug', 'debug_button')
            print("[debug] 章节中的 debug_button 配置项已存储到 self.debug_info 中")

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
        