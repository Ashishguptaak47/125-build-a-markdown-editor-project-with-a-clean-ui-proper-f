import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class MarkdownToken:
    type: str
    content: str
    level: int = 0
    meta: Dict[str, Any] = None


class MarkdownEngine:
    """Parses Markdown text into structured tokens and clean HTML."""

    def __init__(self):
        self.hr_pattern = re.compile(r"^(\-{3,}|\*{3,}|_{3,})$")
        self.heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")
        self.blockquote_pattern = re.compile(r"^>\s*(.*)$")
        self.ul_pattern = re.compile(r"^(\s*)[\*\-\+]\s+(.*)$")
        self.ol_pattern = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
        self.task_pattern = re.compile(r"^(\s*)[\*\-\+]\s+\[([ xX])\]\s+(.*)$")

    def tokenize(self, text: str) -> List[MarkdownToken]:
        tokens: List[MarkdownToken] = []
        lines = text.splitlines()
        in_code_block = False
        code_lang = ""
        code_buffer: List[str] = []

        for line in lines:
            trimmed = line.rstrip()

            # Code block fence
            if trimmed.startswith("```"):
                if in_code_block:
                    tokens.append(MarkdownToken(
                        type="code_block",
                        content="\n".join(code_buffer),
                        meta={"lang": code_lang}
                    ))
                    code_buffer = []
                    in_code_block = False
                else:
                    in_code_block = True
                    code_lang = trimmed[3:].strip()
                continue

            if in_code_block:
                code_buffer.append(line)
                continue

            # Blank line
            if not trimmed:
                tokens.append(MarkdownToken(type="newline", content=""))
                continue

            # Headings
            h_match = self.heading_pattern.match(trimmed)
            if h_match:
                level = len(h_match.group(1))
                content = h_match.group(2).strip()
                tokens.append(MarkdownToken(type="heading", content=content, level=level))
                continue

            # Horizontal Rule
            if self.hr_pattern.match(trimmed):
                tokens.append(MarkdownToken(type="hr", content="---"))
                continue

            # Blockquote
            bq_match = self.blockquote_pattern.match(trimmed)
            if bq_match:
                tokens.append(MarkdownToken(type="blockquote", content=bq_match.group(1)))
                continue

            # Task List Item
            task_match = self.task_pattern.match(trimmed)
            if task_match:
                indent = len(task_match.group(1))
                checked = task_match.group(2).lower() == "x"
                tokens.append(MarkdownToken(
                    type="task_item",
                    content=task_match.group(3),
                    level=indent,
                    meta={"checked": checked}
                ))
                continue

            # Unordered List
            ul_match = self.ul_pattern.match(trimmed)
            if ul_match:
                indent = len(ul_match.group(1))
                tokens.append(MarkdownToken(type="list_item", content=ul_match.group(2), level=indent))
                continue

            # Ordered List
            ol_match = self.ol_pattern.match(trimmed)
            if ol_match:
                tokens.append(MarkdownToken(
                    type="ordered_item",
                    content=ol_match.group(3),
                    level=len(ol_match.group(1)),
                    meta={"num": ol_match.group(2)}
                ))
                continue

            # Default Paragraph line
            tokens.append(MarkdownToken(type="paragraph", content=trimmed))

        if in_code_block:
            tokens.append(MarkdownToken(
                type="code_block",
                content="\n".join(code_buffer),
                meta={"lang": code_lang}
            ))

        return tokens

    def parse_inline_elements(self, text: str) -> List[Dict[str, Any]]:
        """Parses inline markdown: bold, italic, code, links."""
        pattern = re.compile(
            r"(?P<code>`[^`]+`)|(?P<bold>\*\*[^*]+\*\*|__[^_]+__)|(?P<italic>\*[^*]+\*|_[^_]+_)|(?P<strike>~~[^~]+~~)|(?P<link>\[[^\]]+\]\([^\)]+\))"
        )
        result: List[Dict[str, Any]] = []
        cursor = 0

        for m in pattern.finditer(text):
            start, end = m.span()
            if start > cursor:
                result.append({"type": "text", "value": text[cursor:start]})

            if m.group("code"):
                result.append({"type": "code", "value": m.group("code")[1:-1]})
            elif m.group("bold"):
                result.append({"type": "bold", "value": m.group("bold")[2:-2]})
            elif m.group("italic"):
                result.append({"type": "italic", "value": m.group("italic")[1:-1]})
            elif m.group("strike"):
                result.append({"type": "strike", "value": m.group("strike")[2:-2]})
            elif m.group("link"):
                link_match = re.match(r"\[([^\]]+)\]\(([^\)]+)\)", m.group("link"))
                if link_match:
                    result.append({"type": "link", "text": link_match.group(1), "url": link_match.group(2)})
            cursor = end

        if cursor < len(text):
            result.append({"type": "text", "value": text[cursor:]})
        return result

    def to_html(self, markdown_text: str, title: str = "Document") -> str:
        """Convert markdown to complete styled standalone HTML document."""
        tokens = self.tokenize(markdown_text)
        body_html = []
        in_list = False

        for token in tokens:
            if token.type == "heading":
                body_html.append(f"<h{token.level}>{self._escape_html(token.content)}</h{token.level}>")
            elif token.type == "code_block":
                lang = token.meta.get("lang", "") if token.meta else ""
                cls = f' class="language-{lang}"' if lang else ""
                body_html.append(f"<pre><code{cls}>{self._escape_html(token.content)}</code></pre>")
            elif token.type == "blockquote":
                body_html.append(f"<blockquote><p>{self._escape_html(token.content)}</p></blockquote>")
            elif token.type == "list_item":
                body_html.append(f"<ul><li>{self._escape_html(token.content)}</li></ul>")
            elif token.type == "ordered_item":
                num = token.meta.get("num", "1") if token.meta else "1"
                body_html.append(f'<ol start="{num}"><li>{self._escape_html(token.content)}</li></ol>')
            elif token.type == "task_item":
                checked = 'checked="" ' if token.meta and token.meta.get("checked") else ""
                body_html.append(f'<div><input type="checkbox" {checked}disabled=""> {self._escape_html(token.content)}</div>')
            elif token.type == "hr":
                body_html.append("<hr/>")
            elif token.type == "paragraph":
                body_html.append(f"<p>{self._render_inline_html(token.content)}</p>")

        content = "\n".join(body_html)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{self._escape_html(title)}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.6;
      max-width: 800px;
      margin: 40px auto;
      padding: 0 20px;
      color: #24292e;
      background-color: #ffffff;
    }}
    h1, h2, h3, h4, h5, h6 {{
      margin-top: 24px;
      margin-bottom: 16px;
      font-weight: 600;
      line-height: 1.25;
    }}
    h1 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
    h2 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
    code {{
      font-family: 'Consolas', 'Courier New', monospace;
      background-color: #f6f8fa;
      padding: 0.2em 0.4em;
      border-radius: 3px;
      font-size: 85%;
    }}
    pre {{
      background-color: #f6f8fa;
      padding: 16px;
      overflow: auto;
      border-radius: 6px;
      line-height: 1.45;
    }}
    pre code {{ background: none; padding: 0; font-size: 100%; }}
    blockquote {{
      padding: 0 1em;
      color: #6a737d;
      border-left: 0.25em solid #dfe2e5;
      margin: 0 0 16px 0;
    }}
    hr {{ height: 0.25em; padding: 0; margin: 24px 0; background-color: #e1e4e8; border: 0; }}
  </style>
</head>
<body>
{content}
</body>
</html>"""

    def _render_inline_html(self, text: str) -> str:
        inlines = self.parse_inline_elements(text)
        parts = []
        for item in inlines:
            t = item["type"]
            val = self._escape_html(item.get("value", ""))
            if t == "text":
                parts.append(val)
            elif t == "bold":
                parts.append(f"<strong>{val}</strong>")
            elif t == "italic":
                parts.append(f"<em>{val}</em>")
            elif t == "code":
                parts.append(f"<code>{val}</code>")
            elif t == "strike":
                parts.append(f"<del>{val}</del>")
            elif t == "link":
                name = self._escape_html(item.get("text", ""))
                url = self._escape_html(item.get("url", ""))
                parts.append(f'<a href="{url}">{name}</a>')
        return "".join(parts)

    @staticmethod
    def _escape_html(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
