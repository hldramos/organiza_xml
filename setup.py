import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUi"

executables = [
    Executable(
        script="main.py",
        base=base,
    )
]

build_exe_options = {"packages": ["xmltodict"]}

setup(
    name="Indexar xml de NF-e e MDF-e",
    version="0.1.2",
    description="Organizar xml de NF-e e MDF-e por CNPJ do emitente",
    options={"build_exe": build_exe_options},
    executables=executables,
)
