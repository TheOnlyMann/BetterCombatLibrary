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
sound_ids = []
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        pose_defaults = config.get("pose", {})
        attack_defaults = config.get("attack", {})
        condition_enum = config.get("condition_enum", [])
        sound_ids = config.get("sound_id", [])

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
    for handed_type in ["one_handed","two_handed"]:
        if handed_type in pose_defaults:
            prefix = "[2H]" if handed_type == "two_handed" else "[1H]"
            for pose_option in pose_defaults[handed_type]:
                label = f"{prefix} {pose_option or '<empty>'}"
                menu.add_command(label=label, command=lambda p=pose_option, h=handed_type: set_pose(p, h == "two_handed"))
    menu.post(pose_entry.winfo_rootx(), pose_entry.winfo_rooty() + pose_entry.winfo_height())

def set_pose(p, is_two_handed=None):
    pose_var.set(p)
    if is_two_handed is not None:
        two_handed_var.set(is_two_handed)
    else:
        # Determine from grouped pose_defaults
        for handedness, poses in pose_defaults.items():
            if p in poses:
                two_handed_var.set(handedness == "two_handed")
                break

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
    for handed_type in ["one_handed","two_handed"]:
        if handed_type in pose_defaults:
            prefix = "[2H]" if handed_type == "two_handed" else "[1H]"
            for pose_option in pose_defaults[handed_type]:
                label = f"{prefix} {pose_option or '<empty>'}"
                menu.add_command(label=label, command=lambda p=pose_option: two_handed_pose_var.set(p))
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
    for handed_type in ["one_handed","two_handed"]:
        if handed_type in pose_defaults:
            if handed_type == "two_handed":
                continue  # Skip two-handed poses for off-hand
            for pose_option in pose_defaults[handed_type]:
                label = pose_option or "<empty>"
                menu.add_command(label=label, command=lambda p=pose_option: off_hand_pose_var.set(p))
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

create_entry("Hitbox") # 6th entry, used for hitbox selection

# Grouped entries side by side for Damage Multiplier, Angle, Upswing
trio_frame = tk.Frame(root)
trio_frame.pack()

def make_adjust_button(entry_ref, delta):
    def adjust():
        try:
            current = float(entry_ref.get() or 0)
            new_value = max(0.0, round(current + delta, 2))
            entry_ref.delete(0, tk.END)
            entry_ref.insert(0, f"{new_value:.2f}")
        except ValueError:
            pass
    return adjust

def make_adjust_button_int(entry_ref, delta):
    def adjust():
        try:
            current = int(entry_ref.get() or 0)
            new_value = max(0,current + delta)
            entry_ref.delete(0, tk.END)
            entry_ref.insert(0, str(new_value))
        except ValueError:
            pass
    return adjust

for label_text, default in [("Damage Multiplier", "1.0"), ("Angle", "0"), ("Upswing", "0.5")]:
    subframe = tk.Frame(trio_frame)
    subframe.pack(side=tk.LEFT, padx=5)
    tk.Label(subframe, text=label_text).pack()
    entry = tk.Entry(subframe, width=10)
    entry.insert(0, default)
    entry.pack(side=tk.LEFT, padx=2)
    fields[label_text] = entry
    # Add +/- buttons for Damage Multiplier and Angle
    if label_text == "Angle":
        tk.Button(subframe, text="+", command=make_adjust_button_int(entry, +5),width=2).pack(side=tk.LEFT, padx=1)
        tk.Button(subframe, text="-", command=make_adjust_button_int(entry, -5),width=2).pack(side=tk.LEFT, padx=1)
    else:
        tk.Button(subframe, text="+", command=make_adjust_button(entry, +0.1),width=2).pack(side=tk.LEFT, padx=1)
        tk.Button(subframe, text="-", command=make_adjust_button(entry, -0.1),width=2).pack(side=tk.LEFT, padx=1)
# 2nd grouped entries side by side for Attack Range Multiplier, Attack Speed Multiplier, Movement Speed Multiplier
trio_2_frame = tk.Frame(root)
trio_2_frame.pack()
for label_text, default in [("Attack Range Multiplier", "1.0"), ("Attack Speed Multiplier", "1.0"), ("Movement Speed Multiplier", "1.0")]:
    subframe = tk.Frame(trio_2_frame)
    subframe.pack(side=tk.LEFT, padx=5)
    tk.Label(subframe, text=label_text).pack()
    entry = tk.Entry(subframe, width=10)
    entry.insert(0, default)
    entry.pack(side=tk.LEFT, padx=2)
    fields[label_text] = entry
    # Add +/- buttons for each entry
    tk.Button(subframe, text="+", command=make_adjust_button(entry, +0.1),width=2).pack(side=tk.LEFT, padx=1)
    tk.Button(subframe, text="-", command=make_adjust_button(entry, -0.1),width=2).pack(side=tk.LEFT, padx=1)

