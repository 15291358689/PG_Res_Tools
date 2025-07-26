import shutil
from utils import *
import traceback
from collections import defaultdict

# type_handler_map = {
#     "cc.SpriteAtlas": atlas.handle,
#     "sp.SkeletonData": spine.handle,
# }

def handle(proc, info, res_id, save_path):
    
    try:
        proc.logInfo += f'\n》pack 处理:'

        packField = find_field_json(proc.source,info[1])
        if packField is None:
            return False,f"未找到json ：{info[0]}.{info[1]}"

        imageDataS = {}

        if info[0] == "07cdeb531":

            proc.logInfo += ""
        
        for value in packField[5]:
            try:
                data = value[0][0]
                if "rect" in data:
                    # 正常atlas 数据
                    image = value[5][0]
                    if image not in imageDataS:
                        imageDataS[image] = []  # 初始化空列表
                    imageDataS[image].append(value[0])

                elif packField[3][data[0]][0] == "sp.SkeletonData":
                    # 骨骼动画 特殊处理
                    # 图
                    save_path_sk = f'{proc.output}/spine/{data[3][0].split('.')[0]}' 
                    imageResIdS = [proc.uuids.index(packField[1][i]) for i in value[5]]
                    native = proc.versions.get("native")

                    # 多图处理
                    for imageResId in imageResIdS:
                        native = proc.versions.get("native")
                        if(not imageResId in native): 
                            proc.logInfo += f'\npack 处理失败,没有相关资源图 id：{imageResId}'
                            continue
                        hash_str = native[native.index(imageResId) + 1]
                        imageField = find_field_path(proc.source,hash_str)
                        if(imageField is None):
                            proc.logInfo += f'\npack 处理失败,匹配到的图不存在 id：{imageResId}'
                            continue
                        # 未实现保存
                        copy_field(imageField,save_path_sk,imageNameNew)

                    
                    # 保存 文件
                    save_file(data[2].lstrip("\n"),save_path_sk,data[1]+".atlas")
                    save_file(json.dumps(data[4]),save_path_sk,data[1] + ".json")

                continue
            except :
                continue
            
        for key,value in imageDataS.items():
            
            imageNameUuid = packField[1][key]


            # 获取图片资源
            imageResId = proc.uuids.index(imageNameUuid)
            native = proc.versions.get("native")
            if(not imageResId in native): 
                proc.logInfo += f'\npack 处理失败,没有相关资源图 id：{imageResId}'
                continue
            hash_str = native[native.index(imageResId) + 1]
            imageField = find_field_path(proc.source,hash_str)
            if(imageField is None):
                proc.logInfo += f'\npack 处理失败,匹配到的图不存在 id：{imageResId}'
                continue
            newSavePath = f'{save_path}/Image/{hash_str}'
            copy_field(imageField,newSavePath,hash_str)

            # atlas
            imageNameS = [d[0].get("name") for d in value]
            atlasName = extract_representation(imageNameS)
            imageSaveName = f'{hash_str}.{imageField.split('.')[-1]}' 
            atlasS = [d[0] for d in value]
            atlasStr = convert_atlas_array(atlasS,imageSaveName,get_image_size(imageField))
            save_file(atlasStr,newSavePath,f'{atlasName}.atlas')

        return True, "pack 资源处理成功"
    
    except Exception :
        error_info = traceback.format_exc()
        return False, f"****pack 处理失败****\n{error_info}"
    

def extract_representation(strings):
    if not strings:
        return "error"
    
    # 1. 提取所有字符串的基础前缀（去除数字和版本信息）
    base_names = []
    for s in strings:
        # 移除开头和结尾的非字母字符（如空格）
        s = s.strip()
        
        # 尝试移除版本号和序列号（如 "_01", "_v2", "04" 等）
        # 使用正则表达式匹配常见的版本模式
        base = re.sub(r'(_?[0-9]{1,3}(_[0-9]{1,3})?)$', '', s)  # 移除结尾的数字序列
        base = re.sub(r'(_v[0-9]{1,2})$', '', base)             # 移除版本号
        base = re.sub(r'(_[a-z]{2,4})$', '', base)              # 移除短后缀（如_add, _vfx）
        
        # 如果处理后为空，则使用原始字符串
        base_names.append(base if base else s)
    
    # 2. 找出所有字符串的共同前缀
    common_prefix = base_names[0]
    for name in base_names[1:]:
        # 找出两个字符串的最长公共前缀
        min_len = min(len(common_prefix), len(name))
        for i in range(min_len):
            if common_prefix[i] != name[i]:
                common_prefix = common_prefix[:i]
                break
        # 如果没有公共前缀，提前结束
        if not common_prefix:
            break
    
    # 3. 如果所有字符串有共同前缀，返回它
    if common_prefix and all(name.startswith(common_prefix) for name in base_names):
        # 清理前缀结尾的分隔符
        return common_prefix.rstrip('_ ')
    
    # 4. 没有共同前缀时，提取主要词根
    word_groups = defaultdict(int)
    for name in base_names:
        # 分割字符串为单词（处理多种分隔符）
        words = re.split(r'[_\s]+', name)
        # 只保留有意义的单词（长度>1）
        meaningful_words = [word for word in words if len(word) > 1]
        
        if meaningful_words:
            # 使用第一个有意义的单词作为词根
            word_groups[meaningful_words[0]] += 1
    
    # 5. 返回出现频率最高的1-2个词根
    if not word_groups:
        return ""
    
    sorted_words = sorted(word_groups.items(), key=lambda x: x[1], reverse=True)
    
    if len(sorted_words) == 1:
        return sorted_words[0][0]
    else:
        # 返回前两个词根（按字母顺序）
        return " and ".join(sorted([word for word, _ in sorted_words[:2]]))