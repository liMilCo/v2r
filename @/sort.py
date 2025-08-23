import requests
import os
import base64

# Define the fixed text for the initial configuration
fixed_text = """#profile-title: base64:8J+OgSBGcmVlIFByb3h5
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/liMilCo/V2ray-config
#profile-web-page-url: https://github.com/liMilCo/V2ray-config
"""


output_folder = os.path.join(os.path.dirname(__file__), "..")
pro_folder = os.path.join(output_folder, "pro")
if not os.path.exists(pro_folder):
    os.makedirs(pro_folder)


vmess_file = os.path.join(pro_folder, 'vmess.txt')
vless_file = os.path.join(pro_folder, 'vless.txt')
trojan_file = os.path.join(pro_folder, 'trojan.txt')
ss_file = os.path.join(pro_folder, 'ss.txt')
ssr_file = os.path.join(pro_folder, 'ssr.txt')
hysteria_file = os.path.join(pro_folder, 'hysteria.txt')

open(vmess_file, "w").close()
open(vless_file, "w").close()
open(trojan_file, "w").close()
open(ss_file, "w").close()
open(ssr_file, "w").close()
open(hysteria_file, "w").close()

print(f"\nAll Splitted Protocol Files Restarted.")

vmess = ""
vless = ""
trojan = ""
ss = ""
ssr = ""
hysteria = ""

# Read from local all_configs.txt file instead of GitHub
local_config_file = os.path.join(output_folder, 'all_configs.txt')
if os.path.exists(local_config_file):
    with open(local_config_file, 'r', encoding='utf-8') as f:
        response_text = f.read()
else:
    # Fallback to GitHub if local file doesn't exist
    response_text = requests.get("https://raw.githubusercontent.com/liMilCo/v2r/main/all_configs.txt").text

for config in response_text.splitlines():
    if config.startswith("vmess"):
        vmess += config + "\n"     
    elif config.startswith("vless"):
        vless += config + "\n"  
    elif config.startswith("trojan"):
        trojan += config + "\n"   
    elif config.startswith("ssr"):  # Check ssr first before ss
        ssr += config + "\n"
    elif config.startswith("ss"):   
        ss += config + "\n"
    elif config.startswith("hysteria"):   
        hysteria += config + "\n"
         
# Write all protocol files with headers
with open(vmess_file, "w", encoding="utf-8") as f:
    f.write(fixed_text + vmess)
with open(vless_file, "w", encoding="utf-8") as f:
    f.write(fixed_text + vless)
with open(trojan_file, "w", encoding="utf-8") as f:
    f.write(fixed_text + trojan)
with open(ss_file, "w", encoding="utf-8") as f:
    f.write(fixed_text + ss)
with open(ssr_file, "w", encoding="utf-8") as f:
    f.write(fixed_text + ssr)  
with open(hysteria_file, "w", encoding="utf-8") as f:
    f.write(fixed_text + hysteria)

print(f"\nProtocols:  Vless, Vmess, Trojan, ss, ssr & Hysteria Created.")

