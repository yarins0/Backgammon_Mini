import os
import sys

# When PyInstaller bundles support files into _internal/, the bootloader
# sets sys._MEIPASS to that directory using the exe's own path — not the
# current working directory. Adding it here lets Windows find python313.dll
# and other DLLs regardless of which directory the exe is launched from.
if sys.platform == "win32" and hasattr(sys, "_MEIPASS"):
    os.add_dll_directory(sys._MEIPASS)
