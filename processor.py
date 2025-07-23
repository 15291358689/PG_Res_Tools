import os
import json
import shutil
import time
from tkinter import messagebox
from config import TYPE_CATEGORIES
from utils import find_config_json
from handlers import get_handler_for_type

class Processor:
    def __init__(self,source, output, selected_types, update_progress_callback):
        self.source = source
        self.output = output
        self.selected_types = selected_types
        self.update_progress_callback = update_progress_callback
        self.log_path = ""
        self.paths = {}
        self.types = []
        self.uuids = []
        self.packs = {}
        self.versions = {}
        self.logInfo = ""

    def process_resources(self):
        if not self.source : 
            messagebox.showerror("错误", "资源文件夹目录为空")
            return
        os.makedirs(self.output, exist_ok=True)
        self.log_path = os.path.join(self.output, "资源整理日志.txt")


        self.logInfo = f"Cocos资源整理日志\n源文件夹: {self.source}\n输出文件夹: {self.output}\n处理的资源类型: {', '.join(self.selected_types)}\n开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n" + "=" * 50 + "\n\n"

        config_files = find_config_json(self.source,self.selected_types)

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

                self.logInfo += (f"》》》》》》》》》》》》开始处理: {config_path} : \n")

                for idx, (res_id, res_info) in enumerate(self.paths.items(), 1):
                    try:
                        save_path = f'{self.output}/{res_info[0]}'
                        type_idx = res_info[1]
                        # uuid = self.uuids[int(res_id)]
                        res_type = self.types[type_idx]

                        if res_type not in self.selected_types:
                            continue

                        self.logInfo += f"\n>>>>开始处理：{res_id}"

                        handler = get_handler_for_type(res_type)
                        back,msg = handler(self,config, int(res_id), save_path)

                        if(back) : 
                            success_count += 1 
                            self.logInfo += (f"\n   成功处理: {res_info[0]} : {res_id}\n")
                        else: 
                            error_count += 1
                            self.logInfo += (f"\n   ***处理失败***: {res_info[0]} : {res_id}\n     {msg}\n")
                            

                        total_resources += 1
                    except Exception:
                        error_count += 1

                    self.update_progress_callback(idx, len(self.paths), success_count, error_count)
            except Exception as e:
                self.logInfo += (f"配置文件 {config_path} 处理失败: {str(e)}\n")
                    
        with open(self.log_path, "w", encoding="utf-8") as log_file:
            log_file.write(self.logInfo)

        messagebox.showinfo("完成", f"成功: {success_count}, 失败: {error_count}, 总数: {total_resources}")

        # 点击"确定"后打开文件夹
        os.startfile(self.output)  # 仅限Windows
        