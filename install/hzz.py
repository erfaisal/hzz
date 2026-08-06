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
    print(f"Connecting to CupX repository ({REPO_URL})...")
    site_packages = get_site_packages()
    temp_dir = Path(os.getenv("TEMP")) / "hzz_temp"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # 1. Fetch package metadata JSON from server
        meta_url = f"{REPO_URL}/{package_name}/index.json"
        req = urllib.request.Request(meta_url, headers={'User-Agent': 'hzz-cli'})
        with urllib.request.urlopen(req) as response:
            metadata = json.loads(response.read().decode('utf-8'))
        
        wheel_name = metadata["latest_wheel"]
        wheel_url = f"{REPO_URL}/{package_name}/{wheel_name}"
        wheel_path = temp_dir / wheel_name
        
        # 2. Download .whl archive
        print(f"Downloading {wheel_name}...")
        urllib.request.urlretrieve(wheel_url, wheel_path)
        
        # 3. Unzip wheel directly into site-packages
        print(f"Installing {package_name}...")
        with zipfile.ZipFile(wheel_path, 'r') as zip_ref:
            zip_ref.extractall(site_packages)
            
        print(f"Successfully installed '{package_name}'! You can now use 'import {package_name}' in Python.")
        
    except Exception as e:
        print(f"Error: Could not install '{package_name}'. Details: {e}")
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

def uninstall(package_name):
    site_packages = Path(get_site_packages())
    print(f"Uninstalling '{package_name}'...")
    
    # Locate package distribution info folder
    dist_dirs = list(site_packages.glob(f"{package_name}-*.dist-info")) + \
                list(site_packages.glob(f"{package_name.replace('-', '_')}-*.dist-info"))
    
    if not dist_dirs:
        print(f"Package '{package_name}' is not installed.")
        return
        
    dist_info = dist_dirs[0]
    record_file = dist_info / "RECORD"
    
    if record_file.exists():
        with open(record_file, 'r', encoding='utf-8') as f:
            for line in f:
                rel_path = line.split(',')[0].strip()
                full_path = site_packages / rel_path
                if full_path.is_file():
                    full_path.unlink(missing_ok=True)
        shutil.rmtree(dist_info, ignore_errors=True)
        print(f"Successfully uninstalled '{package_name}'.")
    else:
        print(f"Missing install manifest for '{package_name}'. Cannot clean automatically.")

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
