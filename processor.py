import os
import json
import shutil
import time
from tkinter import messagebox
from config import TYPE_CATEGORIES
from utils import find_config_json
from handlers import get_handler_for_type

def process_resources(source, output, selected_types, update_progress_callback):
    os.makedirs(output, exist_ok=True)
    log_path = os.path.join(output, "资源整理日志.txt")

    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write("Cocos资源整理日志\n")
        log_file.write(f"源文件夹: {source}\n")
        log_file.write(f"输出文件夹: {output}\n")
        log_file.write(f"处理的资源类型: {', '.join(selected_types)}\n")
        log_file.write(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("=" * 50 + "\n\n")

    config_files = find_config_json(source)

    print(config_files)

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

            paths = config.get("paths", {})
            types = config.get("types", [])
            uuids = config.get("uuids", [])

            for category in set(TYPE_CATEGORIES.values()):
                os.makedirs(os.path.join(output, category), exist_ok=True)

            for idx, (res_id, res_info) in enumerate(paths.items(), 1):
                try:
                    original_path = res_info[0]
                    type_idx = res_info[1]
                    uuid = uuids[int(res_id)]
                    res_type = types[type_idx] if type_idx < len(types) else "unknown"

                    if res_type not in selected_types:
                        continue

                    category = TYPE_CATEGORIES.get(res_type, "unknown")
                    import_path = os.path.join(source, "import", uuid)
                    assets_path = os.path.join(source, "assets", original_path)

                    source_file = import_path if os.path.exists(import_path) else assets_path
                    if not os.path.exists(source_file):
                        continue

                    _, ext = os.path.splitext(original_path)
                    if not ext:
                        _, ext = os.path.splitext(source_file)
                    dest_file = os.path.join(output, category, f"{uuid}{ext}")

                    handler = get_handler_for_type(res_type)
                    handler(source_file, dest_file, res_info, log_path)

                    success_count += 1
                    total_resources += 1

                except Exception:
                    error_count += 1

                update_progress_callback(idx, len(paths), success_count, error_count)

        except Exception as e:
            with open(log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"配置文件 {config_path} 处理失败: {str(e)}\n")

    messagebox.showinfo("完成", f"成功: {success_count}, 失败: {error_count}, 总数: {total_resources}")