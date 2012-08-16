import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "includes": ["AppKit"], "excludes": ["tkinter"], "include_files": [("cat.png", "cat.png"), ("cat.ico", "cat.ico"), ("setting.json", "setting.json")], "icon": "cat.ico"}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "meow",
        version = "0.1",
        description = "My GUI application!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("meow.py", base=base)])
