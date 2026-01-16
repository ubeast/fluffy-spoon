from IPython.display import Markdown, display

def display_markdown_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    display(Markdown(content))
