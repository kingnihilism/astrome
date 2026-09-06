from __future__ import annotations

import json
import tkinter as tk
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from uuid import uuid4


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
DATA_FILE = DATA_DIR / "astro_me.json"

CATEGORIES = {
    "natal": {
        "label": "Natal Chart",
        "description": "Your permanent natal placements, angles, houses, and aspects.",
        "fields": [("name", "Placement"), ("position", "Position"), ("house", "House"), ("notes", "Notes")],
    },
    "asteroids": {
        "label": "Asteroids",
        "description": "Only the asteroids you actually use.",
        "fields": [("name", "Asteroid"), ("position", "Position"), ("house", "House"), ("notes", "Meaning / Notes")],
    },
    "solar_returns": {
        "label": "Solar Returns",
        "description": "One record per return year, copied from Astrolog.",
        "fields": [("name", "Return Year"), ("position", "Location / Date"), ("house", "Focus"), ("notes", "Interpretation")],
    },
    "persona_charts": {
        "label": "Persona Charts",
        "description": "Your selected persona charts and their defining placements.",
        "fields": [("name", "Persona Chart"), ("position", "Chart Date"), ("house", "Key Placements"), ("notes", "Interpretation")],
    },
    "notes": {
        "label": "Notes",
        "description": "Observations, patterns, research, and questions.",
        "fields": [("name", "Title"), ("position", "Topic"), ("house", "Tags"), ("notes", "Note")],
    },
}

EMPTY_DATA = {"schema_version": 1, "profile": {"name": "", "subtitle": "Astro Me"}, **{key: [] for key in CATEGORIES}}


class Store:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.data = self.load()

    def load(self) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps(EMPTY_DATA, indent=2), encoding="utf-8")
            return deepcopy(EMPTY_DATA)
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"Could not read {self.path.name}: {exc}") from exc
        for key in CATEGORIES:
            loaded.setdefault(key, [])
        return loaded

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")

    def records(self, category: str) -> list[dict]:
        return self.data[category]

    def add(self, category: str, values: dict) -> None:
        values.update(id=str(uuid4()), updated_at=datetime.now().isoformat(timespec="seconds"))
        self.data[category].append(values)
        self.save()

    def update(self, category: str, record_id: str, values: dict) -> None:
        record = self.find(category, record_id)
        record.update(values)
        record["updated_at"] = datetime.now().isoformat(timespec="seconds")
        self.save()

    def duplicate(self, category: str, record_id: str) -> None:
        record = deepcopy(self.find(category, record_id))
        record["id"] = str(uuid4())
        record["name"] = f"{record.get('name', 'Untitled')} (Copy)"
        record["updated_at"] = datetime.now().isoformat(timespec="seconds")
        self.data[category].append(record)
        self.save()

    def delete(self, category: str, record_id: str) -> None:
        self.data[category] = [item for item in self.data[category] if item.get("id") != record_id]
        self.save()

    def find(self, category: str, record_id: str) -> dict:
        return next(item for item in self.data[category] if item.get("id") == record_id)


