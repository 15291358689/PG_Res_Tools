import shutil
from utils import * 

def handle(proc, info, res_id, save_path):

    try:
        proc.logInfo += f'\n》音频 处理:'

        # 获取音频资源
        native = proc.versions.get("native")
        if(not res_id in native): 
            return False,f'音频 处理失败,没有相关资源：{save_path} | id：{res_id}'
        
        hash_str = native[native.index(res_id) + 1]

        audioField = find_field_path(proc.source,hash_str)
        if(audioField is None):
            return False,f'音频 处理失败,匹配到的资源不存在 {audioField} | id：{res_id}'
        
        audioSaveName = proc.paths.get(f'{res_id}')[0].split('/')[-1]
        audioNewName = f'{audioSaveName}.{copy_field(audioField,f'{proc.output}/audio',audioSaveName).split('.')[-1]}'

        return True, "音频 资源处理成功"
    
    except Exception as e:
        return False, "****音频 处理失败****"