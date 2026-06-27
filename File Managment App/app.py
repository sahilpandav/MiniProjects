import tkinter as tk
import tkinter.simpledialog
import tkinter.messagebox
from tkinter import ttk
from pathlib import Path
import os
import shutil


class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")
        self.root.geometry("900x600")

        self.current_path  = Path.home()
        self.history       = [Path.home()]
        self.history_index = 0
        self.clipboard_path = None
        self.clipboard_mode = None

        self._build_ui()
        self.load_folder(self.current_path)

    def _build_ui(self):
        toolbar = tk.Frame(self.root, bg="#2c3e50", height=40)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        tk.Button(toolbar, text="▲ Up",    command=self.go_up,
                  bg="#34495e", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=4, pady=5)
        tk.Button(toolbar, text="◀ Back",  command=self.go_back,
                  bg="#34495e", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=4, pady=5)
        tk.Button(toolbar, text="📁 New",   command=self.create_folder,
                  bg="#27ae60", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=4, pady=5)
        tk.Button(toolbar, text="✏ Rename", command=self.rename_item,
                  bg="#e67e22", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=4, pady=5)
        tk.Button(toolbar, text="🗑 Delete", command=self.delete_item,
                  bg="#e74c3c", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=4, pady=5)
        tk.Button(toolbar, text="📋 Copy",  command=self.copy_item,
                  bg="#2980b9", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=4, pady=5)
        tk.Button(toolbar, text="✂ Cut",   command=self.move_item,
                  bg="#8e44ad", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=4, pady=5)
        tk.Button(toolbar, text="📌 Paste", command=self.paste_item,
                  bg="#16a085", fg="white", relief="flat", padx=10).pack(side=tk.LEFT, padx=4, pady=5)

        self.address_var = tk.StringVar(value=str(self.current_path))
        address_entry = tk.Entry(toolbar, textvariable=self.address_var,
                                  font=("Consolas", 10))
        address_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=6)
        address_entry.bind("<Return>", lambda e: self.navigate_to(self.address_var.get()))

        columns = ("name", "type", "size")
        self.tree = ttk.Treeview(self.root, columns=columns,
                                  show="headings", selectmode="browse")
        self.tree.heading("name", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.column("name", width=450)
        self.tree.column("type", width=100, anchor="center")
        self.tree.column("size", width=100, anchor="e")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self._on_double_click)

        self.status_var = tk.StringVar()
        tk.Label(self.root, textvariable=self.status_var,
                  anchor="w", bg="#ecf0f1").pack(fill=tk.X)

    # ── Load ────────────────────────────────────────────────

    def load_folder(self, path):
        self.tree.delete(*self.tree.get_children())
        try:
            entries = list(path.iterdir())
        except PermissionError:
            self.status_var.set("Access denied.")
            return

        folders = sorted([e for e in entries if e.is_dir()],  key=lambda e: e.name.lower())
        files   = sorted([e for e in entries if e.is_file()], key=lambda e: e.name.lower())

        for entry in folders + files:
            self._add_row(entry)

        self.status_var.set(f"{len(folders)} folders,  {len(files)} files  |  {path}")

    def _add_row(self, entry):
        try:
            stat = entry.stat()
        except (PermissionError, OSError):
            return

        is_dir    = entry.is_dir()
        icon      = "📁" if is_dir else "📄"
        name      = entry.name
        file_type = "Folder" if is_dir else (entry.suffix.upper().lstrip(".") or "File")
        size      = "" if is_dir else self._format_size(stat.st_size)

        self.tree.insert("", tk.END, values=(icon + "  " + name, file_type, size))

    def _format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.1f} MB"
        else:
            return f"{size_bytes / (1024 ** 3):.2f} GB"

    # ── Navigation ──────────────────────────────────────────

    def navigate_to(self, path):
        path = Path(path)
        if not path.exists() or not path.is_dir():
            self.status_var.set("Invalid path.")
            return
        self.history = self.history[:self.history_index + 1]
        self.history.append(path)
        self.history_index += 1
        self.current_path = path
        self.address_var.set(str(path))
        self.load_folder(path)

    def go_up(self):
        parent = self.current_path.parent
        if parent != self.current_path:
            self.navigate_to(parent)

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            self.address_var.set(str(self.current_path))
            self.load_folder(self.current_path)

    def _on_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        row_values = self.tree.item(selected[0], "values")
        name   = row_values[0][3:]
        target = self.current_path / name
        if target.is_dir():
            self.navigate_to(target)

    # ── File Operations ─────────────────────────────────────

    def create_folder(self):
        name = tk.simpledialog.askstring("New Folder", "Enter folder name:")
        if not name:
            return
        new_folder = self.current_path / name
        if new_folder.exists():
            tk.messagebox.showerror("Error", "A file or folder with that name already exists.")
            return
        os.mkdir(new_folder)
        self.load_folder(self.current_path)

    def rename_item(self):
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("Warning", "Select a file or folder first.")
            return
        row_values = self.tree.item(selected[0], "values")
        old_name   = row_values[0][3:]
        old_path   = self.current_path / old_name
        new_name   = tk.simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
        new_path = self.current_path / new_name
        if new_path.exists():
            tk.messagebox.showerror("Error", "That name is already taken.")
            return
        os.rename(old_path, new_path)
        self.load_folder(self.current_path)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("Warning", "Select a file or folder first.")
            return
        row_values = self.tree.item(selected[0], "values")
        name       = row_values[0][3:]
        target     = self.current_path / name
        confirmed  = tk.messagebox.askyesno("Delete", f"Are you sure you want to delete '{name}'?")
        if not confirmed:
            return
        if target.is_file():
            os.remove(target)
        elif target.is_dir():
            shutil.rmtree(target)
        self.load_folder(self.current_path)

    # ── Copy / Move ─────────────────────────────────────────

    def copy_item(self):
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("Warning", "Select a file or folder first.")
            return
        row_values = self.tree.item(selected[0], "values")
        name       = row_values[0][3:]
        self.clipboard_path = self.current_path / name
        self.clipboard_mode = "copy"
        self.status_var.set(f"Copied: {self.clipboard_path}")

    def move_item(self):
        selected = self.tree.selection()
        if not selected:
            tk.messagebox.showwarning("Warning", "Select a file or folder first.")
            return
        row_values = self.tree.item(selected[0], "values")
        name       = row_values[0][3:]
        self.clipboard_path = self.current_path / name
        self.clipboard_mode = "move"
        self.status_var.set(f"Cut: {self.clipboard_path}")

    def paste_item(self):
        if not self.clipboard_path:
            tk.messagebox.showwarning("Warning", "Nothing to paste. Copy or Cut something first.")
            return
        if not self.clipboard_path.exists():
            tk.messagebox.showerror("Error", "Source item no longer exists.")
            self.clipboard_path = None
            self.clipboard_mode = None
            return

        name        = self.clipboard_path.name
        destination = self.current_path / name

        if self.clipboard_path.parent == self.current_path:
            tk.messagebox.showwarning("Warning", "Source and destination are the same folder.")
            return

        if destination.exists():
            confirmed = tk.messagebox.askyesno("Conflict", f"'{name}' already exists here. Replace it?")
            if not confirmed:
                return

        if self.clipboard_mode == "copy":
            if self.clipboard_path.is_file():
                shutil.copy2(self.clipboard_path, destination)
            elif self.clipboard_path.is_dir():
                shutil.copytree(self.clipboard_path, destination, dirs_exist_ok=True)

        elif self.clipboard_mode == "move":
            shutil.move(self.clipboard_path, destination)
            self.clipboard_path = None
            self.clipboard_mode = None

        self.load_folder(self.current_path)
        self.status_var.set(f"Pasted '{name}' into {self.current_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop()