import shutil

def handle(source_file, dest_file, res_info, log_file):
    shutil.copy2(source_file, dest_file)
    return True, "Spine资源处理成功"