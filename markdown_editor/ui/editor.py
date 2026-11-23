import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional
import re


class MarkdownEditor(tk.Frame):
    """Editor widget with synchronized line numbers and markdown syntax coloring."""

    def __init__(self, master, on_change: Optional[Callable[[str], None]] = None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_change = on_change
        self.font = tkfont.Font(family="Consolas", size=11)

        # Layout columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Line numbers sidebar
        self.line_numbers = tk.Text(
            self,
            width=4,
            padx=4,
            pady=6,
            takefocus=0,
            border=0,
            font=self.font,
            state="disabled",
            wrap="none",
        )
        self.line_numbers.grid(row=0, column=0, sticky="nsew")

        # Main text editing area
        self.text_area = tk.Text(
            self,
            wrap="word",
            undo=True,
            font=self.font,
            padx=8,
            pady=6,
            relief="flat",
            border=0,
        )
        self.text_area.grid(row=0, column=1, sticky="nsew")

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self._on_scroll)
        self.scrollbar.grid(row=0, column=2, sticky="ns")
        self.text_area.configure(yscrollcommand=self._on_text_scroll)

        # Bindings
        self.text_area.bind("<KeyRelease>", self._on_key_release)
        self.text_area.bind("<MouseWheel>", self._sync_lines)
        self.text_area.bind("<Button-1>", lambda e: self.after(10, self._update_line_numbers))

        self._configure_syntax_tags()

    def _configure_syntax_tags(self):
        self.text_area.tag_configure("syntax_heading", foreground="#007acc", font=(self.font.cget("family"), 11, "bold"))
        self.text_area.tag_configure("syntax_code", foreground="#d73a49", background="#f0f0f0")
        self.text_area.tag_configure("syntax_bold", font=(self.font.cget("family"), 11, "bold"))
        self.text_area.tag_configure("syntax_italic", font=(self.font.cget("family"), 11, "italic"))
        self.text_area.tag_configure("syntax_list", foreground="#e36209")
        self.text_area.tag_configure("syntax_quote", foreground="#6a737d", font=(self.font.cget("family"), 11, "italic"))

    def _on_scroll(self, *args):
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def _on_text_scroll(self, *args):
        self.scrollbar.set(*args)
        self.line_numbers.yview_moveto(args[0])

    def _sync_lines(self, event=None):
        self.after(5, self._update_line_numbers)

    def _on_key_release(self, event=None):
        self._update_line_numbers()
        self.highlight_syntax()
        if self.on_change:
            self.on_change(self.get_text())

    def _update_line_numbers(self):
        line_count = int(self.text_area.index("end-1c").split(".")[0])
        line_strings = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_strings)
        self.line_numbers.config(state="disabled")
        self.line_numbers.yview_moveto(self.text_area.yview()[0])

    def highlight_syntax(self):
        for tag in ["syntax_heading", "syntax_code", "syntax_bold", "syntax_italic", "syntax_list", "syntax_quote"]:
            self.text_area.tag_remove(tag, "1.0", "end")

        content = self.get_text()
        lines = content.split("\n")

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                self.text_area.tag_add("syntax_heading", f"{idx}.0", f"{idx}.end")
            elif stripped.startswith(("* ", "- ", "+ ")) or re.match(r"^\d+\.\s", stripped):
                self.text_area.tag_add("syntax_list", f"{idx}.0", f"{idx}.end")
            elif stripped.startswith(">"):
                self.text_area.tag_add("syntax_quote", f"{idx}.0", f"{idx}.end")

        # Inline backticks
        for match in re.finditer(r"`[^`]+`", content):
            start_idx = self._pos_to_index(content, match.start())
            end_idx = self._pos_to_index(content, match.end())
            self.text_area.tag_add("syntax_code", start_idx, end_idx)

    @staticmethod
    def _pos_to_index(text: str, pos: int) -> str:
        lines = text[:pos].split("\n")
        row = len(lines)
        col = len(lines[-1])
        return f"{row}.{col}"

    def get_text(self) -> str:
        return self.text_area.get("1.0", "end-1c")

    def set_text(self, text: str):
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", text)
        self._update_line_numbers()
        self.highlight_syntax()
        if self.on_change:
            self.on_change(text)

    def jump_to_line(self, line: int):
        idx = f"{line}.0"
        self.text_area.see(idx)
        self.text_area.mark_set("insert", idx)
        self.text_area.focus()
        self._update_line_numbers()

    def apply_theme(self, theme: dict):
        self.text_area.config(
            bg=theme["editor_bg"],
            fg=theme["editor_fg"],
            insertbackground=theme["editor_fg"],
        )
        self.line_numbers.config(
            bg=theme["line_nums_bg"],
            fg=theme["line_nums_fg"],
        )
        self.text_area.tag_configure("syntax_heading", foreground=theme["heading_fg"])
        self.text_area.tag_configure("syntax_code", foreground=theme["code_fg"], background=theme["code_bg"])
        self.text_area.tag_configure("syntax_quote", foreground=theme["quote_fg"])
