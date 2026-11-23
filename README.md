# Markdown Studio

A lightweight, modern desktop Markdown Editor built with Python and Tkinter.

## Features

- **Dual-Pane Live Preview**: Synchronized Markdown source and formatted visual display.
- **Syntax Highlighting**: Real-time syntax coloring in the editor for headers, code blocks, lists, and inline styles.
- **Document Outline**: Automatic Table of Contents generator parsed directly from headers.
- **Document Statistics**: Live word count, character count, sentence count, and estimated reading time.
- **Dual Themes**: Built-in Dark and Light modern editor themes.
- **Export Engine**: Export documents to clean standalone HTML or raw Markdown.
- **Line Numbers & Shortcuts**: Fast navigation, line numbers, and formatting shortcuts (Ctrl+B, Ctrl+I, Ctrl+K, Ctrl+S).

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

To launch the GUI:
```bash
python main.py
```

To convert a Markdown file to HTML directly from the command line:
```bash
python main.py --export input.md output.html
```

## Running Tests

```bash
pytest
```
