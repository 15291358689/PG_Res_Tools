import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
import threading
import time
import re

class ToolApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cocos资源整理工具")
        self.root.geometry("680x420")
        self.root.minsize(600, 380)
        
        # 存储路径的变量
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.progress = tk.DoubleVar()
        self.progress_label = tk.StringVar()
        
        # 自动路径跟踪
        self.auto_path = True
        self.source_path.trace_add("write", self.auto_set_output)

        self.create_widgets()

    def auto_set_output(self, *args):
        if self.auto_path:
            source = self.source_path.get()
            if source:
                self.output_path.set(os.path.join(source, "整理结果"))

    def create_widgets(self):
        # 统一控件样式
        style = ttk.Style()
        style.configure("TLabelFrame", padding=10)
        style.configure("TButton", padding=6)

        # 资源文件夹选择框
        source_frame = ttk.LabelFrame(self.root, text="Cocos构建文件夹")
        source_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Entry(source_frame, textvariable=self.source_path).pack(
            side="left", padx=5, pady=5, fill="x", expand=True)
        ttk.Button(source_frame, text="浏览", 
                  command=lambda: self.select_folder(self.source_path, "选择Cocos构建文件夹")).pack(
                      side="right", padx=5)
        
        # 输出文件夹选择框
        output_frame = ttk.LabelFrame(self.root, text="输出文件夹")
        output_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Entry(output_frame, textvariable=self.output_path).pack(
            side="left", padx=5, pady=5, fill="x", expand=True)
        ttk.Button(output_frame, text="浏览", 
                  command=lambda: self.select_folder(self.output_path, "选择输出文件夹")).pack(
                      side="right", padx=5)
        
        # 进度条组件
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(pady=15, fill="x", expand=True)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            orient="horizontal",
            length=600,
            mode="determinate",
            variable=self.progress
        )
        self.progress_bar.pack(pady=5)
        
        ttk.Label(progress_frame, textvariable=self.progress_label).pack()
        
        # 整理按钮
        self.organize_btn = ttk.Button(
            self.root, 
            text="开始整理", 
            command=self.start_processing_thread
        )
        self.organize_btn.pack(pady=20)

    def select_folder(self, path_var, title):
        if path_var == self.output_path:
            self.auto_path = False  # 手动选择时禁用自动更新

        folder = filedialog.askdirectory(title=title)
        if folder:
            path_var.set(folder)
            
    def start_processing_thread(self):
        """启动处理线程"""
        self.organize_btn["state"] = "disabled"
        threading.Thread(target=self.process_resources).start()

    def find_config_json(self, source):
        """在源文件夹中查找所有匹配的配置文件"""
        config_files = []
        config_pattern = re.compile(r'^config\.[a-f0-9]+\.json$', re.IGNORECASE)
        
        for root, _, files in os.walk(source):
            for file in files:
                if config_pattern.match(file):
                    config_files.append(os.path.join(root, file))
        
        return config_files

    def process_resources(self):
        """核心处理逻辑 - 处理所有资源类型"""
        try:
            source = self.source_path.get()
            output = self.output_path.get()

            if not all([source, output]):
                raise ValueError("请先选择文件夹")
                
            # 确保输出目录存在
            os.makedirs(output, exist_ok=True)
            
            # 创建日志文件路径
            log_path = os.path.join(output, "资源整理日志.txt")
            
            # 先初始化日志文件
            with open(log_path, "w", encoding="utf-8") as log_file:
                log_file.write("Cocos资源整理日志\n")
                log_file.write(f"源文件夹: {source}\n")
                log_file.write(f"输出文件夹: {output}\n")
                log_file.write(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_file.write("=" * 50 + "\n\n")
                
            # 查找所有可能的配置文件
            config_files = self.find_config_json(source)
            if not config_files:
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write("❌ 未找到任何配置文件（config.*.json），请确保是Cocos构建目录\n")
                raise FileNotFoundError("未找到任何配置文件（config.*.json），请确保是Cocos构建目录")
            else:
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"找到 {len(config_files)} 个配置文件\n")
            
            # 处理每个配置文件
            processed_configs = 0
            total_resources = 0
            success_count = 0
            error_count = 0
            
            
            for config_path in config_files:
                config_name = os.path.basename(config_path)
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    
                    # 验证配置文件
                    required_fields = ["paths", "types", "uuids"]
                    missing_fields = [field for field in required_fields if field not in config]
                    
                    if missing_fields:
                        error_msg = f"配置文件 {config_name} 缺少必要字段: {', '.join(missing_fields)}"
                        with open(log_path, "a", encoding="utf-8") as log_file:
                            log_file.write(f"❌ {error_msg}\n")
                        error_count += 1
                        continue
                    
                    paths = config.get("paths", {})
                    types = config.get("types", [])
                    uuids = config.get("uuids", [])
                    types = config.get("types",[])
                    
                    if not paths or not types or not uuids:
                        error_msg = f"配置文件 {config_name} 格式不完整"
                        with open(log_path, "a", encoding="utf-8") as log_file:
                            log_file.write(f"❌ {error_msg}\n")
                        error_count += 1
                        continue
                    
                    # 记录开始处理此配置文件
                    with open(log_path, "a", encoding="utf-8") as log_file:
                        log_file.write(f"✅ 开始处理配置文件: {config_name}\n")
                        log_file.write(f"  包含资源: {len(paths)} 个\n")
                    
                    # 创建分类目录
                    type_categories = {
                        0: "atlas",     # cc.SpriteAtlas
                        1: "texture",   # cc.Texture2D
                        2: "audio",     # cc.AudioClip
                        3: "animation", # cc.AnimationClip
                        4: "prefab",    # cc.Prefab
                        5: "spine",     # sp.SkeletonData (Spine)
                        6: "asset",     # cc.Asset
                        7: "spriteframe"# cc.SpriteFrame
                    }
                    
                    # 确保输出目录存在
                    for category in set(type_categories.values()):
                        os.makedirs(os.path.join(output, category), exist_ok=True)
                    
                    # 映射表
                    mapping = {}
                    copied_files = set()  # 跟踪已复制的文件，避免重复
                    
                    # 处理此配置文件的资源
                    for idx, (res_id, res_info) in enumerate(paths.items(), 1):
                        try:
                            # 资源信息: [原始路径, 类型索引]
                            original_path = res_info[0]
                            type_idx = res_info[1]
                            
                            # 获取UUID
                            uuid = uuids[int(res_id)]  # res_id是字符串，需转int索引
                            
                            # 确定资源类型和分类目录
                            if type_idx < len(types):
                                res_type = types[type_idx]
                            else:
                                res_type = "unknown"
                            
                            category = type_categories.get(type_idx, "unknown")
                            
                            # 源文件路径 (在import目录下)
                            import_path = os.path.join(source, "import", uuid)
                            assets_path = os.path.join(source, "assets", original_path)
                            
                            # 查找文件的实际位置
                            source_file = None
                            if os.path.exists(import_path):
                                source_file = import_path
                            elif os.path.exists(assets_path):
                                source_file = assets_path
                            else:
                                # 尝试在父目录查找
                                parent_dir = os.path.dirname(original_path)
                                parent_path = os.path.join(source, "assets", parent_dir)
                                if os.path.exists(parent_path):
                                    for file in os.listdir(parent_path):
                                        if file.startswith(uuid):
                                            source_file = os.path.join(parent_path, file)
                                            break
                            
                            if not source_file or not os.path.exists(source_file):
                                raise FileNotFoundError(f"找不到资源文件: {uuid}")
                            
                            # 获取原始扩展名 (从路径推断)
                            _, ext = os.path.splitext(original_path)
                            if not ext:
                                # 如果原始路径没有扩展名，尝试从实际文件获取
                                _, actual_ext = os.path.splitext(source_file)
                                ext = actual_ext if actual_ext else ".bin"
                            
                            # 新文件名和路径
                            new_filename = f"{uuid}{ext}"
                            dest_file = os.path.join(output, category, new_filename)
                            
                            # 复制文件
                            file_key = (source_file, dest_file)  # 避免重复复制相同位置的文件
                            if file_key not in copied_files:
                                shutil.copy2(source_file, dest_file)
                                copied_files.add(file_key)
                                copied = True
                            else:
                                copied = False
                            
                            # 记录到映射表
                            mapping[uuid] = {
                                "config": config_name,
                                "original_path": original_path,
                                "new_path": os.path.join(category, new_filename),
                                "type": res_type,
                                "copied": copied
                            }
                            
                            success_count += 1
                            total_resources += 1
                            
                            # 记录日志（仅记录错误时）
                        except Exception as e:
                            error_count += 1
                            with open(log_path, "a", encoding="utf-8") as log_file:
                                log_file.write(f"❌ 资源ID {res_id} 处理失败: {str(e)}\n")
                        
                        # 更新进度
                        if total_resources > 0:
                            progress_value = (total_resources / (total_resources + len(paths) - idx)) * 100
                            self.progress.set(min(progress_value, 100))
                            self.progress_label.set(f"处理中: {total_resources} 资源 | 成功: {success_count} 失败: {error_count}")
                            self.root.update_idletasks()
                    
                    # 保存此配置的映射表
                    config_mapping_path = os.path.join(output, f"{config_name}_资源映射表.json")
                    with open(config_mapping_path, "w", encoding="utf-8") as f:
                        json.dump(mapping, f, indent=2, ensure_ascii=False)
                    
                    with open(log_path, "a", encoding="utf-8") as log_file:
                        log_file.write(f"✅ 配置文件 {config_name} 处理完成!\n")
                        log_file.write(f"  成功资源: {len(paths)} 个\n")
                        log_file.write(f"  映射表已保存到: {config_mapping_path}\n\n")
                    
                    processed_configs += 1
                    
                except Exception as e:
                    error_count += 1
                    with open(log_path, "a", encoding="utf-8") as log_file:
                        log_file.write(f"❌ 配置文件 {config_name} 处理失败: {str(e)}\n\n")
            
            # 最终日志总结
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write("\n" + "=" * 50 + "\n")
                log_file.write(f"所有配置文件处理完成!\n")
                log_file.write(f"处理配置文件数: {len(config_files)}\n")
                log_file.write(f"成功处理配置文件: {processed_configs}\n")
                log_file.write(f"失败配置文件: {len(config_files) - processed_configs}\n")
                log_file.write(f"处理资源总数: {total_resources}\n")
                log_file.write(f"成功资源: {success_count}\n")
                log_file.write(f"失败资源: {error_count}\n")
                log_file.write(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            if processed_configs == 0:
                messagebox.showerror("错误", 
                    f"所有配置文件处理失败!\n共 {len(config_files)} 个配置文件\n请查看日志: {log_path}")
            else:
                messagebox.showinfo("完成", 
                    f"资源整理完成!\n成功处理: {processed_configs}/{len(config_files)} 配置文件\n资源总数: {total_resources}\n成功: {success_count}\n失败: {error_count}\n日志: {log_path}")
            
        except Exception as e:
            # 尝试记录错误到日志
            try:
                with open(log_path, "a", encoding="utf-8") as log_file:
                    log_file.write(f"\n❌ 严重错误: {str(e)}\n")
            except:
                pass
            
            messagebox.showerror("错误", f"处理失败: {str(e)}")
        finally:
            # 打开文件夹
            output_dir = self.output_path.get()
            if os.path.exists(output_dir):
                os.startfile(output_dir)
            
            self.organize_btn["state"] = "normal"
            self.progress_label.set("准备就绪")
            self.progress.set(0)

if __name__ == "__main__":
    app = ToolApp()
    app.root.mainloop()