create_entry("Animation") # 7th entry, used for animation selection
tk.Label(root, text="Swing Sound ID and Pitch:").pack()
sound_frame = tk.Frame(root)
sound_frame.pack()
sound_entry = tk.Entry(sound_frame, width=35)# 8th entry, used for swing sound ID selection
sound_entry.insert(0, "bettercombat:sword_slash")
sound_entry.pack(side=tk.LEFT)
fields["Swing Sound ID"] = sound_entry

def show_sound_menu():
    menu = tk.Menu(root, tearoff=0)
    for sid in sound_ids:
        menu.add_command(label=sid, command=lambda s=sid: sound_entry.delete(0, tk.END) or sound_entry.insert(0, s) or pitch_entry.delete(0, tk.END) or pitch_entry.insert(0, "0.0"))
    menu.post(sound_entry.winfo_rootx(), sound_entry.winfo_rooty() + sound_entry.winfo_height())
# Button to show sound options
tk.Button(sound_frame, text="▼", width=2, command=show_sound_menu).pack(side=tk.LEFT)

pitch_entry = tk.Entry(sound_frame, width=5)#part for the swing sound pitch
pitch_entry.insert(0, "0.0")
pitch_entry.pack(side=tk.LEFT, padx=2)
fields["Swing Sound Pitch"] = pitch_entry

pitch_control = tk.Frame(sound_frame)
pitch_control.pack(side=tk.LEFT)

def make_pitch_adjust_button(entry_ref, delta):
    def adjust():
        try:
            current = float(entry_ref.get() or 0)
            new_value = round(current + delta, 2)
            entry_ref.delete(0, tk.END)
            entry_ref.insert(0, f"{new_value:.2f}")
        except ValueError:
            pass
    return adjust
# Add +/- buttons for Swing Sound Pitch
tk.Button(pitch_control, text="+", command=make_pitch_adjust_button(pitch_entry, +0.1), width=2).pack(side=tk.LEFT)
tk.Button(pitch_control, text="-", command=make_pitch_adjust_button(pitch_entry, -0.1), width=2).pack(side=tk.LEFT)

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
    top = tk.Toplevel(root)
    top.title("Select Animation")
    top.geometry("400x400")

    list_frame = tk.Frame(top)
    list_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    anim_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
    anim_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=anim_list.yview)

    # Populate list with animations
    for hb_type, anims in attack_defaults.items():
        if hitbox is None or hb_type == hitbox:
            for anim in anims:
                if hitbox:
                    name_prefix = ""
                elif hb_type == "VERTICAL_PLANE":
                    name_prefix ='[ | ] '
                elif hb_type == "HORIZONTAL_PLANE":
                    name_prefix = '[ - ] '
                elif hb_type == "FORWARD_BOX":
                    name_prefix = '[ · ] '
                else:
                    name_prefix = f"[{hb_type}] "
                anim_list.insert(tk.END, f"{name_prefix}{anim}")

    def on_select(event=None):
        try:
            selection = anim_list.get(anim_list.curselection())
            
            if hitbox:# If hitbox is specified, use it directly
                hb_label = hitbox  
                anim = selection
            else:# If hitbox is not specified, parse the selection
                hb_label, anim = selection.split("] ")
                hb_label = hb_label[1:]
                if hb_label == ' | ':
                    hb_label = "VERTICAL_PLANE"
                elif hb_label == ' - ':
                    hb_label = "HORIZONTAL_PLANE"
                elif hb_label == ' · ':
                    hb_label = "FORWARD_BOX"

            set_anim_from_menu(widget, anim, hb_label)
            top.destroy()
        except:
            pass

    anim_list.bind("<Double-1>", on_select)
    tk.Button(top, text="Select", command=on_select).pack(pady=5)


