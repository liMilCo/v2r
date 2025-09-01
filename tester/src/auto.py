import json
import os
import platform
import subprocess
import time
import requests
import sys
import threading
import base64
import html
import webbrowser
import binascii
import random
from urllib.parse import urlparse, parse_qs, unquote
import tkinter as tk
from tkinter import messagebox, font, filedialog
if sys.platform == 'win32':
    from subprocess import CREATE_NO_WINDOW

from v2ray2json import generateConfig  #https://github.com/arminmokri/v2ray2json
#=======================================================================

XRAY_PATH = "xray_test.exe" #https://github.com/XTLS/Xray-core
SRC_CONFIG = "https://raw.githubusercontent.com/liMilCo/v2r/main/sub/1.txt"
#SRC_CONFIG = "src.txt"


BEST_CONFIG_FILE = "best.txt"
TEMP_CONFIG_FILE = "temp_config.json"
WEBSITES_TO_TEST = ["https://www.google.com"] # ["https://www.google.com", "https://www.youtube.com"]
PROXY_IP = "127.0.0.1"
PROXY_PORT = random.randint(49152, 65535) #55555

COMMON_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}


#=======================================================================

def decode_b64(base: str) -> str:
    base = unquote(base)
    # Calculate the required padding
    missing_padding = len(base) % 4
    if missing_padding != 0:
        base += '=' * (4 - missing_padding)

    return base64.b64decode(base).decode('utf-8')
"""
def v2ray_uri_to_json(uri: str) -> dict:

    #Converts a V2Ray URI (vmess, vless, trojan) to a V2Ray JSON configuration.
    try:
        parsed_uri = urlparse(uri)
        protocol = parsed_uri.scheme

        if protocol == "vmess":
            # Decode the base64-encoded part of the VMess URI
            vmess_config = uri[8:]
            decoded_payload = decode_b64(vmess_config)  #base64.b64decode(unquote(parsed_uri.netloc)).decode('utf-8')
            vmess_data = json.loads(decoded_payload)

            # Construct the VMess outbound configuration
            json_config = {
                "outbounds": [
                    {
                        "protocol": "vmess",
                        "settings": {
                            "vnext": [
                                {
                                    "address": vmess_data.get("add"),
                                    "port": int(vmess_data.get("port")),
                                    "users": [
                                        {
                                            "id": vmess_data.get("id"),
                                            "alterId": int(vmess_data.get("aid", 0)),
                                            "security": vmess_data.get("scy", "auto"),
                                            "level": int(vmess_data.get("lvl", 0))
                                        }
                                    ]
                                }
                            ]
                        },
                        "streamSettings": {
                            "network": vmess_data.get("net"),
                            "security": vmess_data.get("tls", "none"),
                            "wsSettings": {
                                "path": vmess_data.get("path", "/"),
                                "headers": {
                                    "Host": vmess_data.get("host", "")
                                }
                            } if vmess_data.get("net") == "ws" else {}
                        },
                        "mux": {
                            "enabled": False
                        }
                    }
                ],
                "log": { "loglevel": "warning" }
            }
            return json_config

        elif protocol == "vless":
            # VLESS URIs are typically structured differently, requiring direct parsing of components
            # Example: vless://uuid@server:port?params#name
            user_info, server_info = parsed_uri.netloc.split('@')
            uuid = user_info
            server_address, server_port = server_info.split(':')
            
            # Parse query parameters for stream settings
            # Use parse_qs for reliable parsing of repeated keys
            query_params = parse_qs(parsed_uri.query)
            
            # Unpack parameters, providing defaults
            flow = query_params.get("flow", [""])[0]
            encryption = query_params.get("encryption", ["none"])[0]
            security = query_params.get("security", ["none"])[0]
            network = query_params.get("type", ["tcp"])[0]
            
            # Extract optional TLS/Reality parameters
            sni = query_params.get("sni", [""])[0]
            fingerprint = query_params.get("fp", [""])[0]
            pbk = query_params.get("pbk", [""])[0]
            sid = query_params.get("sid", [""])[0]
            spx = query_params.get("spx", [""])[0]
            
            # Determine the tag from the fragment
            tag = unquote(parsed_uri.fragment) if parsed_uri.fragment else f"vless-{server_address}:{server_port}"
            
            # Build streamSettings conditionally based on security
            stream_settings = {
                "network": network,
                "security": security
            }

            if network == "ws":
                ws_host = query_params.get("host", [""])[0]
                ws_path = unquote(query_params.get("path", ["/"])[0])
                stream_settings["wsSettings"] = {
                    "path": ws_path,
                    "headers": {"Host": ws_host}
                }

            if security == "tls":
                stream_settings["tlsSettings"] = {"serverName": sni}
            
            elif security == "reality":
                stream_settings["realitySettings"] = {
                    "show": False,
                    "fingerprint": fingerprint,
                    "serverName": sni,
                    "publicKey": pbk,
                    "shortId": sid,
                    "spiderX": spx
                }

            # Construct the VLESS outbound configuration
            json_config = {
                "outbounds": [
                    {
                        "protocol": "vless",
                        "tag": tag,
                        "settings": {
                            "vnext": [
                                {
                                    "address": server_address,
                                    "port": int(server_port),
                                    "users": [
                                        {
                                            "id": uuid,
                                            "level": 0,
                                            "flow": flow,
                                            "encryption": encryption
                                        }
                                    ]
                                }
                            ]
                        },
                        "streamSettings": stream_settings
                    }
                ],
                "log": { "loglevel": "warning" }
            }
            return json_config

        elif protocol == "trojan":
            # Trojan URIs are also structured differently
            # Example: trojan://password@server:port?params
            password, server_info = parsed_uri.netloc.split('@')
            server_address, server_port = server_info.split(':')

            query_params = parse_qs(parsed_uri.query)

            json_config = {
                "outbounds": [
                    {
                        "protocol": "trojan",
                        "settings": {
                            "servers": [
                                {
                                    "address": server_address,
                                    "port": int(server_port),
                                    "password": password,
                                    "level": 0
                                }
                            ]
                        },
                        "streamSettings": {
                            "network": query_params.get("type", ["tcp"])[0],
                            "security": query_params.get("security", ["tls"])[0],
                            "tlsSettings": {
                                "serverName": query_params.get("sni", [""])[0]
                            }
                        }
                    }
                ],
                "log": { "loglevel": "warning" }
            }
            return json_config

        elif protocol == "ss":
            # Shadowsocks URI format: ss://base64(method:password)@address:port
            decoded_info = decode_b64(parsed_uri.netloc.split('@')[0])  #base64.b64decode(unquote(parsed_uri.netloc.split('@')[0])).decode('utf-8')
            method, password = decoded_info.split(':')
            address, port = parsed_uri.netloc.split('@')[1].split(':')

            json_config = {
                "outbounds": [
                    {
                        "protocol": "shadowsocks",
                        "settings": {
                            "servers": [
                                {
                                    "address": address,
                                    "port": int(port),
                                    "method": method,
                                    "password": password
                                }
                            ]
                        }
                    }
                ],
                "log": { "loglevel": "warning" }
            }
            return json_config
        else:
            raise ValueError(f"Unsupported V2Ray protocol: {protocol}")
    except Exception as e:
        #print(f"  [FAIL] Error Creating Config: {e}")
        return {"outbounds": False}
        #pass
"""
#=======================================================================


