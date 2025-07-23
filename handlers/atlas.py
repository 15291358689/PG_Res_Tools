import shutil
from utils import *

def handle(proc, config, res_id, save_path):

    try:
        proc.logInfo += f'\n》atlas处理:'
        packName = ""
        packIds = []
        for key, values in proc.packs.items():
            if(not packName == ""):break
            if res_id in values :
                packName = key
                packIds = values
                break
                    
        if(packName == ""):
            return False,"atlas 处理失败,不包含与任何pack中。"
        
        packField = find_field_json(proc.source,packName)
        if(packField is None):
            return False,f"atlas 处理失败,匹配到的pack不存在:{packName}"
        
        packUuidS = [proc.uuids[i] for i in packIds if 0 <= i < len(proc.uuids)]
        packIndex = packIds.index(res_id)
        
        # packField = packField[0]
        fieldUuidS = packField[1]
        fieldAtlasData = packField[5][packIndex]
        atlasSonS = fieldAtlasData[5]
        atlasSonUuidS = [fieldUuidS[i] for i in atlasSonS if 0 <= i < len(fieldUuidS)]
        
        atlasSonIdxS = [proc.uuids.index(uuid) for uuid in atlasSonUuidS]
        fieldAtlasSonIdxS = [packIds.index(i) for i in atlasSonIdxS]

        

        # 获取图片资源
        imageResId = proc.uuids.index(fieldUuidS[fieldAtlasData[1]])
        native = proc.versions.get("native")
        if(not imageResId in native): 
            return False,f'atlas 处理失败,没有相关资源图：{save_path} | id：{imageResId}'
        
        hash_str = native[native.index(imageResId) + 1]
        imageField = find_field_image(proc.source,hash_str)
        if(imageField is None):
            return False,f'atlas 处理失败,匹配到的图不存在 {save_path} | id：{imageResId}'
        imageSaveName = proc.paths.get(f'{imageResId}')[0].split('/')[-1]
        imageNewName = f'{imageSaveName}.{save_image(imageField,save_path,imageSaveName).split('.')[-1]}'

        atlasSaveName = save_path.split('/')[-1]
        wh = get_image_size(imageField)
        # 把atlasSonS 中 fieldAtlasSonIdxS序号的文件转为 atlas
        atlasDataS = [packField[5][i][0][0] for i in fieldAtlasSonIdxS]
        atlasDataStr = convert_atlas_array(atlasDataS,imageNewName,wh)
        save_atlas_file(atlasDataStr,save_path,atlasSaveName)

        return True, "atlas 资源处理成功"
    
    except Exception as e:
        return False, "****atlas 处理失败****"
