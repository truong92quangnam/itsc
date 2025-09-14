from flask import Flask, request, jsonify
import os
import PortStatus
import threading
import time

app = Flask(__name__)

def on_pc_change_server(key, old_value, new_value):
    print(f"[ServerForAI] PC[{key}] changed: {old_value} -> {new_value}")
    if new_value:
        print(f"[ServerForAI] New image ready for processing: {key}")
    else:
        print(f"[ServerForAI] {key} finished processing")

PortStatus.PC.add_observer(on_pc_change_server)

UPLOAD_FOLDER = 'Undatabase/AIService'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    IP = request.form.get('IP')
    if not file.filename:
        return jsonify({"error": "No selected file"}), 400
    
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    print(f"[ServerForAI] Saved file: {filepath}")
    PortStatus.PC[IP] = True
    if IP in PortStatus.PC.pc_data:
          # ✅ dùng __setitem__
        print(f"[ServerForAI] Updated PC[{IP}] = True")
    else:
        print(f"[ServerForAI] ERROR: Unknown IP {IP}")
    
    return jsonify({
        "message": "File uploaded successfully", 
        "filename": file.filename,
        "ip_received": IP
    }), 200

def status_monitor():
    while True:
        time.sleep(10)
        print(f"[ServerForAI] Current PC status: {PortStatus.PC}")

if __name__ == '__main__':
    print("[ServerForAI] Starting...")
    print(f"[ServerForAI] Initial PC status: {PortStatus.PC}")
    
    monitor_thread = threading.Thread(target=status_monitor, daemon=True)
    monitor_thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
