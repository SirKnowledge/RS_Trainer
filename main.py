import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import os
import requests
import webbrowser
import json
from order_key_binds import reorder_keybinds_json
import rs_trainer
import config
from key_binds import triggerkeybinds


# ----------------- Config -----------------
CURRENT_VERSION = "1.1.1"
VERSION_URL = "https://raw.githubusercontent.com/blueboy4g/RS_Trainer/main/version.json"

os.makedirs(config.APPDATA_DIR, exist_ok=True)

last_boss_selected_save = os.path.join(config.APPDATA_DIR, "last_boss_selected.txt")
last_rotation_selected_save = os.path.join(
    config.APPDATA_DIR, "last_rotation_selected.txt"
)
KEYBINDS_FILE = os.path.join(config.APPDATA_DIR, "keybinds.json")
CONFIG_FILE = os.path.join(config.APPDATA_DIR, "config.json")
BUILD_ROTATION_FILE = os.path.join(config.APPDATA_DIR, "build_rotation.txt")
# DEFAULT_BUILD_ROTATION_FILE = os.path.join("conf"build_rotation.txt")


APPDATA_BOSS_DIR = os.path.join(config.APPDATA_DIR, "boss_rotations")
# SOURCE_BOSS_DIR = Path("boss_rotations")
# APPDATA_BOSS_DIR.mkdir(parents=True, exist_ok=True)

BOSS_FILE = os.path.join(APPDATA_BOSS_DIR, "azulyn_telos_2499_necro.json")
# TODO: This should pick up last saved boss file

ICON_PATH = "Resources/azulyn_icon.ico"
# ------------------------------------------

with open(KEYBINDS_FILE, "r", encoding="utf-8") as f:
    print("Loading default keybinds from: ", KEYBINDS_FILE)
    default_keybinds: dict[str, dict[str, list[str]]] = json.load(f)

# Check for missing keys under "ABILITY_KEYBINDS" in USER_KEYBINDS
missing_keybinds = {
    key: value
    for key, value in default_keybinds["ABILITY_KEYBINDS"].items()
    if key not in config.keybind_config["ABILITY_KEYBINDS"]
}

if missing_keybinds:
    # Add missing keys to "ABILITY_KEYBINDS"
    config.keybind_config["ABILITY_KEYBINDS"].update(missing_keybinds)

    # Save the updated user keybinds without reformatting other entries
    with open(config.USER_KEYBINDS, "w", encoding="utf-8") as f:
        json.dump(config.keybind_config, f, indent=4, separators=(",", ": "))
    print(f"Added missing keybinds under 'ABILITY_KEYBINDS': {missing_keybinds}")
else:
    print("All keybinds under 'ABILITY_KEYBINDS' are already present.")

# if not os.path.exists(BUILD_ROTATION_FILE):
#     if os.path.exists(DEFAULT_BUILD_ROTATION_FILE):
#         shutil.copy(DEFAULT_BUILD_ROTATION_FILE, BUILD_ROTATION_FILE)

# for file in SOURCE_BOSS_DIR.glob("*.json"):
#     target = APPDATA_BOSS_DIR / file.name
#     if not target.exists():
#         shutil.copy(file, target)


def check_for_update():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        data = response.json()
        latest_version = data["version"]
        download_url = data["download_url"]
        notes = data.get("notes", "")
        if latest_version != CURRENT_VERSION:
            if messagebox.askyesno(
                "Update Available",
                f"New version {latest_version} available:\n\n{notes}\n\nDownload now?",
            ):
                webbrowser.open(download_url)
        else:
            messagebox.showinfo(
                "No Update", f"You're running the latest version ({CURRENT_VERSION})"
            )
    except Exception as e:
        messagebox.showerror("Update Check Failed", str(e))


def load_last_used_boss():
    if os.path.exists(last_boss_selected_save):
        with open(last_boss_selected_save, "r") as f:
            return f.read().strip()
    else:
        return BOSS_FILE


def load_last_pvm_rot():
    if os.path.exists(last_rotation_selected_save):
        with open(last_rotation_selected_save, "r") as f:
            return f.read().strip()
    return BUILD_ROTATION_FILE


def save_current_config():
    with open(last_boss_selected_save, "w") as f:
        f.write(last_used_boss.get())


def open_file_editor(filepath):
    if not os.path.isfile(filepath):
        messagebox.showerror("Error", f"File not found: {filepath}")
        return
    subprocess.Popen([get_default_editor(), filepath])
    # TODO: Use default based on file extension


def get_default_editor():
    return os.environ.get("EDITOR", "notepad")