def start_xray(config_content: dict, config_file):
    global xray_process
    stop_xray()
    try:
        with open(config_file, "w", encoding='utf-8') as f: json.dump(config_content, f, indent=2)
    except Exception as e:
        ##print(f"  [FAIL] Error saving config: {e}") 
        return False
        
    
    xray = os.path.join(os.path.dirname(__file__), XRAY_PATH)


    try:
        startupinfo = None
        if sys.platform == 'win32':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        xray_process = subprocess.Popen([xray, 'run', '-config', config_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=CREATE_NO_WINDOW if sys.platform == 'win32' else 0, startupinfo=startupinfo)
                
        #creationflags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        #xray_process = subprocess.Popen([xray, "-c", config_file], creationflags=creationflags, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        if xray_process.poll() is not None:
            ##print(f"  [FAIL] Xray exited immediately.") 
            return False
        return True
    except Exception as e:
        #print(f"  [FAIL] Error starting Xray: {e}")
        return False
        #pass

def stop_xray_():
    global xray_process
    if xray_process and xray_process.poll() is None:
        try: xray_process.kill()
        except Exception: pass
    if platform.system() == "Windows": subprocess.run(["taskkill", "/F", "/IM", XRAY_PATH], capture_output=True, check=False)
    #else: subprocess.run(["killall", "-9", "xray"], capture_output=True, check=False)


def stop_xray():
    """Kill any existing Xray processes"""  # inserted
    try:
        if sys.platform == 'win32':
            import psutil
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] == XRAY_PATH:
                        proc.kill()
        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        return None
    except Exception as e:
        return None


def test_accessibility() -> bool:
    proxy_url = proxy_url = "socks5h://"+PROXY_IP+":"+str(PROXY_PORT)
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    for site in WEBSITES_TO_TEST:
        try:
            response = requests.get(site, proxies=proxies, timeout=5, headers=COMMON_HEADERS)
            if response.status_code != 200: return False
        except requests.exceptions.RequestException: return False
    return True

 

