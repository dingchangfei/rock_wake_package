#!/usr/bin/env python3
"""
listen_rock.py

- 使用 pvporcupine 离线唤醒词 (.ppn)
- 支持多个关键词文件（KEYWORD_FILES）
- 仅在检测到耳机时启动（可用 --no-headphone-check 覆盖）
- 触发动作：全屏短闪、系统通知、可选智能灯控制（yeelight）
- 运行前请设置环境变量 PV_ACCESS_KEY
"""
import os
import sys
import time
import subprocess
import argparse
import struct
from pathlib import Path

# Optional imports
try:
    import pvporcupine
except Exception:
    print("Missing pvporcupine. Install: pip3 install pvporcupine")
    raise

try:
    import pyaudio
except Exception:
    print("Missing pyaudio. On mac: brew install portaudio; pip3 install pyaudio")
    raise

# macOS notification (pyobjc)
try:
    from Foundation import NSUserNotification, NSUserNotificationCenter
except Exception:
    NSUserNotification = None

ACCESS_KEY = os.environ.get("PV_ACCESS_KEY", "")
KEYWORD_FILES = ["rock.ppn"]
MODEL_PATH = os.environ.get("PV_MODEL_PATH", "porcupine_params_zh.pv")
SENSITIVITY = float(os.environ.get("PV_SENSITIVITY", "0.8"))
FRAME_WAIT_SECONDS = 0.01
FLASH_COLOR = "#FF0000"
FLASH_DURATION = 0.15
LIGHT_CONFIG = "light_config.json"

def is_headphone_connected():
    try:
        out = subprocess.check_output(["SwitchAudioSource", "-c"], stderr=subprocess.DEVNULL).decode()
        out = out.strip().lower()
        if not out:
            return False
        return any(k in out for k in ("headphones", "airpods", "耳机"))
    except Exception:
        try:
            out = subprocess.check_output(["system_profiler", "SPBluetoothDataType"], stderr=subprocess.DEVNULL).decode()
            return "connected: yes" in out.lower()
        except Exception:
            return False

