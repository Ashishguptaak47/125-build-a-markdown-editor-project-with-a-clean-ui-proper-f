import tkinter as tk
from tkinter import font as tkfont
from markdown_editor.core.parser import MarkdownEngine


class MarkdownPreview(tk.Frame):
    """Live rich formatted Markdown preview pane."""

    def __init__(self, master, engine: MarkdownEngine, **kwargs):
        super().__init__(master, **kwargs)
        self.engine = engine
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.display = tk.Text(
            self,
            wrap="word",
            state="disabled",
            padx=16,
            pady=16,
            relief="flat",
            border=0,
            cursor="arrow",
        )
        self.display.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.display.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.display.configure(yscrollcommand=self.scrollbar.set)

        self._setup_tags()

    def _setup_tags(self):
        self.base_font = "Segoe UI"
        self.display.tag_configure("h1", font=(self.base_font, 20, "bold"), spacing1=10, spacing3=6)
        self.display.tag_configure("h2", font=(self.base_font, 16, "bold"), spacing1=8, spacing3=4)
        self.display.tag_configure("h3", font=(self.base_font, 13, "bold"), spacing1=6, spacing3=2)
        self.display.tag_configure("body", font=(self.base_font, 11), spacing1=2, spacing3=2)
        self.display.tag_configure("bold", font=(self.base_font, 11, "bold"))
        self.display.tag_configure("italic", font=(self.base_font, 11, "italic"))
        self.display.tag_configure("code_block", font=("Consolas", 10), lmargin1=12, lmargin2=12, spacing1=4, spacing3=4)
        self.display.tag_configure("inline_code", font=("Consolas", 10))
        self.display.tag_configure("quote", font=(self.base_font, 11, "italic"), lmargin1=18, lmargin2=18)
        self.display.tag_configure("list_item", font=(self.base_font, 11), lmargin1=16, lmargin2=28)
        self.display.tag_configure("hr", font=(self.base_font, 8))

    def render(self, markdown_text: str):
        tokens = self.engine.tokenize(markdown_text)
        self.display.configure(state="normal")
        self.display.delete("1.0", "end")

        for token in tokens:
            if token.type == "heading":
                tag = f"h{min(token.level, 3)}"
                self.display.insert("end", f"{token.content}\n", (tag,))
            elif token.type == "paragraph":
                self._insert_inline_text(token.content)
                self.display.insert("end", "\n\n", ("body",))
            elif token.type == "code_block":
                self.display.insert("end", f"{token.content}\n\n", ("code_block",))
            elif token.type == "blockquote":
                self.display.insert("end", f"“ {token.content}\n\n", ("quote",))
            elif token.type == "list_item":
                indent = " " * (token.level * 2)
                self.display.insert("end", f"{indent}• {token.content}\n", ("list_item",))
            elif token.type == "ordered_item":
                num = token.meta.get("num", "1") if token.meta else "1"
                self.display.insert("end", f"{num}. {token.content}\n", ("list_item",))
            elif token.type == "task_item":
                box = "[x]" if token.meta and token.meta.get("checked") else "[ ]"
                self.display.insert("end", f"{box} {token.content}\n", ("list_item",))
            elif token.type == "hr":
                self.display.insert("end", "―" * 40 + "\n\n", ("hr",))
            elif token.type == "newline":
                self.display.insert("end", "\n")

        self.display.configure(state="disabled")

    def _insert_inline_text(self, text: str):
        inlines = self.engine.parse_inline_elements(text)
        for item in inlines:
            t = item["type"]
            val = item.get("value", "")
            if t == "text":
                self.display.insert("end", val, ("body",))
            elif t == "bold":
                self.display.insert("end", val, ("bold",))
            elif t == "italic":
                self.display.insert("end", val, ("italic",))
            elif t == "code":
                self.display.insert("end", f" {val} ", ("inline_code",))
            elif t == "link":
                txt = item.get("text", "")
                self.display.insert("end", txt, ("link",))
            else:
                self.display.insert("end", val, ("body",))

    def apply_theme(self, theme: dict):
        self.display.configure(bg=theme["preview_bg"], fg=theme["preview_fg"])
        self.display.tag_configure("h1", foreground=theme["heading_fg"])
        self.display.tag_configure("h2", foreground=theme["heading_fg"])
        self.display.tag_configure("h3", foreground=theme["heading_fg"])
        self.display.tag_configure("code_block", background=theme["code_bg"], foreground=theme["code_fg"])
        self.display.tag_configure("inline_code", background=theme["code_bg"], foreground=theme["code_fg"])
        self.display.tag_configure("quote", foreground=theme["quote_fg"])
        self.display.tag_configure("hr", foreground=theme["border"])
