#! /usr/bin/env python3
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
        try:
            # 读取 Paths 部分
            if self.config.has_section('Paths'):
                self.paths = {
                    'source_path': self.config.get('Paths', 'source_path'),
                    'target_path': self.config.get('Paths', 'target_path')
                }
            else:
                print("未找到[Paths]章节，配置文件格式有误")
                return False
            
            # 读取 Backup 部分
            if self.config.has_section('Backup'):
                self.backup_info = {
                    'backup_name': self.config.get('Backup', 'backup_name')
                }
            else:
                print("未找到[Backup]章节，配置文件格式有误")
                return False

            # 检查是否存在[ErrorHandling]部分
            if self.config.has_section('ErrorHandling'):
                umount_on_error = self.config.get('ErrorHandling', 'umount_on_error')
                if umount_on_error.lower() == 'true':
                    self.error_handling = {
                        'umount_on_error': True
                    }
                elif umount_on_error.lower() == 'false':
                    self.error_handling = {
                        'umount_on_error': False
                    }
                else:
                    print("ErrorHandling配置中的umount_on_error不是布尔值")
                    return False
            else:
                print("未找到[ErrorHandling]章节，将默认ErrorHandling配置为False")
                self.error_handling = {
                    'umount_on_error' : False
                }
            # 检查是否存在[Debug]部分
            if self.config.has_section('Debug'):
                debug_button = self.config.get('Debug', 'debug_button')
                if debug_button.lower() == 'true':
                    self.debug_info = {
                        'debug_button': True
                    }
                elif debug_button.lower() == 'false':
                    self.debug_info = {
                        'debug_button': False
                    }
                else:
                    print("debug配置中的debug_button不是布尔值")
                    return False
        except configparser.NoSectionError as invalid_section_error:
            print(f"填写错误的章节名，请重新填写: {invalid_section_error}")
            return False
            
    #验证备份包名称有效性
    def validate_backup_name(self):
        if 'backup_name' not in self.backup_info:
            print("验证备份包名称有效性方法中，未找到备份包名称，请检查配置文件")
            return False
    
        source_path = self.paths.get('source_path')

        # 检查是否包含设备标识，例如 sda、sdb、sdc 等
        if any(device in source_path for device in ['sda', 'sdb', 'sdc']):
            source_path = source_path.replace('/dev/', '/mnt/')

        specified_backup_name = 'backup.tar.gz'  # 备份包名称
        
        # 遍历整个目录，查找备份包
        for root, dirs, files in os.walk(source_path):
            if specified_backup_name in files:
                return True
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
                print(f"源路径 '{source_path_value}' 不存在，请检查配置项'source_path'中的路径")
        else:
            print("未找到配置项 'source_path' 中的路径")

        # 验证目标路径
        if target_path_value:
            if os.path.exists(target_path_value):
                print(f"目标路径 '{target_path_value}' 存在，验证通过")
            else:
                print(f"目标路径 '{target_path_value}' 不存在，请检查配置项'target_path'中的路径")
        else:
            print("未找到配置项 'target_path' 中的路径")

    # 验证debug按钮
    def check_debug_switch(self):
        config = configparser.ConfigParser()
        config.read('input.ini')
        if config.has_section('Debug'):
            # 将 [debug] 章节中的配置信息存储到self.debug_info中
            self.debug_info['debug_button'] = config.getboolean('Debug', 'debug_button')
            print("[debug] 章节中的debug_button配置项已存储到self.debug_info中")

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
        
