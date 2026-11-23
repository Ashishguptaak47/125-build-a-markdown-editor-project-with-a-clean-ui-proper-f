import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from markdown_editor.core.parser import MarkdownEngine
from markdown_editor.core.stats import DocumentMetrics
from markdown_editor.ui.editor import MarkdownEditor
from markdown_editor.ui.preview import MarkdownPreview
from markdown_editor.ui.themes import THEMES


class MarkdownStudioApp(tk.Tk):
    """Main application window for Markdown Studio."""

    SAMPLE_TEXT = """# Welcome to Markdown Studio

A modern, clean, and real-time Markdown editor with live preview.

## Features List
- **Live Formatting**: Side-by-side editing and formatted view.
- **Syntax Tags**: Headers, blockquotes, lists, and inline code.
- **Document Outline**: Click headers in the sidebar to jump instantly.

### Code Blocks Example
```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
print(greet("Markdown Studio"))
```

> "Simplicity is prerequisite for reliability." - Edsger W. Dijkstra

### Next Steps
- [x] Create project architecture
- [ ] Write documentation
- [ ] Deploy v1.0.0 release
"""

    def __init__(self):
        super().__init__()
        self.title("Markdown Studio - Untitled.md")
        self.geometry("1100x700")
        self.minsize(800, 500)

        self.current_file = None
        self.theme_name = "dark"
        self.engine = MarkdownEngine()

        self._create_menu()
        self._create_widgets()
        self.apply_theme(self.theme_name)

        # Load default text
        self.editor.set_text(self.SAMPLE_TEXT)
        self._on_content_changed(self.SAMPLE_TEXT)

    def _create_menu(self):
        menu_bar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.action_new)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.action_open)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.action_save)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.action_save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export to HTML...", command=self.action_export_html)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Toggle Light/Dark Theme", command=self.toggle_theme)
        view_menu.add_command(label="Toggle Outline Sidebar", command=self.toggle_sidebar)
        menu_bar.add_cascade(label="View", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Cheatsheet", command=self.show_cheatsheet)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menu_bar)

        # Keyboard shortcuts
        self.bind("<Control-n>", lambda e: self.action_new())
        self.bind("<Control-o>", lambda e: self.action_open())
        self.bind("<Control-s>", lambda e: self.action_save())
        self.bind("<Control-S>", lambda e: self.action_save_as())

    def _create_widgets(self):
        # Main horizontal split
        self.main_split = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_split.pack(fill=tk.BOTH, expand=True)

        # Outline Sidebar
        self.sidebar_frame = tk.Frame(self.main_split, width=220)
        self.sidebar_label = tk.Label(self.sidebar_frame, text="TABLE OF CONTENTS", font=("Segoe UI", 9, "bold"))
        self.sidebar_label.pack(fill=tk.X, padx=8, pady=(8, 4))

        self.outline_listbox = tk.Listbox(self.sidebar_frame, border=0, relief="flat", activestyle="none")
        self.outline_listbox.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.outline_listbox.bind("<Double-Button-1>", self._on_outline_select)
        self.main_split.add(self.sidebar_frame, weight=1)

        # Editor & Preview Splitter
        self.content_split = ttk.PanedWindow(self.main_split, orient=tk.HORIZONTAL)
        self.editor = MarkdownEditor(self.content_split, on_change=self._on_content_changed)
        self.preview = MarkdownPreview(self.content_split, engine=self.engine)
        self.content_split.add(self.editor, weight=3)
        self.content_split.add(self.preview, weight=3)
        self.main_split.add(self.content_split, weight=5)

        # Status bar
        self.status_bar = tk.Label(
            self,
            text="Ready",
            anchor="w",
            padx=10,
            pady=4,
            font=("Segoe UI", 9),
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _on_content_changed(self, text: str):
        self.preview.render(text)
        self._update_stats(text)
        self._update_outline(text)

    def _update_stats(self, text: str):
        metrics = DocumentMetrics.compute_stats(text)
        stat_str = (
            f"Words: {metrics['words']}  |  "
            f"Chars: {metrics['chars']}  |  "
            f"Lines: {metrics['lines']}  |  "
            f"Est. Read: ~{metrics['reading_time_mins']} min"
        )
        self.status_bar.config(text=stat_str)

    def _update_outline(self, text: str):
        outline = DocumentMetrics.extract_outline(text)
        self.outline_listbox.delete(0, tk.END)
        self.outline_data = outline
        for item in outline:
            indent = "  " * (item["level"] - 1)
            self.outline_listbox.insert(tk.END, f"{indent}H{item['level']}: {item['title']}")

    def _on_outline_select(self, event):
        selection = self.outline_listbox.curselection()
        if selection and selection[0] < len(self.outline_data):
            target_line = self.outline_data[selection[0]]["line"]
            self.editor.jump_to_line(target_line)

    def apply_theme(self, theme_name: str):
        self.theme_name = theme_name
        theme = THEMES[theme_name]
        self.configure(bg=theme["bg"])
        self.sidebar_frame.configure(bg=theme["sidebar_bg"])
        self.sidebar_label.configure(bg=theme["sidebar_bg"], fg=theme["sidebar_fg"])
        self.outline_listbox.configure(bg=theme["sidebar_bg"], fg=theme["sidebar_fg"], selectbackground=theme["accent"])
        self.status_bar.configure(bg=theme["status_bg"], fg=theme["status_fg"])
        self.editor.apply_theme(theme)
        self.preview.apply_theme(theme)

    def toggle_theme(self):
        new_theme = "light" if self.theme_name == "dark" else "dark"
        self.apply_theme(new_theme)

    def toggle_sidebar(self):
        if self.sidebar_frame.winfo_viewable():
            self.main_split.forget(self.sidebar_frame)
        else:
            self.main_split.insert(0, self.sidebar_frame, weight=1)

    def action_new(self):
        self.current_file = None
        self.title("Markdown Studio - Untitled.md")
        self.editor.set_text("")

    def action_open(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Markdown Files", "*.md;*.markdown"), ("All Files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.current_file = filepath
                self.title(f"Markdown Studio - {os.path.basename(filepath)}")
                self.editor.set_text(content)
            except Exception as e:
                messagebox.showerror("Open Error", f"Failed to open file:\n{e}")

    def action_save(self):
        if not self.current_file:
            return self.action_save_as()
        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.editor.get_text())
            self.title(f"Markdown Studio - {os.path.basename(self.current_file)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{e}")

    def action_save_as(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")],
        )
        if filepath:
            self.current_file = filepath
            self.action_save()

    def action_export_html(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
        )
        if filepath:
            try:
                doc_title = os.path.splitext(os.path.basename(filepath))[0]
                html = self.engine.to_html(self.editor.get_text(), title=doc_title)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html)
                messagebox.showinfo("Export Success", f"Exported HTML successfully to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export HTML:\n{e}")

    def show_cheatsheet(self):
        cheatsheet = (
            "Markdown Quick Reference:\n\n"
            "# Heading 1\n"
            "## Heading 2\n"
            "**Bold text**\n"
            "*Italic text*\n"
            "`Inline code`\n"
            "```python\ncode block\n```\n"
            "> Blockquote\n"
            "- Bullet item\n"
            "1. Numbered item\n"
            "- [ ] Task checkbox\n"
            "[Link Name](https://url)\n"
        )
        messagebox.showinfo("Markdown Cheatsheet", cheatsheet)

    def show_about(self):
        messagebox.showinfo(
            "About Markdown Studio",
            "Markdown Studio v1.0.0\nA clean and efficient desktop Markdown editor and live preview tool.",
        )
