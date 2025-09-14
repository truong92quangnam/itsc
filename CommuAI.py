import requests
import time
import os
import PortStatus

def on_pc_change_commu(key, old_value, new_value):
    print(f"[CommuAI] PC[{key}] changed: {old_value} -> {new_value}")
    if new_value:
        print(f"[CommuAI] {key} is now available for processing!")

PortStatus.PC.add_observer(on_pc_change_commu)

def Post_image_to_AI(filename, API):
    try:
        with open(filename, 'rb') as f:
            response = requests.post(API, files={'file': f})
        if response.status_code == 200:
            print("[CommuAI] Image posted successfully:", response.json())
        else:
            print(f"[CommuAI] Failed to post image. Status {response.status_code}")
    except Exception as e:
        print(f"[CommuAI] Error posting image: {e}")

def main_loop():
    folder = 'Undatabase/AIrequest'
    os.makedirs(folder, exist_ok=True)
    
    while True:
        time.sleep(5)
        for unit in list(PortStatus.PC.pc_data.keys()):
            if PortStatus.PC[unit]:
                files = os.listdir(folder) if os.path.exists(folder) else []
                if not files:
                    print("[CommuAI] Folder empty, retry in 5s")
                    continue
                
                file = files[0]
                filename = os.path.join(folder, file)
                 # reset trạng thái
                PortStatus.PC[unit] = False
                Post_image_to_AI(filename, unit)
                if os.path.exists(filename):
                    os.remove(filename)
                
        print(f"[CommuAI] Current PC status: {PortStatus.PC}")

if __name__ == "__main__":
    print("[CommuAI] Starting...")
    main_loop()
