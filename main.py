import sys
import os
from markdown_editor.core.parser import MarkdownEngine


def run_cli_export(input_file: str, output_file: str) -> int:
    """Converts a markdown file to standalone HTML via CLI."""
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
        return 1

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
        engine = MarkdownEngine()
        title = os.path.splitext(os.path.basename(input_file))[0]
        html = engine.to_html(content, title=title)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Successfully converted '{input_file}' -> '{output_file}'")
        return 0
    except Exception as e:
        print(f"Conversion failed: {e}", file=sys.stderr)
        return 1


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--export":
        sys.exit(run_cli_export(sys.argv[2], sys.argv[3]))

    from markdown_editor.ui.app import MarkdownStudioApp
    app = MarkdownStudioApp()
    app.mainloop()


if __name__ == "__main__":
    main()
