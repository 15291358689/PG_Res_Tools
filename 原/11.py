import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
import re
import threading
import time
from PIL import Image


class ToolApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("素材整理工具")
        self.root.geometry("680x420")  # 更紧凑的尺寸
        self.root.minsize(600, 380)    # 设置最小尺寸
        
        # 存储路径的变量
        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # 进度条相关变量 [6,7]
        self.progress = tk.DoubleVar()
        self.progress_label = tk.StringVar()
        
        # 自动路径跟踪
        self.auto_path = True  # 自动路径标记
        self.source_path.trace_add("write", self.auto_set_output)  # 绑定路径变化事件

        self.create_widgets()

    def auto_set_output(self, *args):
        """资源路径变化时自动设置输出路径"""
        if self.auto_path:
            source = self.source_path.get()
            if source:
                self.output_path.set(os.path.join(source, "OUT"))

    def create_widgets(self):
        # 统一控件样式
        style = ttk.Style()
        style.configure("TLabelFrame", padding=10)
        style.configure("TButton", padding=6)

        # 资源文件夹选择框
        source_frame = ttk.LabelFrame(self.root, text="资源文件夹")
        source_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Entry(source_frame, textvariable=self.source_path).pack(
            side="left", padx=5, pady=5, fill="x", expand=True)
        ttk.Button(source_frame, text="浏览", 
                  command=lambda: self.select_folder(self.source_path, "选择资源文件夹")).pack(
                      side="right", padx=5)
        
        # 输出文件夹选择框
        output_frame = ttk.LabelFrame(self.root, text="输出文件夹")
        output_frame.pack(padx=10, pady=10, fill="x")
        
        ttk.Entry(output_frame, textvariable=self.output_path).pack(
            side="left", padx=5, pady=5, fill="x", expand=True)
        ttk.Button(output_frame, text="浏览", 
                  command=lambda: self.select_folder(self.output_path, "选择输出文件夹")).pack(
                      side="right", padx=5)
        
        # 进度条组件 [6,7]
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
            text="整理", 
            command=self.start_processing_thread
        )
        self.organize_btn.pack(pady=20)

    def select_folder(self, path_var, title):
        """手动选择时禁用自动路径"""
        if path_var == self.output_path:
            self.auto_path = False  # 手动选择时禁用自动更新

        folder = filedialog.askdirectory(title=title)
        if folder:
            path_var.set(folder)
            
    def start_processing_thread(self):
        """启动处理线程"""
        self.organize_btn["state"] = "disabled"
        threading.Thread(target=self.process_files).start()

    
    def process_files(self):
        """核心处理逻辑"""
        try:
            source = self.source_path.get()
            output = self.output_path.get()

            if not all([source, output]):
                raise ValueError("请先选择文件夹")
                
            # 递归收集所有JSON文件
            json_files = []
            for root, _, files in os.walk(source):
                for file in files:
                    if file.lower().endswith(".json"):
                        json_files.append(os.path.join(root, file))
            
            # 全局收集所有PNG图片路径
            all_images = []
            for root, _, files in os.walk(source):
                for file in files:
                    if file.lower().endswith(".png"):
                        all_images.append(os.path.join(root, file))
            
            total = len(json_files)
            success_count = 0
            error_count = 0
            
            # 初始化进度条
            self.progress.set(0)
            self.progress_label.set("开始处理...")
            self.root.update_idletasks()
            
            error_folder = os.path.join(output, "errors")
            os.makedirs(error_folder, exist_ok=True)

            # 创建日志文件
            log_path = os.path.join(output, "Log.txt")
            with open(log_path, "w", encoding="utf-8") as log_file:
                log_file.write("素材整理日志\n")
                log_file.write(f"源文件夹: {source}\n")
                log_file.write(f"输出文件夹: {output}\n")
                log_file.write(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_file.write("=" * 50 + "\n\n")
            
            # 只记录已复制的图片，用于避免重复复制
            copied_images = set()
            
            # SpineData计数器
            spine_counter = 1
            
            for idx, json_path in enumerate(json_files, 1):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    # 验证数据结构
                    if not (isinstance(data, list) and len(data) > 5 and data[3][0][0] == "sp.SkeletonData"):
                        continue
                    
                    # 计算源文件的相对路径（相对于资源文件夹）
                    source_relative_path = os.path.relpath(json_path, source)
                    
                    for spineData in data[5]:
                        # 获取 atlas
                        atlas_content = spineData[2].replace("\n", "",1)
                        # 生成.json文件
                        json_content = json.dumps(spineData[4], ensure_ascii=False)

                        # 获取目标图片大小
                        sizeString = atlas_content.split("\n")[1]
                        size_match = re.search(r"size:\s*(\d+),\s*(\d+)", sizeString) 
                        if not size_match:
                            continue
                        
                        target_size = f"{size_match.group(1)}x{size_match.group(2)}"

                        # 创建目标文件夹
                        target_folder_name = spineData[3][0] + target_size
                        target_folder = os.path.join(output, target_folder_name)
                        os.makedirs(target_folder, exist_ok=True)

                        # 生成.atlas文件
                        atlas_file_name = f"{spineData[1]}.atlas"
                        atlas_path = os.path.join(target_folder, atlas_file_name)
                        with open(atlas_path, "w", encoding="utf-8") as f:
                            f.write(atlas_content)
                            
                        # 生成.json文件
                        json_file_name = f"{spineData[1]}.json"
                        spine_json_path = os.path.join(target_folder, json_file_name)
                        with open(spine_json_path, "w", encoding="utf-8") as f:
                            f.write(json_content)

                        # 全局搜索匹配的图片
                        matched_image = None
                        for img_path in all_images:
                            try:
                                with Image.open(img_path) as img:
                                    img_size = f"{img.width}x{img.height}"
                                
                                # 尺寸匹配时选择该图片
                                if img_size == target_size:
                                    matched_image = img_path
                                    break
                            except:
                                # 跳过无法打开的图片
                                continue
                        
                        # 记录日志（无论是否找到图片）
                        # 计算Atlas和Json文件的相对路径（相对于输出文件夹）
                        atlas_relative_path = os.path.join(target_folder_name, atlas_file_name)
                        spine_json_relative_path = os.path.join(target_folder_name, json_file_name)
                        
                        with open(log_path, "a", encoding="utf-8") as log_file:
                            log_file.write(f"============第{spine_counter}个=============\n")
                            # 修正：使用源JSON文件的相对路径
                            log_file.write(f"源文件: {source_relative_path}\n")
                            log_file.write(f"Atlas: {atlas_relative_path}\n")
                            log_file.write(f"Json: {spine_json_relative_path}\n")
                            log_file.write(f"目标尺寸: {target_size}\n")
                            
                            if matched_image:
                                # 使用原始命名方式
                                new_image_name = spineData[3][0]
                                
                                # 计算匹配图片的相对路径（相对于资源文件夹）
                                image_relative_path = os.path.relpath(matched_image, source)
                                
                                # 仅当图片尚未复制时才进行复制
                                if matched_image not in copied_images:
                                    dest_img = os.path.join(target_folder, new_image_name)
                                    shutil.copy2(matched_image, dest_img)
                                    copied_images.add(matched_image)
                                    log_file.write(f"匹配图片: {image_relative_path} => {new_image_name} (已复制)\n")
                                else:
                                    log_file.write(f"匹配图片: {image_relative_path} => {new_image_name} (已存在)\n")
                            else:
                                log_file.write("匹配图片: 未找到匹配图片\n")
                            
                            log_file.write("\n")
                        
                        spine_counter += 1
                    
                    # 成功处理一个JSON文件
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    error_file = os.path.join(error_folder, os.path.basename(json_path))
                    shutil.copy2(json_path, error_file)
                    with open(os.path.join(error_folder, "error.log"), "a") as log:
                        log.write(f"{json_path}: {str(e)}\n")
                
                # 更新进度
                self.progress.set((idx / total) * 100)
                self.progress_label.set(f"处理中: {idx}/{total} 文件 | 成功: {success_count} 失败: {error_count}")
                self.root.update_idletasks()
                
            # 在日志中添加总结信息
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write("\n" + "=" * 50 + "\n")
                log_file.write(f"处理完成! 成功: {success_count}, 失败: {error_count}\n")
                log_file.write(f"结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                log_file.write(f"已复制图片总数: {len(copied_images)}\n")
            
            messagebox.showinfo("完成", f"处理完成！\n成功: {success_count}\n失败: {error_count}\n日志已保存到: {log_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"严重错误: {str(e)}")
        finally:
            # 打开文件夹
            output_dir = self.output_path.get()
            if os.path.exists(output_dir):
                os.startfile(output_dir)
            
            self.organize_btn["state"] = "normal"
            self.progress_label.set("准备就绪")

if __name__ == "__main__":
    app = ToolApp()
    app.root.mainloop()