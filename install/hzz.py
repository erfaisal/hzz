# hzz.py
import argparse
import json
import os
import shutil
import site
import sys
import urllib.request
import zipfile
from pathlib import Path

# Base server URL hosting your packages
REPO_URL = "https://hzz.cupx.in/pkg"

def get_site_packages():
    """Returns the site-packages path of the active Python environment."""
    return site.getsitepackages()[0]

def install(package_name):
    # 1. Updated terminal message
    print(f"Connecting to CupX system (on- hzz.cupx.in/pkg)...")
    
    site_packages = Path(get_site_packages())
    
    # 2. Check if already installed (looks for the .dist-info folder)
    existing_install = list(site_packages.glob(f"{package_name}-*.dist-info"))
    if existing_install:
        print(f"Requirement already satisfied: {package_name}")
        return

    temp_dir = Path(os.getenv("TEMP")) / "hzz_downloads"
    temp_dir.mkdir(exist_ok=True)
    wheel_path = None
    
    try:
        meta_url = f"{REPO_URL}/{package_name}/index.json"
        with urllib.request.urlopen(meta_url) as response:
            metadata = json.loads(response.read().decode())
        
        wheel_name = metadata["latest_wheel"]
        wheel_url = f"{REPO_URL}/{package_name}/{wheel_name}"
        wheel_path = temp_dir / wheel_name
        
        print(f"Downloading {wheel_name}...")
        urllib.request.urlretrieve(wheel_url, wheel_path)
        
        print(f"Installing {package_name}...")
        with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
            zip_ref.extractall(site_packages)
            
        print(f"Successfully installed '{package_name}'! You can now use 'import {package_name}' in Python.")
        
    except Exception as e:
        print(f"Error: Could not install '{package_name}'. Details: {e}")
    finally:
        if wheel_path and wheel_path.exists():
            try:
                wheel_path.unlink()
            except PermissionError:
                pass

def uninstall(package_name):
    site_packages = Path(get_site_packages())
    
    dist_info_dirs = list(site_packages.glob(f"{package_name}-*.dist-info"))
    if not dist_info_dirs:
        print(f"Package '{package_name}' not found.")
        return
        
    print(f"Uninstalling '{package_name}'...")
    dist_info = dist_info_dirs[0]
    record_file = dist_info / "RECORD"
    
    if record_file.exists():
        # 3. Read lines into memory FIRST, then close the file immediately
        with open(record_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Now it is safe to loop through and delete because the file is closed
        for line in lines:
            file_path = line.split(',')[0]
            full_path = site_packages / file_path
            
            # Delete files if they exist
            if full_path.exists() and full_path.is_file():
                try:
                    full_path.unlink()
                except PermissionError:
                    # Skips any file that might be locked by another program
                    pass 
        
        # Finally, delete the .dist-info folder itself
        try:
            shutil.rmtree(dist_info)
            print(f"Successfully uninstalled '{package_name}'.")
        except PermissionError:
            print(f"Warning: Cleaned up files, but could not remove folder {dist_info.name}.")
    else:
        print("RECORD file missing. Cannot safely uninstall.")

def list_packages():
    site_packages = Path(get_site_packages())
    print("Installed Python packages:")
    print("-------------------------")
    dist_dirs = sorted(site_packages.glob("*.dist-info"))
    count = 0
    for d in dist_dirs:
        parts = d.name.replace(".dist-info", "").split("-")
        name = parts[0]
        version = parts[1] if len(parts) > 1 else "unknown"
        print(f" - {name} ({version})")
        count += 1
    if count == 0:
        print("No packages found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CupX Package Manager (hzz)")
    parser.add_argument("command", choices=["install", "uninstall", "list"], help="Action to perform")
    parser.add_argument("package", nargs="?", default="", help="Target package name (for install/uninstall)")
    
    args = parser.parse_args()
    
    if args.command == "install":
        if not args.package:
            print("Error: Please specify a package name (e.g., hzz install xyz)")
        else:
            install(args.package)
    elif args.command == "uninstall":
        if not args.package:
            print("Error: Please specify a package name (e.g., hzz uninstall xyz)")
        else:
            uninstall(args.package)
    elif args.command == "list":
        list_packages()
