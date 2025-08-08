import pybase64
import base64
import requests
import binascii
import os
import random

# Define a fixed timeout for HTTP requests
TIMEOUT = 15  # seconds
# Define Source links of Sub 
sources_links = "sources.txt"
# Define the fixed text for the initial configuration
fixed_text = """#profile-title: base64:8J+OgSBGcmVlIEludGVybmV0
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/liMilCo/v2r
#profile-web-page-url: https://limilco.github.io/v2r/
"""

def get_links(file_path):
    try:
        with open(file_path, 'r') as file:
            lines_list = file.readlines()

        lines_list = [line.strip() for line in lines_list]
        lines_list = [line for line in lines_list if not line.startswith('#')]

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        lines_list = []
    except Exception as e:
        print(f"An error occurred: {e}")
        lines_list = []

    return lines_list    


# Disable link from sources
def disable_link(link):
    try:

        sources_filename = os.path.join(os.path.dirname(__file__), sources_links)
        with open(sources_filename, 'r') as file:  # Open for reading
            file_contents = file.read()
        
        updated_contents = file_contents.replace(link, "#"+link)

        with open(sources_filename, 'w') as file:  # Open for writing (overwrites existing content)
            file.write(updated_contents)

        print(f'URL {link} disabeld in {sources_filename}')
    except FileNotFoundError:
        print(f"Error: File '{sources_filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Base64 decoding function
def decode_base64(encoded):
    decoded = ""
    for encoding in ["utf-8", "iso-8859-1"]:
        try:
            decoded = pybase64.b64decode(encoded + b"=" * (-len(encoded) % 4)).decode(encoding)
            break
        except (UnicodeDecodeError, binascii.Error):
            pass
    return decoded

# Function to Get links with a timeout
def decode_links(links):
    decoded_data = []
    for link in links:
        try:
            response = requests.get(link, timeout=TIMEOUT)
            if response.status_code == 404:
                print(f"*****   Error 404:'{link}'  *****")
                disable_link(link)
            elif "://" in response.text:
                decoded_text = response.text
                decoded_data.append(decoded_text)
            else:
                encoded_bytes = response.content
                decoded_text = decode_base64(encoded_bytes)
                decoded_data.append(decoded_text)
            decoded_num_lines = decoded_text.count('\n') + 1
            print(f"Loaded {decoded_num_lines} configs from ({link}).")
        except requests.RequestException:
            pass  # If the request fails or times out, skip it
    return decoded_data

# Filter function to select lines based on specified protocols and remove duplicates (only for config lines)
def filter_for_protocols(data, protocols, old_config):
    filtered_data = []
    filtered_data1 = []
    filtered_data2 = []
    seen_configs = set()
    
    # Process each decoded content
    for content in data:
        if content and content.strip():  # Skip empty content
            lines = content.strip().split('\n')
            for line in lines:
                line = line.strip()
                if any(protocol in line for protocol in protocols):
                    if line.startswith('vmess://'):
                        check_seen = line
                    else:
                        check_seen = line.split('#')[0].split('?')[0]                       
                    if check_seen not in seen_configs:
                        seen_configs.add(check_seen)
                        if line in old_config:
                            filtered_data2.append(line)
                        else:
                            filtered_data1.append(line)
    random.shuffle(filtered_data2)
    filtered_data = filtered_data1 + ["#  ======= The Old Configs ====================="] + filtered_data2
    return filtered_data



# Create necessary directories if they don't exist
def ensure_directories_exist():
    output_folder = os.path.join(os.path.dirname(__file__), "..")
    base64_folder = os.path.join(output_folder, "base64")
    sub_folder = os.path.join(output_folder, "sub")


    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    if not os.path.exists(base64_folder):
        os.makedirs(base64_folder)
    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)

    return output_folder, base64_folder, sub_folder

