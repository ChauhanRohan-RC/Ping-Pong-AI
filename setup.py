from cx_Freeze import setup, Executable
import sys
import R

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "random", "threading", "io"],
                     "includes": ["pygame", ],
                     "excludes": ["numpy", "tkinter", ]}

# GUI applications require a different base on Windows (the default is for a
# console application).

base = None
if sys.platform == 'win32':
    base = "Win32GUI"

client = Executable(
    script="pong_client.py",
    targetName=R.DISPLAY_TITLE,
    base=base,
    icon=R.FILE_PATH_IMG_EXE_ICON
    )

setup(
    name=R.EXE_NAME,
    version=R.EXE_VERSION,
    description=R.DISPLAY_DESCRIPTION,
    author=R.DISPLAY_AUTHOR,
    options={"build_exe": build_exe_options},
    executables=[client, ], requires=['pygame'])
