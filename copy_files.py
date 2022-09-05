#!/usr/bin/env python

import os
import sys
import shutil
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

is_piped_or_redirected_to_file = not sys.stdout.isatty()
files = open("files.txt").read()[:-1].split('\n')
exclude_list = open("exclude.txt").read()[:-1].split('\n')
parent_folder = ".rootfs.tmp"

def log(lvl, fmt):
    global is_piped_or_redirected_to_file
    if is_piped_or_redirected_to_file:
        if lvl == "OK":
            print(f"[+] {fmt}")
        elif lvl == "WARNING":
            print(f"[!] {fmt}")
        elif lvl == "FAIL":
            print(f"[-] {fmt}")
        else:
            print(f"[-] Wrong lvl specified. ('{lvl}')")
    else:
        if lvl == "OK":
            print(f"{bcolors.OKGREEN}[+] {fmt}{bcolors.ENDC}")
        elif lvl == "WARNING":
            print(f"{bcolors.WARNING}[!] {fmt}{bcolors.ENDC}")
        elif lvl == "FAIL":
            print(f"{bcolors.FAIL}[-] {fmt}{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}[-] Wrong lvl specified. ('{lvl}'){bcolors.ENDC}")

for file in files:
    for root, dirs, files in os.walk(file):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(parent_folder, src[1:])
            dst_parent_dir = dst[:dst.rfind('/')]

            if os.path.join(root, file) not in exclude_list:
                if not os.path.exists(dst_parent_dir):
                    os.makedirs(dst_parent_dir)
                try:
                    shutil.copy2(src, dst, follow_symlinks=False)
                    log("OK", f"Copied '{src}' to '{dst}'")
                except Exception as e:
                    log("FAIL", f"Error copying '{src}': Exception '{e}' occured")
            else:
                log("WARNING", f"Skipping '{src}' because it was found in exclude list.")

        for dir in dirs:
            if os.path.join(root, dir) in exclude_list:
                dirs.remove(dir)
                log("WARNING", f"Skipping '{os.path.join(root, dir)}' because it was found in exclude list.")

for root, dirs, files in os.walk(parent_folder):
    for dir in dirs:
        original_path = os.path.join(root, dir)[len(parent_folder):]
        if not os.path.islink(original_path):
            st = os.stat(original_path)
            os.chown(os.path.join(root, dir), st.st_uid, st.st_gid)

    for file in files:
        original_path = os.path.join(root, file)[len(parent_folder):]
        if not os.path.islink(original_path):
            st = os.stat(original_path)
            os.chown(os.path.join(root, file), st.st_uid, st.st_gid)

log("OK", "Backup created! Creating tar archive...")
subprocess.run([ "bash", "-c", f"cd {parent_folder} && tar cf ../rootfs.tar ." ])

#log("OK", "Tar archive created! Compressing it with `xz`...")
#subprocess.run([ "xz", "-v", "-T", "4", "rootfs.tar" ])

shutil.chown("rootfs.tar", 1000, 1000)
shutil.rmtree(parent_folder)

log("OK", "Done!")