def flash_screen(color=FLASH_COLOR, duration=FLASH_DURATION):
    try:
        subprocess.Popen(
            ["say", "-v", "Ting-Ting", "Rock 有人在叫你"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass
    
    try:
        print("\n" + "=" * 50)
        print("🔴 Rock 有人在叫你！")
        print(time.strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 50 + "\n")
    except Exception:
        pass
    
    try:
        script = 'display dialog "🔴 检测到唤醒词！" buttons {"确定"} default button "确定" with title "Hey Rock" giving up after 3'
        subprocess.Popen(
            ["osascript", "-e", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass
    
    try:
        flash_script = f'''
import tkinter as tk
import sys

color = "{color}"
duration = {duration}

root = tk.Tk()
root.overrideredirect(True)
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.configure(bg=color)
root.focus_set()

def close_window():
    root.destroy()
    root.quit()

root.after(int(duration * 1000), close_window)
root.mainloop()
'''
        subprocess.Popen(
            [sys.executable, "-c", flash_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def send_notification(title="Hey", message="Someone called your name."):
    title_escaped = title.replace('\\', '\\\\').replace('"', '\\"')
    message_escaped = message.replace('\\', '\\\\').replace('"', '\\"')
    
    try:
        if NSUserNotification is not None:
            notification = NSUserNotification.alloc().init()
            notification.setTitle_(title)
            notification.setInformativeText_(message)
            notification.setSoundName_("Glass")
            notification.setUserInfo_({"source": "rock_wake"})
            NSUserNotificationCenter.defaultUserNotificationCenter().deliverNotification_(notification)
            return True
    except Exception:
        pass
    
    scripts = [
        f'display notification "{message_escaped}" with title "{title_escaped}" sound name "Glass"',
        f'display notification "{message_escaped}" with title "{title_escaped}"',
        f'tell application "System Events" to display notification "{message_escaped}" with title "{title_escaped}"',
    ]
    
    for script in scripts:
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=3,
                check=False
            )
            if result.returncode == 0:
                return True
        except Exception:
            continue
    
    try:
        subprocess.Popen(
            ["say", "-v", "Ting-Ting", f"{title}: {message}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass
    
    return False

def play_sound(sound_name="Glass"):
    try:
        sound_paths = [
            f"/System/Library/Sounds/{sound_name}.aiff",
            "/System/Library/Sounds/Glass.aiff",
            "/System/Library/Sounds/Basso.aiff",
        ]
        for path in sound_paths:
            if os.path.exists(path):
                subprocess.Popen(["afplay", path], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
        subprocess.Popen(["say", "-v", "Ting-Ting", "ding"], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def trigger_external_light():
    try:
        import json
        from yeelight import Bulb
    except Exception:
        return False

    cfg_path = Path(LIGHT_CONFIG)
    if not cfg_path.exists():
        return False
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        ip = cfg.get("ip")
        if not ip:
            return False
        b = Bulb(ip)
        b.turn_on()
        b.set_power_mode("normal")
        b.set_brightness(100)
        b.toggle()
        time.sleep(0.2)
        b.toggle()
        return True
    except Exception:
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-headphone-check", action="store_true", help="Disable headphone check (always active)")
    parser.add_argument("--keywords", nargs="+", help="List .ppn files to use", default=KEYWORD_FILES)
    parser.add_argument("--sensitivity", type=float, default=SENSITIVITY, 
                       help=f"Sensitivity for keyword detection [0, 1], higher = more sensitive (default: {SENSITIVITY})")
    parser.add_argument("--check-interval", type=float, default=2.0, 
                       help="Headphone check interval in seconds (default: 2.0)")
    args = parser.parse_args()
    
    if args.sensitivity < 0 or args.sensitivity > 1:
        args.sensitivity = max(0.0, min(1.0, args.sensitivity))

    if not ACCESS_KEY:
        print("ERROR: Picovoice ACCESS_KEY not found. Set PV_ACCESS_KEY environment variable.")
        print("Example: export PV_ACCESS_KEY='YOUR_KEY_HERE'")
        sys.exit(2)

    base = Path(__file__).parent.resolve()
    keyword_paths = []
    for k in args.keywords:
        p = (base / k)
        if not p.exists():
            print(f"Missing keyword file: {p}")
            sys.exit(3)
        keyword_paths.append(str(p))

    print("Starting Porcupine with keywords:", keyword_paths)
    print(f"Sensitivity: {args.sensitivity} (range: 0.0-1.0, higher = more sensitive)")
    try:
        create_kwargs = {
            "access_key": ACCESS_KEY, 
            "keyword_paths": keyword_paths,
            "sensitivities": [args.sensitivity] * len(keyword_paths)
        }
        if MODEL_PATH:
            model_path_obj = Path(MODEL_PATH)
            if not model_path_obj.is_absolute():
                model_path_obj = base / MODEL_PATH
            if model_path_obj.exists():
                create_kwargs["model_path"] = str(model_path_obj)
                print(f"Using custom model: {model_path_obj}")
        porcupine = pvporcupine.create(**create_kwargs)
    except Exception as e:
        error_msg = str(e)
        if "language" in error_msg.lower() or "belong to the same language" in error_msg:
            print("ERROR: Language mismatch detected!")
            sys.exit(4)
        else:
            print(f"ERROR: Failed to create Porcupine instance: {e}")
            raise

    audio = pyaudio.PyAudio()
    stream = None
    is_active = False
    last_check_time = 0
    
    print("Program started. Waiting for headphones... (Press Ctrl+C to stop)")
    if args.no_headphone_check:
        print("Headphone check disabled - always active")
        is_active = True
        stream = audio.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
            input_device_index=None
        )

    try:
        while True:
            current_time = time.time()
            
            if not args.no_headphone_check:
                if current_time - last_check_time >= args.check_interval:
                    headphone_connected = is_headphone_connected()
                    last_check_time = current_time
                    
                    if headphone_connected and not is_active:
                        print("Headphones detected. Starting listener...")
                        is_active = True
                        if stream is None:
                            stream = audio.open(
                                rate=porcupine.sample_rate,
                                channels=1,
                                format=pyaudio.paInt16,
                                input=True,
                                frames_per_buffer=porcupine.frame_length,
                                input_device_index=None
                            )
                    elif not headphone_connected and is_active:
                        print("Headphones disconnected. Pausing listener...")
                        is_active = False
                        if stream is not None:
                            stream.stop_stream()
                            stream.close()
                            stream = None
            
            if is_active and stream is not None:
                try:
                    pcm_bytes = stream.read(porcupine.frame_length, exception_on_overflow=False)
                    pcm = struct.unpack('<' + 'h' * porcupine.frame_length, pcm_bytes)
                    result = porcupine.process(pcm)
                    if result >= 0:
                        send_notification("Hey Rock", "检测到唤醒词！")
                        play_sound("Glass")
                        flash_screen()
                        trigger_external_light()
                        time.sleep(1.0)
                except Exception:
                    pass
            else:
                time.sleep(args.check_interval)
                
    except KeyboardInterrupt:
        print("Stopping listener...")
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        audio.terminate()
        porcupine.delete()

if __name__ == "__main__":
    main()
