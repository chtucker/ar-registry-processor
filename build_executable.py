#!/usr/bin/env python3
"""
Build script for creating a standalone executable of the Arkansas Registry Processor.
This script uses PyInstaller to create a Windows executable that includes all dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("Success")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main build process"""
    print("=" * 60)
    print("Arkansas Registry Processor - Executable Builder")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("gui/main_app.py"):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Create dist directory
    dist_dir = Path("dist")
    if dist_dir.exists():
        print("Cleaning previous build...")
        shutil.rmtree(dist_dir)
    
    # Create build directory
    build_dir = Path("build")
    if build_dir.exists():
        print("Cleaning previous build files...")
        shutil.rmtree(build_dir)
    
    # Install dependencies
    if not run_command("pip3 install -r requirements_gui.txt", "Installing dependencies..."):
        print("Failed to install dependencies")
        sys.exit(1)
    
    # Create PyInstaller spec file content
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui/main_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'selenium.common.exceptions',
        'openpyxl',
        'pandas',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.random._pickle',
        'IPython',
        'jupyter'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Arkansas_Registry_Processor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    # Write spec file
    with open("registry_processor.spec", "w") as f:
        f.write(spec_content)
    
    print("Created PyInstaller spec file")
    
    # Build the executable  
    build_cmd = "pyinstaller --clean registry_processor.spec"
    if not run_command(build_cmd, "Building executable with PyInstaller..."):
        print("Failed to build executable")
        sys.exit(1)
    
    # Check if executable was created (handle different platforms)
    exe_path_windows = Path("dist/Arkansas_Registry_Processor.exe")
    exe_path_unix = Path("dist/Arkansas_Registry_Processor")
    
    if exe_path_windows.exists():
        exe_path = exe_path_windows
    elif exe_path_unix.exists():
        exe_path = exe_path_unix
    else:
        print("\n✗ Executable not found in expected location")
        sys.exit(1)
    
    print(f"\n✓ Executable created successfully!")
    print(f"Location: {exe_path.absolute()}")
    print(f"Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    
    # Create documentation
    readme_content = """# Arkansas Registry Processor

## About
This application processes Excel files against the Arkansas Sex Offender Registry website.

## Requirements
- Windows 10 or later
- Internet connection
- Chrome browser (for ChromeDriver compatibility)

## Usage
1. Double-click `Arkansas_Registry_Processor.exe` to launch the application
2. Click "Browse..." to select your Excel file (.xlsx format)
3. Ensure your Excel file has:
   - Column B: First Name
   - Column D: Last Name  
   - Column G: Gender (male/female/unknown)
   - Data starting from row 4
4. Choose where to save the results (defaults to Desktop)
5. Click "Start Processing" and wait for completion
6. Results will be saved as an Excel file with processing status

## Results
The output Excel file will contain:
- Original data (First Name, Last Name, Gender)
- Result column: "no results found" or "warning"
- Processing timestamp

## Support
For technical issues, contact your IT department.

## Version
Built: {build_date}
"""
    
    from datetime import datetime
    readme_path = dist_dir / "README.txt"
    with open(readme_path, "w") as f:
        f.write(readme_content.format(build_date=datetime.now().strftime("%Y-%m-%d %H:%M")))
    
    print(f"Created documentation: {readme_path}")
    
    # Clean up build files
    print("\nCleaning up build files...")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if os.path.exists("registry_processor.spec"):
        os.remove("registry_processor.spec")
    
    print("\n" + "=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    print(f"Executable: {exe_path.absolute()}")
    print(f"Documentation: {readme_path.absolute()}")
    print("\nTo distribute:")
    print("1. Copy the entire 'dist' folder to the target machine")
    print("2. Ensure Chrome browser is installed on the target machine")
    print("3. Run Arkansas_Registry_Processor.exe")

if __name__ == "__main__":
    main() 