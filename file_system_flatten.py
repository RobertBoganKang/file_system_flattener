import glob
import os
import subprocess

# the name of restore script
restore_script = '#restore.sh'


def open_fs(folder):
    """
    flatten the file system to the current folder
    :param folder: str; target folder to flatten
    :return: None
    """
    print('=' * 50)
    print('Reading file system ~')
    # search files
    fs = glob.glob(os.path.join(folder, '**/*'), recursive=True)
    # search hidden files
    fs = fs + glob.glob(os.path.join(folder, '**/.*'), recursive=True)
    # select files
    fs_file = [x for x in fs if os.path.isfile(x)]
    fs_folder = [x for x in fs if os.path.isdir(x)]
    fs_file.sort()
    fs_folder.sort()
    print('Flatten file system ~')
    # write move script to file
    restore_have = False
    if os.path.exists(os.path.join(folder, restore_script)):
        restore_have = True
    with open(os.path.join(folder, restore_script), 'a+') as shell:
        if not restore_have:
            # bash header
            shell.write('#!/bin/bash\n')
            # enter the current pwd for the file
            shell.write('p=$(cd `dirname $0`; pwd)\n')
            # write folder creation script
            for f in fs_folder:
                folder_creation_command = ['mkdir', os.path.join('$p', f[len(folder) + 1:].replace(' ', '\\ '))]
                shell.write(' '.join(folder_creation_command))
                shell.write('\n')

        # flatten the file and write the script
        for file in fs_file:
            file_name = file[len(folder) + 1:].replace('/', '__').replace('\\', '__')
            target_path = os.path.join(folder, file_name)
            if file != target_path:
                mv_command = ['mv', file, target_path]
                restore_mv_command = ['mv', os.path.join('$p', file_name.replace(' ', '\\ ')),
                                      os.path.join('$p', file[len(folder) + 1:].replace(' ', '\\ '))]
                # write restoration script first in case of unwanted stop
                shell.write(' '.join(restore_mv_command))
                shell.write('\n')
                # then move the file
                subprocess.run(mv_command)

        # remove folders reversely
        fs_folder.reverse()
        for f in fs_folder:
            folder_remove_command = ['rm', '-R', f]
            subprocess.run(folder_remove_command)

    print('Done flattening.')
    print('=' * 50)


def close_fs(folder):
    """
    restore the file system to original state
    :param folder: str;
    :return: None
    """
    print('=' * 50)
    print('Restore file system ~')
    subprocess.run(['bash', os.path.join(folder, restore_script)])
    subprocess.run(['rm', os.path.join(folder, restore_script)])
    print('Done restoration.')
    print('=' * 50)


if __name__ == '__main__':
    open_fs('in')
    close_fs('in')
