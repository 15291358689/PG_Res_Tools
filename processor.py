import os
import json
import shutil
import time
from tkinter import messagebox
from config import TYPE_CATEGORIES
from utils import *
from handlers import get_handler_for_type

class Processor:
    def __init__(self,source, output, update_progress_callback):
        self.source = source
        self.output = output
        self.update_progress_callback = update_progress_callback
        self.log_path = ""
        self.paths = {}
        self.types = []
        self.uuids = []
        self.packs = {}
        self.versions = {}
        self.logInfo = ""
        self.importData = [] 

    def process_resources(self):
        if not self.source : 
            messagebox.showerror("错误", "资源文件夹目录为空")
            return
        os.makedirs(self.output, exist_ok=True)
        self.log_path = os.path.join(self.output, "资源整理日志.txt")


        self.logInfo = f"Cocos资源整理日志\n源文件夹: {self.source}\n输出文件夹: {self.output}\n开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n" + "=" * 50 + "\n\n"

        config_files = find_config_json(self.source)

        print("已找到配置文件：",config_files)

        if not config_files:
            messagebox.showerror("错误", "未找到任何配置文件")
            return

        total_resources = 0
        success_count = 0
        error_count = 0

        for config_path in config_files:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)

                self.paths = config.get("paths", {})
                self.types = config.get("types", [])
                self.uuids = config.get("uuids", [])
                self.packs = config.get("packs", {})
                self.versions = config.get("versions", {})
                self.importData = self.versions.get("import", {})

                self.logInfo += (f"》》》》》》》》》》》》开始处理: {config_path} : \n")

                for i in range(0, len(self.importData), 2):
                    try:
                        key = self.importData[i]
                        value = self.importData[i + 1]
                        back = False
                        msg = "类型出错 未处理"

                        if type(key) == int:
                            pathInfo = self.paths.get(str(key))
                            if pathInfo is None:
                                continue
                            else:
                                res_type = self.types[pathInfo[1]]
                                handler = get_handler_for_type(res_type)
                                if handler is None:
                                    continue
                                back,msg = handler(self,[key,value], int(key), f'{self.output}/{pathInfo[0]}')
                        else:
                            packField = find_field_json(self.source,value)
                            if packField is None:
                                continue
                            handler = get_handler_for_type("pack")
                            back,msg = handler(self,[key,value], 0, f'{self.output}')

                        if(back) : 
                            success_count += 1 
                            self.logInfo += (f"\n   成功处理: {key} : {value}\n")
                        else: 
                            error_count += 1
                            self.logInfo += (f"\n   ***处理失败***: {key} : {value}\n     {msg}\n")
                            
                        total_resources += 1
                    except Exception as e:
                        error_count += 1
                        self.logInfo += (f"\n   》》异常-----: {e} \n{key} : {value}\n     {msg}\n")

                    self.update_progress_callback(i, len(self.paths), success_count, error_count)
            except Exception as e:
                self.logInfo += (f"配置文件 {config_path} 处理失败: {str(e)}\n")
                    
        with open(self.log_path, "w", encoding="utf-8") as log_file:
            log_file.write(self.logInfo)

        messagebox.showinfo("完成", f"成功: {success_count}, 失败: {error_count}, 总数: {total_resources}")

        # 点击"确定"后打开文件夹
        os.startfile(self.output)  # 仅限Windows
        