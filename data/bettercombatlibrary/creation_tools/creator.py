import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os

root = tk.Tk()
root.title("Better Combat JSON Builder")

# Config path and file name
config_path = "data/bettercombatlibrary/creation_tools/config.json"
json_filename = tk.StringVar(value="attribute.json")

# Load config
pose_defaults = {}
attack_defaults = {}
condition_enum = []
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        pose_defaults = config.get("pose", {})
        attack_defaults = config.get("attack", {})
        condition_enum = config.get("condition_enum", [])

attacks = []

category_var = tk.StringVar(value="none")       #default category as "none"
range_bonus_var = tk.IntVar(value=0)            #default range bonus as 0, default player interaction range is 3
pose_var = tk.StringVar()                       # Pose variable for weapon-level pose, initially empty  
two_handed_pose_var = tk.StringVar()            # Two-handed pose variable, initially empty
two_handed_var = tk.BooleanVar(value=False)     # Two-handed flag, default is False
off_hand_pose_var = tk.StringVar()              # Off-hand pose variable, initially empty

# Json file name entry
tk.Label(root, text="JSON File Name:").pack()
tk.Entry(root, textvariable=json_filename, width=50).pack() #first entry, used for file name when saving

# Weapon-level fields

# Pose selection entry
tk.Label(root, text="Pose:").pack()
pose_frame = tk.Frame(root)
pose_frame.pack()
pose_entry = tk.Entry(pose_frame, textvariable=pose_var, width=47) #2nd entry, used for pose selection
pose_entry.pack(side=tk.LEFT) #prepares for a dropdown menu to select pose options

def show_pose_menu():
    menu = tk.Menu(root, tearoff=0)
    for pose_option, metadata in pose_defaults.items():
        menu.add_command(label=pose_option or "<empty>", command=lambda p=pose_option, m=metadata: set_pose(p, m))
    menu.post(pose_entry.winfo_rootx(), pose_entry.winfo_rooty() + pose_entry.winfo_height())

def set_pose(p, metadata=None):
    pose_var.set(p)
    if metadata is None:
        metadata = pose_defaults.get(p, {})
    two_handed_var.set(metadata.get("two_handed", False))

tk.Button(pose_frame, text="▼", width=2, command=show_pose_menu).pack(side=tk.LEFT) # Button to show pose options


# Two handed checkbox
def toggle_two_handed_pose_state(*args):
    state = tk.DISABLED if two_handed_var.get() else tk.NORMAL
    two_handed_pose_entry.config(state=state)
    off_hand_pose_entry.config(state=state)


tk.Checkbutton(root, text="Two Handed", variable=two_handed_var, command=toggle_two_handed_pose_state).pack() #3rd entry, used for two-handed checkbox
two_handed_var.trace_add('write', toggle_two_handed_pose_state) # Trace the two_handed_var to toggle the state of the two_handed_pose_entry

# Two-handed pose selection entry
tk.Label(root, text="Two-Handed Pose:").pack()
two_handed_pose_frame = tk.Frame(root)
two_handed_pose_frame.pack()
two_handed_pose_entry = tk.Entry(two_handed_pose_frame, textvariable=two_handed_pose_var, width=47) #4th entry, used for two-handed pose selection
two_handed_pose_entry.pack(side=tk.LEFT) #prepares for a dropdown menu to select two-handed pose options


def show_two_handed_pose_menu():
    menu = tk.Menu(root, tearoff=0)
    for pose_option in pose_defaults.keys():
        menu.add_command(label=pose_option or "<empty>", command=lambda p=pose_option: two_handed_pose_var.set(p))
    menu.post(two_handed_pose_entry.winfo_rootx(), two_handed_pose_entry.winfo_rooty() + two_handed_pose_entry.winfo_height())

tk.Button(two_handed_pose_frame, text="▼", width=2, command=show_two_handed_pose_menu).pack(side=tk.LEFT) # Button to show two-handed pose options

# Off-hand pose selection entry
tk.Label(root, text="Off-Hand Pose:").pack()
off_hand_pose_frame = tk.Frame(root)
off_hand_pose_frame.pack()
off_hand_pose_entry = tk.Entry(off_hand_pose_frame, textvariable=off_hand_pose_var, width=47) #5th entry, used for off-hand pose selection
off_hand_pose_entry.pack(side=tk.LEFT)

def show_off_hand_pose_menu():
    menu = tk.Menu(root, tearoff=0)
    for pose_option in pose_defaults.keys():
        menu.add_command(label=pose_option or "<empty>", command=lambda p=pose_option: off_hand_pose_var.set(p))
    menu.post(off_hand_pose_entry.winfo_rootx(), off_hand_pose_entry.winfo_rooty() + off_hand_pose_entry.winfo_height())

tk.Button(off_hand_pose_frame, text="▼", width=2, command=show_off_hand_pose_menu).pack(side=tk.LEFT) # Button to show off-hand pose options

