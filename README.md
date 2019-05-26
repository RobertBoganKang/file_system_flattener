# File System Flattener
## Introduction
This script will flatten the directory in only one master folder, and can restore. 

This script support multiple systems and is code-wise safely.
## Function
Initialize the class with: `FileSystemFlatten(<target_folder>)`, then use functions.
* open_fs(): flatten the file system.
* close_fs(): restore the file system (by python).

The dropout file `#restore.sh` or `#restore.bat` is the script that can restore the file system.
## Usage
```bash
python3 file_system_flatten.py -i <target_folder> -r
```
* `-i` input folder.
* `-r` if have: restore, not have: flatten.
