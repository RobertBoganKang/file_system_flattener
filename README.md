# File System Flattener (need bash support)
## Introduction
This script will flatten the file system in only one folder, and can restore. This script is code-wise safely.
## Function
Initialize the class with: `FileSystemFlatten(<target_folder>)`, then use functions.
* open_fs(): flatten the file system.
* close_fs(): restore the file system (by python).

The dropout file '#restore.sh' is the script that can restore the file system.
## Usage
```bash
python3 -i <target_folder> -r
```
* `-i` input folder.
* `-r` if have: restore, not have: flatten.
