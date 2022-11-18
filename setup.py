from cx_Freeze import setup, Executable
import os
import sys

os.environ['TCL_LIBRARY'] = 'C:/Users/user/anaconda3/tcl/tcl8.6'
os.environ['TK_LIBRARY'] = 'C:/Users/user/anaconda3/tcl/tk8.6'

path_platforms = (
    "C:/Users/user/anaconda3/pkgs/qt-5.9.7-vc14h73c81de_0/Library/plugins/platforms/qwindows.dll",
    "platfors/qwindows.dll"
)

includes = [
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    "requests"
]

includefiles = [path_platforms]

excludes= []

packages = ["os"]
path = []

build_exe_options = {
    "includes"      :   includes,
    "include_files":   includefiles,
    "excludes"      :   excludes,
    "packages"      :   packages,
    "path"          :   path
}

base = None
exe = None

if sys.platform == "win32":
    exe = Executable(
        script = "main.py", 
        initScript= None,
        base = 'Win32GUI',
        target_name="Twitch Recorder.exe",
        icon = None
    )
    
setup(
    name = 'Twitch Recorder',
    version='0.1.0',
    author='engui',
    description='Twitch Recorder beta 0.1.0',
    options = dict(build_exe = build_exe_options),
    executables = [exe]
)