def browse_rotation_file():
    file_path = filedialog.askopenfilename(
        initialdir=str(APPDATA_BOSS_DIR),
        title="Select Rotation File",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
    )
    if file_path:
        last_used_boss.set(file_path)
        last_used_boss_trimmed.set(
            os.path.splitext(os.path.split(last_used_boss.get())[1])[0]
        )
        save_current_config()


def open_donation():
    webbrowser.open("https://buymeacoffee.com/azulyn")


def open_discord():
    webbrowser.open("https://discord.gg/Sp7Sh52B")


def open_rotation():
    webbrowser.open("https://blueboy4g.github.io/RS_Rotation_Creator/")


def open_youtube():
    webbrowser.open("https://www.youtube.com/@Azulyn1")


def start_overlay():
    root.withdraw()
    rs_trainer.triggerrstrainer()
    root.deiconify()


# --------------- UI Setup ----------------
reorder_keybinds_json()
root = tk.Tk()
root.title("RuneScape Trainer")
root.geometry("450x220")
root.iconbitmap(ICON_PATH)

# Dark button styling
style = ttk.Style()
style.theme_use("default")
style.configure("Dark.TButton", foreground="white", background="#444", padding=6)
style.map("Dark.TButton", background=[("active", "#555")])

last_used_boss = tk.StringVar(value=load_last_used_boss())
last_used_pvm_rot = tk.StringVar(value=load_last_pvm_rot())


ascii_title = r"""
   _____               .__                
  /  _  \ __________ __|  | ___.__. ____  
 /  /_\  \\___   /  |  \  |<   |  |/    \ 
/    |    \/    /|  |  /  |_\___  |   |  \
\____|__  /_____ \____/|____/ ____|___|  /
        \/      \/          \/         \/ 
"""

# Layout Frames
top_frame = tk.Frame(root)
top_frame.pack(pady=5, fill="x")

left = tk.Frame(top_frame)
right = tk.Frame(top_frame)
left.pack(side="left", padx=5, expand=True, fill="both")
right.pack(side="right", padx=5, expand=True, fill="both")

log_frame = tk.Frame(root)
log_frame.pack(pady=0, fill="both")

bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=(5, 0))

footer = tk.Frame(root)
footer.pack(side="right", pady=(10, 0))

ttk.Button(
    left,
    text="Start RS Overlay",
    style="Gray.TButton",
    command=lambda: start_overlay(),
).pack(pady=2, fill="x")
ttk.Button(
    left,
    text="Edit Keybinds",
    style="Gray.TButton",
    command=lambda: triggerkeybinds(),
).pack(pady=2, fill="x")

tk.Label(log_frame, text="Current Boss:").pack(pady=(0, 2))

last_used_boss_trimmed = tk.StringVar(
    value=os.path.splitext(os.path.split(last_used_boss.get())[1])[0]
)

tk.Entry(log_frame, textvariable=last_used_boss_trimmed, width=40).pack()
# TODO: Change above entry to a list dialog, loading all boss rotation files
ttk.Button(
    log_frame,
    text="Select Boss Script",
    style="Gray.TButton",
    command=browse_rotation_file,
).pack(pady=10, padx=30, fill="x")

ttk.Button(
    right,
    text="Start RS Trainer",
    style="Gray.TButton",
    command=lambda: start_overlay(),
).pack(pady=2, fill="x")
ttk.Button(
    right,
    text="Edit Config",
    style="Gray.TButton",
    command=lambda: open_file_editor(CONFIG_FILE),
).pack(pady=2, fill="x")

ttk.Button(
    bottom_frame,
    text="Check for Updates",
    style="Gray.TButton",
    command=check_for_update,
).pack(side="left", padx=5, pady=1)
ttk.Button(
    bottom_frame, text="Youtube", style="Gray.TButton", command=open_youtube
).pack(side="left", padx=5, pady=1)
ttk.Button(
    bottom_frame, text="Discord", style="Gray.TButton", command=open_discord
).pack(side="left", padx=5, pady=1)
ttk.Button(
    bottom_frame, text="Build a Rotation", style="Gray.TButton", command=open_rotation
).pack(side="left", padx=5, pady=1)
ttk.Button(
    bottom_frame, text="Donate", style="Gray.TButton", command=open_donation
).pack(side="left", padx=5, pady=1)

# tk.Label(q
#     footer,
#     text=ascii_title,
#     font=("Courier", 3),
#     justify="right",
#     anchor="w",
#     foreground="blue",
# ).pack(side="left", padx=5, pady=0)

tk.Label(footer, font=("Courier", 8), text=f"Current Version: {CURRENT_VERSION}").pack(
    side="right", padx=5, pady=0
)

root.protocol("WM_DELETE_WINDOW", root.destroy)

root.mainloop()