#======================================================================= 
def get_base(outbounds: dict):
    base = "X"
    outbound = outbounds[0] 
    if outbound["protocol"] in ["shadowsocks","trojan"]:
        base = outbound["protocol"]+outbound["settings"]["servers"][0]["password"]+outbound["settings"]["servers"][0]["address"]+str(outbound["settings"]["servers"][0]["port"])
    
    if outbound["protocol"] in ["vmess","vless"]:
        base = outbound["protocol"]+outbound["settings"]["vnext"][0]["users"][0]["id"]+outbound["settings"]["vnext"][0]["address"]+str(outbound["settings"]["vnext"][0]["port"])
    return base

#=======================================================================       

inbounds_config = {
            "inbounds": [
                {
                    "port": PROXY_PORT,
                    "listen": PROXY_IP,
                    "protocol": "socks",
                    "settings": {
                        "udp": True,
                    }
                }
            ],
            "log": { "loglevel": "warning" }
        }


#=======================================================================



def run_test(src):
    global total_i, g, dbl, check_doble
    try:
        output_folder = os.path.dirname(__file__)
        output_sysfolder = os.path.dirname(sys.argv[0])
        temp_config = os.path.join(output_folder, TEMP_CONFIG_FILE)
        best_configs = os.path.join(output_sysfolder, BEST_CONFIG_FILE)
        #best_configs = "./"+BEST_CONFIG_FILE
        best_configs_bu = os.path.join(output_sysfolder, "bu_"+BEST_CONFIG_FILE)
        #best_configs_bu = "./bu_"+BEST_CONFIG_FILE

        response_text = ""
        i = 0

        if src.startswith("http"):
            response_text = get_link(src) #requests.get(src).text
        else:
            #src = os.path.join(output_folder, SRC_CONFIG)
            src_configs = src
            if os.path.exists(src_configs):
                with open(src_configs, 'r', encoding='utf-8') as f:
                    response_text = f.read()
            else:
                send_error('File Config Src ['+src+'] Not found!')
                return False

        

        if not any(protcol in response_text for protcol in ["vless://","vmess://","ss://","trojan://"]):
            send_error("Can't found any Suported Config!")
            return False



        if total_i == 0 :
            # BackUp best_configs
            if os.path.exists(best_configs):
                with open(best_configs, 'r', encoding='utf-8') as f:
                    best_configs_get = f.read()
                with open(best_configs_bu, "a", encoding="utf-8") as f: 
                    f.write(best_configs_get + "\n")

            ##print(f'\nConfigs Source: [{src}]')

            now_time = time.ctime()
            with open(best_configs, "w", encoding="utf-8") as f: f.write("# Updated: "+now_time+"     ||     From: "+src+" \n")


        bests = ""

        count_configs = response_text.count('://')
        ##print(f'\nTotal Configs: [{count_configs}]')   

        for config_url in response_text.splitlines():
            try:
                if not start_run:
                    break
                if (config_url.startswith("vmess") or config_url.startswith("vless") or config_url.startswith("trojan") or config_url.startswith("ss")):
                    config_url = unquote(html.unescape(config_url))
                    #outbounds = v2ray_uri_to_json(config_url)
                    outbounds = json.loads(generateConfig(config_url))
                    if outbounds['outbounds']:


                        i += 1
                        if not i > total_i:
                            continue   

                        total_i += 1

                        outbounds_base  = get_base(outbounds['outbounds'])                    
                        if not outbounds_base in check_doble:
                            check_doble.append(get_base(outbounds['outbounds']))
                            


                            
                            config_json = {
                                "inbounds": inbounds_config["inbounds"],
                                "outbounds": outbounds['outbounds']
                            }
                            ##print(f"\n{i} ({g}) - {config_url}")
                            send_lbl("Test "+str(i)+"/"+str(count_configs)+" Successful: "+str(g)+" ...") 
                            if(start_xray(config_json, temp_config)):
                                if(test_accessibility()):
                                    ##print(f"  [Connection Success].")
                                    g += 1
                                    bests += config_url + "\n"
                                    with open(best_configs, "a", encoding="utf-8") as f: f.write(config_url + "\n")
                                ##else:
                                    ##print(f"  [FAIL Connection].")
                                stop_xray()
                        else:
                            dbl += 1

            except Exception as e:
                continue

              
    except Exception as e:
        #print(f"\nAn unexpected error occurred: {e}")
        pass
    finally:
        ##print("-> Best Configs Selected.")
        if i > 0:
            final_msg = "Successful: "+str(g)+" | Tested: "+str(i)+" | Total: "+str(count_configs)+" | Double: "+str(dbl)+"."
        stoped_test()
        if start_run:
            reset_test()

        if i > 0:
            send_lbl(final_msg)
        if auto_start:
            #print("Goodbay :)")
            os._exit(0)
            