toggle_two_handed_pose_state()  # Initial state

# Entries for attack data
fields = {}
def create_entry(label_text, default_value=""):
    tk.Label(root, text=label_text).pack()
    entry = tk.Entry(root, width=50)
    entry.insert(0, default_value)
    entry.pack()
    fields[label_text] = entry

create_entry("Hitbox")

# Grouped entries side by side for Damage Multiplier, Angle, Upswing
trio_frame = tk.Frame(root)
trio_frame.pack()

for label_text, default in [("Damage Multiplier", "1.0"), ("Angle", "0"), ("Upswing", "0.5")]:
    subframe = tk.Frame(trio_frame)
    subframe.pack(side=tk.LEFT, padx=5)
    tk.Label(subframe, text=label_text).pack()
    entry = tk.Entry(subframe, width=15)
    entry.insert(0, default)
    entry.pack()
    fields[label_text] = entry

create_entry("Animation")
create_entry("Swing Sound ID", "bettercombat:sword_slash")


# Bind right-click for Hitbox field to load presets
fields["Hitbox"].bind("<Button-3>", lambda event: show_hitbox_menu(event, fields["Hitbox"]))

def show_hitbox_menu(event, widget):
    menu = tk.Menu(root, tearoff=0)
    for hitbox_type in attack_defaults.keys():
        menu.add_command(label=hitbox_type, command=lambda h=hitbox_type: set_hitbox_from_menu(event,widget, h))
    menu.post(event.x_root, event.y_root)

def set_hitbox_from_menu(event,widget, hitbox):
    widget.delete(0, tk.END)
    widget.insert(0, hitbox)
    #after selection, it will show you the animation menu for that hitbox for the user to select
    show_anim_menu(event, fields["Animation"], hitbox)

# Bind right-click for Animation field to load presets
fields["Animation"].bind("<Button-3>", lambda event: show_anim_menu(event, fields["Animation"]))

def show_anim_menu(event, widget, hitbox=None):
    menu = tk.Menu(root, tearoff=0)
    for hitbox_type, anims in attack_defaults.items():
        if hitbox is None or hitbox == hitbox_type:
            # Only show animations for the selected hitbox type
            if hitbox_type not in attack_defaults:
                continue
            # Add animations for the hitbox type
            for anim in anims.keys():
                menu.add_command(label=anim, command=lambda a=anim, h=hitbox_type: set_anim_from_menu(widget, a, h))
    menu.post(event.x_root, event.y_root)

def set_anim_from_menu(widget, anim, hitbox):
    widget.delete(0, tk.END)
    widget.insert(0, anim)
    #if not fields["Hitbox"].get().strip():
    fields["Hitbox"].delete(0, tk.END)
    fields["Hitbox"].insert(0, hitbox)
    angle = attack_defaults[hitbox][anim].get("angle")
    if angle :#and not fields["Angle"].get().strip():
        fields["Angle"].delete(0, tk.END)
        fields["Angle"].insert(0, str(angle))

# Conditions checklist
tk.Label(root, text="Conditions:").pack()
condition_vars = {}
cond_frame = tk.Frame(root)
cond_frame.pack()
for cond in condition_enum:
    var = tk.BooleanVar()
    cb = tk.Checkbutton(cond_frame, text=cond, variable=var)
    cb.pack(anchor="w")
    condition_vars[cond] = var

# Listbox to show and select attacks
class DraggableListbox(tk.Listbox):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.bind('<Button-1>', self.click)
        self.bind('<B1-Motion>', self.drag)
        self.bind('<ButtonRelease-1>', self.drop)
        self._drag_data = {"item": None, "index": None}

    def click(self, event):
        self._drag_data["index"] = self.nearest(event.y)
        self._drag_data["item"] = self.get(self._drag_data["index"])

    def drag(self, event):
        pass

    def drop(self, event):
        drop_index = self.nearest(event.y)
        if drop_index != self._drag_data["index"]:
            item = self._drag_data["item"]
            self.delete(self._drag_data["index"])
            self.insert(drop_index, item)
            attacks.insert(drop_index, attacks.pop(self._drag_data["index"]))
        self._drag_data = {"item": None, "index": None}

listbox = DraggableListbox(root, width=60, height=10)
listbox.pack()

# Add/Edit/Delete/Load/Save/Update Config

def add_attack():
    try:
        conditions = [c for c, v in condition_vars.items() if v.get()]
        damage_multiplier = float(fields["Damage Multiplier"].get() or 1.0)
        upswing = float(fields["Upswing"].get() or 0.5)
        swing_sound_id = fields["Swing Sound ID"].get() or "bettercombat:sword_slash"
        attack = {
            "hitbox": fields["Hitbox"].get(),
            "conditions": conditions,
            "damage_multiplier": damage_multiplier,
            "angle": int(fields["Angle"].get()),
            "upswing": upswing,
            "animation": fields["Animation"].get(),
            "swing_sound": {"id": swing_sound_id},
            "attack_range_multiplier": 1.0,
            "attack_speed_multiplier": 1.0,
            "movement_speed_multiplier": 1.0,
            "stamina_cost_multiplier": 1.0,
            "damage_type": ""
        }
        attacks.append(attack)
        listbox.insert(tk.END, attack['animation'])
    except Exception as e:
        messagebox.showerror("Error", str(e))

