import argparse
import glob
import os
import subprocess
from itertools import groupby


class FileSystemFlatten(object):
    """
    flatten and restore the file system
    """

    def __init__(self, in_folder):
        # the name of restore script
        self.restore_script = '#restore.sh'
        # separator of file name
        self.separator = '__'
        # input folder
        self.input = os.path.abspath(in_folder)

    @staticmethod
    def add_quote(string):
        """
        add quote for the path
        :param string: str; path
        :return: str; quoted path
        """
        return '\"' + string + '\"'

    def delete_repeat(self):
        """
        delete the repeated script since unwanted stop will create
        :return: None
        """
        path = os.path.join(self.input, self.restore_script)
        # rebuild restoration file
        rebuild_lines = []
        with open(path, 'r') as r:
            lines = r.readlines()
            lines = [x.strip() for x in lines]
            # detect repeat and delete
            rebuild_lines = [x[0] for x in groupby(lines)]

        # rewrite file
        with open(path, 'w+') as r:
            for l in rebuild_lines:
                r.write(l)
                r.write('\n')

    def open_fs(self):
        """
        flatten the file system to the current folder
        :return: None
        """
        print('=' * 50)
        print('-->[{}] flattening ~'.format(self.input))
        # start operation
        print('\r~~>[Read...', end='')
        # search files
        fs = glob.glob(os.path.join(self.input, '**/*'), recursive=True)
        # search hidden files
        fs = fs + glob.glob(os.path.join(self.input, '**/.*'), recursive=True)
        # select files
        fs_file = [x for x in fs if os.path.isfile(x)]
        fs_folder = [x for x in fs if os.path.isdir(x)]
        fs_file.sort()
        fs_folder.sort()
        print('\r~~>[Read|-->|Flatten...', end='')
        # write move script to file
        restore_have = False
        if os.path.exists(os.path.join(self.input, self.restore_script)):
            restore_have = True
        with open(os.path.join(self.input, self.restore_script), 'a+') as shell:
            if not restore_have:
                # bash header
                shell.write('#!/bin/bash\n')
                # enter the current pwd for the file
                shell.write('p=$(cd `dirname $0`; pwd)\n')
                # get the file name
                shell.write('n=${0##*/}\n')
                # write folder creation script
                for f in fs_folder:
                    folder_creation_command = ['mkdir', self.add_quote(os.path.join('$p', f[len(self.input) + 1:]))]
                    shell.write(' '.join(folder_creation_command))
                    shell.write('\n')

            # flatten the file and write the script
            for file in fs_file:
                file_name = file[len(self.input) + 1:].replace('/', self.separator)
                target_path = os.path.join(self.input, file_name)
                if file != target_path:
                    mv_command = ['mv', file, target_path]
                    restore_mv_command = ['mv', self.add_quote(os.path.join('$p', file_name)),
                                          self.add_quote(os.path.join('$p', file[len(self.input) + 1:]))]
                    # write restoration script first in case of unwanted stop
                    # the program may write move script twice if stop
                    shell.write(' '.join(restore_mv_command))
                    shell.write('\n')
                    # then move the file
                    subprocess.run(mv_command)

            # write delete file script finally
            shell.write('rm ' + self.add_quote(os.path.join('$p', '$n')))
            shell.write('\n')

            # clean the script
            self.delete_repeat()

            # remove folders reversely
            fs_folder.reverse()
            for f in fs_folder:
                folder_remove_command = ['rm', '-R', f]
                subprocess.run(folder_remove_command)

        print('\r~~>[Read|-->|Flatten|-->|Done]')
        print('=' * 50)

    def close_fs(self):
        """
        restore the file system to original state
        :return: None
        """
        if not os.path.exists(os.path.join(self.input, self.restore_script)):
            print('Restore script missing!!')
            return
        print('=' * 50)
        print('-->[{}] restoring ~'.format(self.input))
        print('\r~~>[Restore...', end='')
        subprocess.run(['bash', os.path.join(self.input, self.restore_script)])
        print('\r~~>[Restore|-->|Done]')
        print('=' * 50)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='flatten and restore the file system')
    parser.add_argument('--input', '-i', help='the target folder for operation', type=str, default='in')
    parser.add_argument('--restore', '-r', action='store_true', help='if have: restore the file system')
    args = parser.parse_args()

    flatten = FileSystemFlatten(args.input)
    if args.restore:
        flatten.close_fs()
    else:
        flatten.open_fs()
