import shutil
from utils import *

def handle(proc, info, res_id, save_path):
    
    try:
        proc.logInfo += f'\n》Spine 处理:'

        # atlas 部分
        importData = proc.versions.get("import")
        if(not res_id in importData): 
            return False,f'Spine atlas处理失败,没有相关资源'
        hash_str = importData[importData.index(res_id) + 1]
        jsonField = find_field_json(proc.source,hash_str)
        if(jsonField is None):
            return False,f'Spine atlas处理失败,没有Json资源'
        spineData = jsonField[5][0]
        
        # 图片
        # imageResId = proc.uuids.index(jsonField[1][0])
        # native = proc.versions.get("native")
        # if(not imageResId in native): 
        #     return False,f'Spine 图片处理失败,没有相关资源图'
        # hash_str = native[native.index(imageResId) + 1]
        # imageField = find_field_path(proc.source,hash_str)
        # if(imageField is None):
        #     return False,f'Spine 图片处理失败,匹配到的图不存在'
        # imageSaveName = spineData[3][0].split(".")[0]
        
        imageResIdS = [proc.uuids.index(jsonField[1][i]) for i in jsonField[5][0][5]]
        native = proc.versions.get("native")
        save_path = f'{proc.output}/spine/{spineData[3][0].split(".")[0]}' 
        
        # 多图处理
        for i, imageResId in enumerate(imageResIdS):
            if(not imageResId in native): 
                proc.logInfo += f'\npack 处理失败,没有相关资源图 id：{imageResId}'
                continue
            hash_str = native[native.index(imageResId) + 1]
            imageField = find_field_path(proc.source,hash_str)
            if(imageField is None):
                proc.logInfo += f'\npack 处理失败,匹配到的图不存在 id：{imageResId}'
                continue
            # 未实现保存
            copy_field(imageField,save_path,spineData[3][i],False)

        # 保存文件
        save_file(spineData[2],save_path,spineData[1]+".atlas")
        animJson = spineData[4]
        save_file(json.dumps(animJson),save_path,spineData[1] + ".json")

        return True, "Spine 资源处理成功"
    
    except Exception as e:
        return False, f"****Spine 处理失败****\n{e}"