class RecordDialog(tk.Toplevel):
    def __init__(self, parent, config: dict, record: dict | None = None):
        super().__init__(parent)
        self.result = None
        self.config = config
        self.record = record or {}
        self.title(("Edit " if record else "Add ") + config["label"])
        self.geometry("590x520")
        self.minsize(500, 440)
        self.configure(bg="#171321")
        self.transient(parent)
        self.grab_set()

        wrapper = ttk.Frame(self, padding=24, style="Panel.TFrame")
        wrapper.pack(fill="both", expand=True, padx=16, pady=16)
        self.inputs = {}
        for row, (key, label) in enumerate(config["fields"]):
            ttk.Label(wrapper, text=label, style="Form.TLabel").grid(row=row * 2, column=0, sticky="w", pady=(7, 4))
            if key == "notes":
                widget = tk.Text(wrapper, height=9, wrap="word", bg="#241d33", fg="#f5efff", insertbackground="#f5efff", relief="flat", padx=10, pady=10)
                widget.insert("1.0", self.record.get(key, ""))
            else:
                widget = ttk.Entry(wrapper, font=("Segoe UI", 10))
                widget.insert(0, self.record.get(key, ""))
            widget.grid(row=row * 2 + 1, column=0, sticky="nsew")
            self.inputs[key] = widget

        wrapper.columnconfigure(0, weight=1)
        wrapper.rowconfigure(7, weight=1)
        buttons = ttk.Frame(wrapper, style="Panel.TFrame")
        buttons.grid(row=8, column=0, sticky="e", pady=(18, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy, style="Quiet.TButton").pack(side="left", padx=5)
        ttk.Button(buttons, text="Save", command=self.submit, style="Accent.TButton").pack(side="left", padx=5)
        self.bind("<Escape>", lambda _event: self.destroy())

    def submit(self):
        values = {}
        for key, widget in self.inputs.items():
            values[key] = widget.get("1.0", "end").strip() if isinstance(widget, tk.Text) else widget.get().strip()
        if not values["name"]:
            messagebox.showwarning("Missing name", f"{self.config['fields'][0][1]} is required.", parent=self)
            return
        self.result = values
        self.destroy()


class AstroMe(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Astro Me — Personal Astrology Archive")
        self.geometry("1180x720")
        self.minsize(920, 600)
        self.configure(bg="#100d18")
        self.store = Store()
        self.active_category = "natal"
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Your data stays in this folder on your computer.")
        self.setup_styles()
        self.build_layout()
        self.show_category("natal")

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#100d18")
        style.configure("Panel.TFrame", background="#171321")
        style.configure("Sidebar.TFrame", background="#171321")
        style.configure("Title.TLabel", background="#100d18", foreground="#faf5ff", font=("Georgia", 24, "bold"))
        style.configure("Subtitle.TLabel", background="#100d18", foreground="#a99db9", font=("Segoe UI", 10))
        style.configure("Section.TLabel", background="#100d18", foreground="#e8ddf3", font=("Georgia", 18, "bold"))
        style.configure("Form.TLabel", background="#171321", foreground="#d9cde8", font=("Segoe UI", 10, "bold"))
        style.configure("Count.TLabel", background="#171321", foreground="#bca7d2", font=("Segoe UI", 9))
        style.configure("TEntry", fieldbackground="#241d33", foreground="#f5efff", bordercolor="#3d3151", insertcolor="#f5efff", padding=8)
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 9), borderwidth=0)
        style.configure("Nav.TButton", background="#171321", foreground="#cdbedc", anchor="w")
        style.map("Nav.TButton", background=[("active", "#2c223b")], foreground=[("active", "#ffffff")])
        style.configure("Active.Nav.TButton", background="#6f4b8b", foreground="#ffffff", anchor="w")
        style.configure("Accent.TButton", background="#9c6ac1", foreground="#ffffff")
        style.map("Accent.TButton", background=[("active", "#b27bd8")])
        style.configure("Quiet.TButton", background="#2a2237", foreground="#ddd1e8")
        style.map("Quiet.TButton", background=[("active", "#3b304d")])
        style.configure("Treeview", background="#191421", fieldbackground="#191421", foreground="#eee7f5", rowheight=35, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#2a2237", foreground="#e8ddf3", font=("Segoe UI", 10, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#684785")], foreground=[("selected", "#ffffff")])

    def build_layout(self):
        sidebar = ttk.Frame(self, width=230, padding=(18, 24), style="Sidebar.TFrame")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="✦  ASTRO ME", style="Form.TLabel", font=("Georgia", 15, "bold")).pack(anchor="w", pady=(0, 4))
        ttk.Label(sidebar, text="Personal chart archive", style="Count.TLabel").pack(anchor="w", pady=(0, 28))
        self.nav_buttons = {}
        for key, config in CATEGORIES.items():
            button = ttk.Button(sidebar, text=config["label"], style="Nav.TButton", command=lambda k=key: self.show_category(k))
            button.pack(fill="x", pady=3)
            self.nav_buttons[key] = button
        ttk.Label(sidebar, text="V1 · Astrolog companion", style="Count.TLabel").pack(side="bottom", anchor="w")

        main = ttk.Frame(self, padding=(28, 24))
        main.pack(side="left", fill="both", expand=True)
        top = ttk.Frame(main)
        top.pack(fill="x")
        title_box = ttk.Frame(top)
        title_box.pack(side="left", fill="x", expand=True)
        self.title_label = ttk.Label(title_box, text="", style="Section.TLabel")
        self.title_label.pack(anchor="w")
        self.description_label = ttk.Label(title_box, text="", style="Subtitle.TLabel")
        self.description_label.pack(anchor="w", pady=(4, 0))
        ttk.Button(top, text="+ Add Record", command=self.add_record, style="Accent.TButton").pack(side="right")

        search = ttk.Entry(main, textvariable=self.search_var)
        search.pack(fill="x", pady=(22, 14))
        search.bind("<KeyRelease>", lambda _event: self.refresh_table())
        self.search_var.set("")

        table_frame = ttk.Frame(main, style="Panel.TFrame")
        table_frame.pack(fill="both", expand=True)
        self.table = ttk.Treeview(table_frame, columns=("name", "position", "house", "notes"), show="headings", selectmode="browse")
        self.table.pack(side="left", fill="both", expand=True)
        self.table.bind("<Double-1>", lambda _event: self.edit_record())
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scroll.pack(side="right", fill="y")
        self.table.configure(yscrollcommand=scroll.set)

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(14, 0))
        ttk.Button(actions, text="Edit", command=self.edit_record, style="Quiet.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Duplicate", command=self.duplicate_record, style="Quiet.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Delete", command=self.delete_record, style="Quiet.TButton").pack(side="left")
        ttk.Label(actions, textvariable=self.status_var, style="Subtitle.TLabel").pack(side="right")

    def show_category(self, category: str):
        self.active_category = category
        config = CATEGORIES[category]
        self.title_label.configure(text=config["label"])
        self.description_label.configure(text=config["description"])
        for key, button in self.nav_buttons.items():
            button.configure(style="Active.Nav.TButton" if key == category else "Nav.TButton")
        for index, (key, label) in enumerate(config["fields"]):
            self.table.heading(key, text=label)
            widths = [180, 170, 150, 380]
            self.table.column(key, width=widths[index], minwidth=100, stretch=(key == "notes"))
        self.search_var.set("")
        self.refresh_table()

    def refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)
        query = self.search_var.get().strip().lower()
        visible = 0
        for record in self.store.records(self.active_category):
            values = tuple(record.get(key, "") for key, _label in CATEGORIES[self.active_category]["fields"])
            if query and query not in " ".join(values).lower():
                continue
            self.table.insert("", "end", iid=record["id"], values=values)
            visible += 1
        total = len(self.store.records(self.active_category))
        self.status_var.set(f"Showing {visible} of {total} records · saved locally")

    def selected_id(self) -> str | None:
        selected = self.table.selection()
        if not selected:
            messagebox.showinfo("Select a record", "Choose a record first.", parent=self)
            return None
        return selected[0]

    def open_dialog(self, record=None):
        dialog = RecordDialog(self, CATEGORIES[self.active_category], record)
        self.wait_window(dialog)
        return dialog.result

    def add_record(self):
        values = self.open_dialog()
        if values:
            self.store.add(self.active_category, values)
            self.refresh_table()

    def edit_record(self):
        record_id = self.selected_id()
        if not record_id:
            return
        values = self.open_dialog(self.store.find(self.active_category, record_id))
        if values:
            self.store.update(self.active_category, record_id, values)
            self.refresh_table()

    def duplicate_record(self):
        record_id = self.selected_id()
        if record_id:
            self.store.duplicate(self.active_category, record_id)
            self.refresh_table()

    def delete_record(self):
        record_id = self.selected_id()
        if not record_id:
            return
        record = self.store.find(self.active_category, record_id)
        if messagebox.askyesno("Delete record?", f"Delete “{record.get('name', 'this record')}”?", parent=self):
            self.store.delete(self.active_category, record_id)
            self.refresh_table()


def main():
    try:
        app = AstroMe()
    except RuntimeError as exc:
        messagebox.showerror("Astro Me could not start", str(exc))
        return
    app.mainloop()


if __name__ == "__main__":
    main()
