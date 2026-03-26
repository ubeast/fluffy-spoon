from clean_empty_notebooks   import run as clean_notebooks
from clean_empty_dirs        import run as clean_dirs
from clean_empty_text_files  import run as clean_files

path = "."

clean_notebooks(path, delete=True)
clean_dirs(path,      delete=True)
clean_files(path,     delete=True)
