import json
import os
import re
import shutil
from PIL import Image

def find_config_json(source):
    config_files = []
    pattern = re.compile(r'^config\.[a-f0-9]+\.json$', re.IGNORECASE)
    
    for root, _, files in os.walk(source):
        for file in files:
            if pattern.match(file):  # 如果文件名符合规则
                file_path = os.path.join(root, file)
                
                # 检查文件是否是有效的 JSON 格式
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        config_files.append(file_path)  # 如果包含选中的类型，加入列表
                except json.JSONDecodeError:
                    print(f"警告: 文件 {file_path} 不是有效的 JSON 文件")
                except Exception as e:
                    print(f"处理文件 {file_path} 时出现错误: {e}")
    
    return config_files

def find_field_json(source, name):
    pattern = re.compile(rf'.*{re.escape(name)}.*\.json$', re.IGNORECASE)

    for root, _, files in os.walk(source):
        for file in files:
            if pattern.match(file):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)  # 加载 JSON 数据
                        return data  # 找到第一个匹配项后立即返回
                except json.JSONDecodeError:
                    print(f"警告: 文件 {file_path} 不是有效的 JSON 文件")
                    continue  # 继续查找下一个文件
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {e}")
                    continue  # 继续查找下一个文件

    return None  # 如果没有找到任何匹配项，返回 None

def find_field_path(source, name):
    field_pattern = re.compile(rf'^.+\.{re.escape(name)}\..*?$', re.IGNORECASE)

    for root, _, files in os.walk(source):
        for file in files:
            if field_pattern.match(file):
                return os.path.join(root, file)

    return

def copy_field(src_path, dst_dir, new_name,addExt = True):
    """
    复制文件到新路径并重命名（保留后缀），自动创建目录，覆盖同名文件
    
    :param src_path: 原路径（如 "/data/old_image.jpg"）
    :param dst_dir: 目标文件夹（如 "/backup"）
    :param new_name: 新文件名（不带后缀，如 "new_image"）
    :return: 新文件的完整路径
    """
    # 确保目标目录存在
    os.makedirs(dst_dir, exist_ok=True)
    
    # 提取原文件后缀（如 ".jpg"）
    _, ext = os.path.splitext(src_path)
    
    # 构建新文件路径（新名字 + 原后缀）
    new_filename = f"{new_name}{ext if not addExt else ''}"
    dst_path = os.path.join(dst_dir, new_filename)
    
    # 复制文件（自动覆盖同名文件）
    shutil.copy2(src_path, dst_path)
    
    return dst_path

def get_image_size(image_path):
    """获取图片的宽度和高度"""
    with Image.open(image_path) as img:
        width, height = img.size  # 返回 (width, height)
        return [width, height]
    

def convert_atlas_array(atlas_json_list, img_name, atlas_size, 
                       format="RGBA8888", 
                       filter="Linear,Linear",
                       repeat="none"):
    """
    将JSON图集对象数组转换为标准图集格式
    :param atlas_json_list: JSON格式的纹理列表
    :param img_name: 图像文件名
    :param atlas_size: 图集尺寸 (width, height)
    :param format: 像素格式
    :param filter: 过滤模式
    :param repeat: 重复模式
    :return: 字符串格式的完整图集文件
    """
    # 生成头部信息
    atlas_str = [
        f"{img_name}",
        f"size: {atlas_size[0]},{atlas_size[1]}",
        f"format: {format}",
        f"filter: {filter}",
        f"repeat: {repeat}"
    ]
    
    # 处理每个纹理项
    for item in atlas_json_list:
        # 提取各项数据
        name = item.get("name", "unknown")
        rect = item.get("rect", [0, 0, 0, 0])
        orig_size = item.get("originalSize", rect[2:])
        offset = item.get("offset", [0, 0])
        rotated = item.get("rotated",0)
        
        # 添加纹理信息
        atlas_str.append(f"{name}")
        atlas_str.append(f"  rotate: {False if rotated == 0 else True}")
        atlas_str.append(f"  xy: {int(rect[0])},{int(rect[1])}")
        atlas_str.append(f"  size: {int(rect[2])},{int(rect[3])}")
        atlas_str.append(f"  orig: {int(orig_size[0])},{int(orig_size[1])}")
        atlas_str.append(f"  offset: {int(offset[0])},{int(offset[1])}")
        atlas_str.append(f"  index: -1")
    
    # 返回连接后的完整图集文件
    return "\n".join(atlas_str)

def save_file(content, folder_path, filename):
    """
    将内容保存为文件
    
    :param atlas_content: 从convert_atlas_array返回的字符串
    :param folder_path: 目标文件夹路径
    :param filename: 文件名（含后缀）
    """
    # 确保文件夹存在，不存在则创建
    os.makedirs(folder_path, exist_ok=True)
    
    # 拼接完整文件路径
    file_path = os.path.join(folder_path, filename)
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"文件已保存至: {file_path}")
    return file_path