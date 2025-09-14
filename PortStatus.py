import json
import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Luôn dùng file tuyệt đối, cùng thư mục với PortStatus.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PC_FILE = os.path.join(BASE_DIR, "pc_status.json")

class PCStatusManager:
    def __init__(self):
        self.pc_data = {
            "https://597cptb5-2310.asse.devtunnels.ms/process_image": True
        }
        self.ip_to_url = {
            "127.0.0.1": "https://597cptb5-2310.asse.devtunnels.ms/process_image",
            "localhost": "https://597cptb5-2310.asse.devtunnels.ms/process_image"
        }
        self._observers = []
        self._lock = threading.Lock()
        self._file_lock = threading.Lock()

        self._save_to_file()
        self._start_file_watcher()
    
    def _save_to_file(self):
        with self._file_lock:
            with open(PC_FILE, 'w') as f:
                json.dump(self.pc_data, f, indent=2)
    
    def _load_from_file(self):
        if os.path.exists(PC_FILE):
            with self._file_lock:
                try:
                    with open(PC_FILE, 'r') as f:
                        data = json.load(f)
                        return data
                except:
                    return self.pc_data
        return self.pc_data
    
    def _start_file_watcher(self):
        event_handler = PCFileHandler(self)
        observer = Observer()
        observer.schedule(event_handler, BASE_DIR, recursive=False)
        observer.start()
    
    def _notify_observers(self, key, old_value, new_value):
        for observer in self._observers:
            try:
                observer(key, old_value, new_value)
            except Exception as e:
                print(f"Error in observer: {e}")
    
    def add_observer(self, callback_func):
        with self._lock:
            self._observers.append(callback_func)
    
    def set_by_ip(self, ip, value):
        if ip in self.ip_to_url:
            url = self.ip_to_url[ip]
            print(f"[PortStatus] Mapping IP {ip} -> URL {url}")
            self[url] = value
        else:
            print(f"[PortStatus] Warning: IP {ip} not found in mapping")
            print(f"[PortStatus] Available mappings: {list(self.ip_to_url.keys())}")
    
    def add_ip_mapping(self, ip, url):
        self.ip_to_url[ip] = url
        print(f"[PortStatus] Added mapping: {ip} -> {url}")
    
    def __getitem__(self, key):
        return self.pc_data.get(key)
    
    def __setitem__(self, key, value):
        with self._lock:
            old_value = self.pc_data.get(key)
            self.pc_data[key] = value
            self._save_to_file()
            self._notify_observers(key, old_value, value)
    
    def sync_from_file(self):
        new_data = self._load_from_file()
        with self._lock:
            for key, new_value in new_data.items():
                old_value = self.pc_data.get(key)
                if old_value != new_value:
                    self.pc_data[key] = new_value
                    self._notify_observers(key, old_value, new_value)
    
    def keys(self):
        return self.pc_data.keys()
    
    def items(self):
        return self.pc_data.items()
    
    def __repr__(self):
        return repr(self.pc_data)

class PCFileHandler(FileSystemEventHandler):
    def __init__(self, pc_manager):
        self.pc_manager = pc_manager
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith("pc_status.json"):
            time.sleep(0.1)
            print("[PortStatus] File change detected, syncing...")
            self.pc_manager.sync_from_file()

PC = PCStatusManager()