def edit_attack():
    try:
        index = listbox.curselection()
        if not index:
            messagebox.showwarning("No selection", "Select an attack to edit.")
            return
        index = index[0]
        attack = attacks[index]
        fields["Hitbox"].delete(0, tk.END)
        fields["Hitbox"].insert(0, attack.get("hitbox", ""))
        fields["Damage Multiplier"].delete(0, tk.END)
        fields["Damage Multiplier"].insert(0, attack.get("damage_multiplier", 1.0))
        fields["Angle"].delete(0, tk.END)
        fields["Angle"].insert(0, attack.get("angle", 0))
        fields["Upswing"].delete(0, tk.END)
        fields["Upswing"].insert(0, attack.get("upswing", 0.0))
        fields["Animation"].delete(0, tk.END)
        fields["Animation"].insert(0, attack.get("animation", ""))
        fields["Swing Sound ID"].delete(0, tk.END)
        fields["Swing Sound ID"].insert(0, attack.get("swing_sound", {}).get("id", ""))
        for cond in condition_vars:
            condition_vars[cond].set(cond in attack.get("conditions", []))
        listbox.delete(index)
        attacks.pop(index)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def delete_attack():
    index = listbox.curselection()
    if not index:
        messagebox.showwarning("No selection", "Select an attack to delete.")
        return
    index = index[0]
    listbox.delete(index)
    attacks.pop(index)

def save_json():
    data = {
        "attributes": {
            "range_bonus": range_bonus_var.get(),
            "category": category_var.get(),
            "pose": pose_var.get(),
            "two_handed_pose": two_handed_pose_var.get(),
            "two_handed": two_handed_var.get(),
            "attacks": []
        }
    }
    for opt in ["pose", "two_handed_pose"]:
        if not data["attributes"][opt]:
            del data["attributes"][opt]
    if data["attributes"]["two_handed"] == 0:
        del data["attributes"]["two_handed"]
    elif data["attributes"].get("two_handed_pose"):
        del data["attributes"]["two_handed_pose"]
    for atk in attacks:
        filtered = atk.copy()
        for opt in ["damage_multiplier", "attack_range_multiplier", "attack_speed_multiplier", "movement_speed_multiplier", "stamina_cost_multiplier", "damage_type"]:
            if opt in filtered and (filtered[opt] == 1.0 or filtered[opt] == ""):
                del filtered[opt]
        data["attributes"]["attacks"].append(filtered)
    file = filedialog.asksaveasfilename(initialfile=json_filename.get(), defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if file:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Saved", f"Saved to {file}")

def load_json():
    file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            attrs = data.get("attributes", {})
            category_var.set(attrs.get("category", ""))
            range_bonus_var.set(attrs.get("range_bonus", 0))
            pose_var.set(attrs.get("pose", ""))
            two_handed_var.set(attrs.get("two_handed", False))
            attacks.clear()
            listbox.delete(0, tk.END)
            for atk in attrs.get("attacks", []):
                attacks.append(atk)
                listbox.insert(tk.END, atk.get("animation", "<unnamed>"))

def update_config():
    pose = pose_var.get().strip()
    two_handed = two_handed_var.get()
    if pose:
        pose_defaults[pose] = {"two_handed": two_handed}
        anim = fields["Animation"].get()
        hitbox = fields["Hitbox"].get()
        angle = fields["Angle"].get()
        if anim and hitbox and angle:
            if hitbox not in attack_defaults:
                attack_defaults[hitbox] = {}
            attack_defaults[hitbox][anim] = {"angle": int(angle)}
    config_data = {
        "pose": pose_defaults,
        "attack": attack_defaults,
        "condition_enum": condition_enum
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    messagebox.showinfo("Saved", f"Config saved to {config_path}")

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack()
tk.Button(btn_frame, text="Add Attack", command=add_attack).pack(side=tk.LEFT)
tk.Button(btn_frame, text="Edit Selected", command=edit_attack).pack(side=tk.LEFT)
tk.Button(btn_frame, text="Delete Selected", command=delete_attack).pack(side=tk.LEFT)
tk.Button(btn_frame, text="Save JSON", command=save_json).pack(side=tk.LEFT)
tk.Button(btn_frame, text="Update Config", command=update_config).pack(side=tk.LEFT)
tk.Button(btn_frame, text="Load JSON", command=load_json).pack(side=tk.LEFT)

root.mainloop()