# ==================================================================================

def is_base64(s):
    """Checks if a string is valid Base64 encoded."""
    if not s or len(s) % 4 != 0:
        return False
    try:
        base64.b64decode(s, validate=True)
        return True
    except binascii.Error:
        return False


# Function to Get links with a timeout
def get_link(link):
    decoded_text = ""
    try:
        response = requests.get(link, timeout=15)
        if response.status_code == 404:
            send_error("Link not found!\n"+link, "Error 404")
        elif is_base64(response.text):
            encoded_bytes = response.content
            decoded_text = decode_b64(encoded_bytes)            
        else:
            decoded_text = response.text

        return decoded_text
    except requests.RequestException:      
        return ""  # If the request fails or times out, skip it

    
    

# ==================================================================================

entries = {}
start_run = True
total_i = 0
g = 0
dbl = 0
check_doble = []
main_url = ""
min_lbl = decode_b64("wqkgbGlNaWwgfCAgRnJlZWRvbSBBY2Nlc3MgSW50ZXJuZXQg")
auto_start = False
xray_process = None

# ==================================================================================
def send_error(error, title="Error"):
    messagebox.showerror(title, error)

def send_lbl(msg):
    entries['msg'].config(text=msg)

def reset_test():
    global total_i, g, dbl, check_doble
    total_i = 0
    g = 0
    dbl = 0
    check_doble = []
    entries['start'].config(text="Start Test", command=start_test, bg="#28a745")
    send_lbl(min_lbl)

def stop_test(): 
    global start_run
    start_run = False
    entries['start'].config(state=tk.DISABLED, bg="#cccccc")
    

def stoped_test():   
    entries['start'].config(state=tk.NORMAL, text="Continue Test", command=start_test, bg="#2830a7")
    entries['rest'].config(state=tk.NORMAL, bg="#a75028")



def start_test():
    global start_run, main_url
    start_run = True
    params_url = entries['url'].get()
    if not main_url == params_url:
        reset_test()
        main_url = params_url

    entries['start'].config(text="Stop",command=stop_test, bg="#a72828")
    entries['rest'].config(state=tk.DISABLED, bg="#cccccc")
    thread = threading.Thread(target=run_test, args=(params_url,))
    thread.start()
    #run_test(params_url)



def open_link(url):
    """Function to open the specified URL."""
    webbrowser.open_new(url)

def open_limilco_v2r():
    open_link("https://limilco.github.io/v2r/")

def gui():
    window = tk.Tk()
    window.title("Auto Configs Founder.")
    window.geometry("450x130")
    window.resizable(False, False)

    form_frame = tk.Frame(window, padx=10, pady=10)
    form_frame.pack(fill="x", expand=True)



    label = tk.Label(form_frame, text="URL:", anchor="w")
    label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
    entry = tk.Entry(form_frame, width=60)
    entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
    entry.insert(0, SRC_CONFIG)
    entries['url'] = entry



    form_frame.grid_columnconfigure(1, weight=1)

    button_frame = tk.Frame(window)
    button_frame.pack(pady=10)

    start_button = tk.Button(button_frame, text="Start Test", command=start_test, bg="#28a745", fg="white", font=("Arial", 10, "bold"), width=20)
    start_button.pack(side="left", padx=5)
    entries['start'] = start_button

    rest_button = tk.Button(button_frame, text="Rest", command=reset_test, bg="#a75028", fg="white", font=("Arial", 10, "bold"), width=7)
    rest_button.pack(side="left", padx=5)
    entries['rest'] = rest_button

    v2r_button = tk.Button(button_frame, text="?", command=open_limilco_v2r, bg="#30b7d9", fg="white", font=("Arial", 10, "bold"), width=3)
    v2r_button.pack(side="left", padx=5)

    slogan_font = font.Font(family="Consolas", size=9, slant="italic")
    limil_label = tk.Label(window, text=min_lbl, font=slogan_font, fg="#222222")
    limil_label.pack(pady=5)
    entries['msg'] = limil_label


    if auto_start:
        start_test()

    window.mainloop()

# ==================================================================================

if __name__ == "__main__":

    if 1 < len(sys.argv) < 3:
        SRC_CONFIG = sys.argv[1]
        auto_start = True
        gui()
    else:
        gui()