# Main function to process links and write output files
def main():
    output_folder, base64_folder, sub_folder = ensure_directories_exist()  # Ensure directories are created

    # All_Configs_Sub file name
    output_filename = os.path.join(output_folder, "all_configs.txt")
    main_base64_filename = os.path.join(output_folder, "configs.txt")
    sources_filename = os.path.join(output_folder, "@/"+sources_links)
    
    # Cach Old Configs ...
    print("Load Old Configs ...")
    if os.path.exists(output_filename):
        with open(output_filename, "r", encoding="utf-8") as f:
            old_config_data = f.read()
    else:
            old_config_data = ""

    # Clean existing output files FIRST before processing
    print("Cleaning existing files...")

    if os.path.exists(output_filename):
        os.remove(output_filename)
        print(f"Removed: {output_filename}")
    if os.path.exists(main_base64_filename):
        os.remove(main_base64_filename)
        print(f"Removed: {main_base64_filename}")

    for i in range(1, 99):  # Clean Sub1.txt to Sub99.txt
        filename = os.path.join(sub_folder, f"{i}.txt")
        if os.path.exists(filename):
            os.remove(filename)
            print(f"Removed: {filename}")
        filename_base64 = os.path.join(base64_folder, f"{i}.txt")
        if os.path.exists(filename_base64):
            os.remove(filename_base64)
            print(f"Removed: {filename_base64}")

    print("Starting to fetch and process configs...")
    
    protocols = ["vmess", "vless", "trojan", "ss", "ssr", "hy2", "hysteria2", "tuic", "warp://"]
    

    print("Get Sources Links ...")
    links = get_links(sources_filename)

    print("Fetching configs...")
    decoded_links = decode_links(links)
    print(f"Decoded {len(decoded_links)} sources")
    

    print("Filtering configs...")
    merged_configs = filter_for_protocols(decoded_links, protocols, old_config_data)
    print(f"Found {len(merged_configs)} unique configs after filtering")

    # Write merged configs to output file
    print("Writing main config file...")
    output_filename = os.path.join(output_folder, "all_configs.txt")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(fixed_text)
        for config in merged_configs:
            f.write(config + "\n")
    print(f"Main config file created: {output_filename}")

    # Create base64 version of the main file
    print("Creating base64 version...")
    with open(output_filename, "r", encoding="utf-8") as f:
        main_config_data = f.read()
    
    main_base64_filename = os.path.join(output_folder, "configs.txt")
    with open(main_base64_filename, "w", encoding="utf-8") as f:
        encoded_main_config = base64.b64encode(main_config_data.encode()).decode()
        f.write(encoded_main_config)
    print(f"Base64 config file created: {main_base64_filename}")

    # Split merged configs into smaller files (no more than 500 configs per file)
    print("Creating split files...")
    with open(output_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    num_lines = len(lines)
    max_lines_per_file = 500
    num_files = (num_lines + max_lines_per_file - 1) // max_lines_per_file
    print(f"Splitting into {num_files} files with max {max_lines_per_file} lines each")
    index_html = ""
    for i in range(num_files):
        profile_title = f"🎁 Free Proxy | Sub {i+1} 🌎"
        encoded_title = base64.b64encode(profile_title.encode()).decode()
        custom_fixed_text = f"""#profile-title: base64:{encoded_title}
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/liMilCo/v2r
#profile-web-page-url: https://limilco.github.io/v2r/
"""
        index_html += f"""<p>Sub{i+1}: <a href="https://limilco.github.io/v2r/sub/{i+1}.txt">https://limilco.github.io/v2r/sub/{i+1}.txt</a><br><br>
<img width="200" height="200" alt="frame" src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://limilco.github.io/v2r/base64/{i+1}.txt" />
</p>
<hr>
"""

        input_filename = os.path.join(sub_folder, f"{i + 1}.txt")
        with open(input_filename, "w", encoding="utf-8") as f:
            f.write(custom_fixed_text)
            start_index = i * max_lines_per_file
            if i == 0:
                start_index = 5
            end_index = min((i + 1) * max_lines_per_file, num_lines)
            for line in lines[start_index:end_index]:
                f.write(line)
        print(f"Created: sub/{i + 1}.txt")

        with open(input_filename, "r", encoding="utf-8") as input_file:
            config_data = input_file.read()
        
        base64_output_filename = os.path.join(base64_folder, f"{i + 1}.txt")
        with open(base64_output_filename, "w", encoding="utf-8") as output_file:
            encoded_config = base64.b64encode(config_data.encode()).decode()
            output_file.write(encoded_config)
        print(f"Created: base64/{i + 1}.txt")

    index_html_filename = os.path.join(sub_folder, "index.html")
    with open(index_html_filename, "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"\nProcess completed successfully!")
    print(f"Total configs processed: {len(merged_configs)}")
    print(f"Files created:")
    print(f"  - all_configs.txt")
    print(f"  - configs.txt (Coded)") 
    print(f"  - {num_files} split files (Sub 1.txt to {num_files}.txt)")
    print(f"Update Completed.")

if __name__ == "__main__":
    main()