def set_anim_from_menu(widget, anim, hitbox):
    widget.delete(0, tk.END)
    widget.insert(0, anim)
    #if not fields["Hitbox"].get().strip():
    fields["Hitbox"].delete(0, tk.END)
    fields["Hitbox"].insert(0, hitbox)
    anim_data = attack_defaults[hitbox][anim]
    angle = anim_data.get("angle")
    if angle :#and not fields["Angle"].get().strip():
        fields["Angle"].delete(0, tk.END)
        fields["Angle"].insert(0, str(angle))
    for key in ["damage_multiplier", "attack_range_multiplier", "attack_speed_multiplier", "movement_speed_multiplier"]:
        val = anim_data.get(key)
        if val is not None and key.replace("_", " ").title() in fields:
            fields[key.replace("_", " ").title()].delete(0, tk.END)
            fields[key.replace("_", " ").title()].insert(0, str(val))
    for cond in condition_vars:
        condition_vars[cond].set(cond in anim_data.get("conditions", []))

# Conditions checklist, make it a two-column layout
tk.Label(root, text="Conditions:").pack()
condition_vars = {}
cond_frame = tk.Frame(root)
cond_frame.pack()
for i, cond in enumerate(condition_enum):
    var = tk.BooleanVar()
    condition_vars[cond] = var
    cb = tk.Checkbutton(cond_frame, text=cond, variable=var)
    cb.grid(row=i // 2, column=i % 2, sticky='w')  # Two-column layout

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

listbox_frame = tk.Frame(root)
listbox_frame.pack()

scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
listbox = DraggableListbox(listbox_frame, width=60, height=10, yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


# Add/Edit/Delete/Load/Save/Update Config

def add_attack():
    try:
        attack = generate_attack()
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
        extract_attack(index)
        listbox.delete(index)
        attacks.pop(index)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def load_attack():
    try:
        index = listbox.curselection()
        if not index:
            messagebox.showwarning("No selection", "Select an attack to load.")
            return
        index = index[0]
        extract_attack(index)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_attack():
    try:
        index = listbox.curselection()
        if not index:
            messagebox.showwarning("No selection", "Select an attack to update.")
            return
        index = index[0]
        attack = generate_attack()
        attacks[index] = attack
        listbox.delete(index)
        listbox.insert(index, attack['animation'])
    except Exception as e:
        messagebox.showerror("Error", str(e))
        

def generate_attack():
    conditions = [c for c, v in condition_vars.items() if v.get()]
    upswing = float(fields["Upswing"].get() or 0.5)
    swing_sound_id = fields["Swing Sound ID"].get() or "bettercombat:sword_slash"
    swing_sound_pitch = float(fields["Swing Sound Pitch"].get() or 0.0)
    attack = {
        "hitbox": fields["Hitbox"].get(),
        "conditions": conditions,
        "damage_multiplier": float(fields["Damage Multiplier"].get() or 1.0),
        "angle": int(fields["Angle"].get()),
        "upswing": upswing,
        "animation": fields["Animation"].get(),
        "swing_sound": {"id": swing_sound_id, "pitch": swing_sound_pitch},
        "attack_range_multiplier": float(fields["Attack Range Multiplier"].get() or 1.0),
        "attack_speed_multiplier": float(fields["Attack Speed Multiplier"].get() or 1.0),
        "movement_speed_multiplier": float(fields["Movement Speed Multiplier"].get() or 1.0),
        "damage_type": ""
    }
    return attack
def extract_attack(index):
    try:
        attack = attacks[index]
        fields["Hitbox"].delete(0, tk.END)
        fields["Hitbox"].insert(0, attack.get("hitbox", ""))
        fields["Damage Multiplier"].delete(0, tk.END)
        fields["Damage Multiplier"].insert(0, attack.get("damage_multiplier", 1.0))
        fields["Angle"].delete(0, tk.END)
        fields["Angle"].insert(0, attack.get("angle", 0))
        fields["Upswing"].delete(0, tk.END)
        fields["Upswing"].insert(0, attack.get("upswing", 0.0))
        fields["Attack Range Multiplier"].delete(0, tk.END)
        fields["Attack Range Multiplier"].insert(0, attack.get("attack_range_multiplier", 1.0))
        fields["Attack Speed Multiplier"].delete(0, tk.END) 
        fields["Attack Speed Multiplier"].insert(0, attack.get("attack_speed_multiplier", 1.0))
        fields["Movement Speed Multiplier"].delete(0, tk.END)
        fields["Movement Speed Multiplier"].insert(0, attack.get("movement_speed_multiplier", 1.0))
        fields["Animation"].delete(0, tk.END)
        fields["Animation"].insert(0, attack.get("animation", ""))
        fields["Swing Sound ID"].delete(0, tk.END)
        fields["Swing Sound ID"].insert(0, attack.get("swing_sound", {}).get("id", ""))
        fields["Swing Sound Pitch"].delete(0, tk.END)
        fields["Swing Sound Pitch"].insert(0, str(attack.get("swing_sound", {}).get("pitch", 0.0)))
        for cond in condition_vars:
            condition_vars[cond].set(cond in attack.get("conditions", []))
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
        if "conditions" in filtered and not filtered["conditions"]:
            del filtered["conditions"]
        if "swing_sound" in filtered:
            if "pitch" in filtered["swing_sound"] and filtered["swing_sound"]["pitch"] == 0.0:
                del filtered["swing_sound"]["pitch"]
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

def restructure_pose_defaults():
    grouped = {"two_handed": [], "one_handed": []}
    for handed in ["one_handed","two_handed"]:
        if handed in pose_defaults:
            for pose in pose_defaults[handed]:
                grouped[handed].append(pose)
    return grouped

def update_config():
    pose = pose_var.get().strip()
    two_handed = two_handed_var.get()
    if pose:
        if two_handed:
            if "two_handed" not in pose_defaults:
                pose_defaults["two_handed"] = []
            if pose not in pose_defaults["two_handed"]:
                pose_defaults["two_handed"].append(pose)
        else:
            if "one_handed" not in pose_defaults:
                pose_defaults["one_handed"] = []
            if pose not in pose_defaults["one_handed"]:
                pose_defaults["one_handed"].append(pose)
    anim = fields["Animation"].get()
    hitbox = fields["Hitbox"].get()
    angle = fields["Angle"].get()
    damage_multiplier = fields["Damage Multiplier"].get()
    attack_range_multiplier = fields["Attack Range Multiplier"].get()
    attack_speed_multiplier = fields["Attack Speed Multiplier"].get()
    movement_speed_multiplier = fields["Movement Speed Multiplier"].get()
    sound_id = fields["Swing Sound ID"].get().strip()
    conditions = [c for c, v in condition_vars.items() if v.get()]
    if anim and hitbox and angle:
        if hitbox not in attack_defaults:
            attack_defaults[hitbox] = {}
            attack_defaults[hitbox][anim] = {}
        if angle:
            attack_defaults[hitbox][anim]["angle"] = int(angle)
        if damage_multiplier and damage_multiplier != "1.0":
            attack_defaults[hitbox][anim]["damage_multiplier"] = float(damage_multiplier)
        if attack_range_multiplier and attack_range_multiplier != "1.0":
            attack_defaults[hitbox][anim]["attack_range_multiplier"] = float(attack_range_multiplier)
        if attack_speed_multiplier and attack_speed_multiplier != "1.0":
            attack_defaults[hitbox][anim]["attack_speed_multiplier"] = float(attack_speed_multiplier)
        if movement_speed_multiplier and movement_speed_multiplier != "1.0":
            attack_defaults[hitbox][anim]["movement_speed_multiplier"] = float(movement_speed_multiplier)
        if conditions and conditions != []:
            attack_defaults[hitbox][anim]["conditions"] = conditions
    if sound_id and sound_id not in sound_ids:
        sound_ids.append(sound_id)
    config_data = {
        "pose": pose_defaults,
        "attack": attack_defaults,
        "condition_enum": condition_enum,
        "sound_id": sound_ids
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2)
    messagebox.showinfo("Saved", f"Config saved to {config_path}")

# Buttons
btn_frame_row1 = tk.Frame(root)
btn_frame_row1.pack(pady=0)
tk.Button(btn_frame_row1, text="Add Attack", command=add_attack).pack(side=tk.LEFT,padx=0)
tk.Button(btn_frame_row1, text="Load Selected", command=load_attack).pack(side=tk.LEFT,padx=0)
tk.Button(btn_frame_row1, text="Update Selected", command=update_attack).pack(side=tk.LEFT,padx=0)
tk.Button(btn_frame_row1, text="Edit Selected", command=edit_attack).pack(side=tk.LEFT,padx=0)
tk.Button(btn_frame_row1, text="Delete Selected", command=delete_attack).pack(side=tk.LEFT,padx=0)
btn_frame_row2 = tk.Frame(root)
btn_frame_row2.pack(pady=0)
tk.Button(btn_frame_row2, text="Save Attack String JSON", command=save_json).pack(side=tk.LEFT,padx=12)
tk.Button(btn_frame_row2, text="Update Config", command=update_config).pack(side=tk.LEFT,padx=12)
tk.Button(btn_frame_row2, text="Load Attack String JSON", command=load_json).pack(side=tk.LEFT,padx=12)

root.mainloop()
