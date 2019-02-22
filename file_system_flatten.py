import argparse
import glob
import os
import platform
import shutil
import subprocess
from itertools import groupby


class ScriptUtils(object):
    @staticmethod
    def add_quote(string):
        """
        add quote for the path
        :param string: str; path
        :return: str; quoted path
        """
        return '\"' + string + '\"'


class BashScript(ScriptUtils):
    """Linux, Mac OS"""

    def __init__(self, in_folder, separator, restore):
        # the name of restore script
        self.restore_script = restore + '.sh'
        # separator of file name
        self.separator = separator
        # input folder
        self.input = os.path.abspath(in_folder)

    @staticmethod
    def write_header_script(shell):
        """write header of shell"""
        # bash header
        shell.write('#!/bin/bash\n')
        # enter the current pwd for the file
        shell.write('p=$(cd `dirname $0`; pwd)\n')
        # get the file name
        shell.write('n=`realpath $0`\n')

    def write_folder_creation_script(self, shell, fs_folder):
        """write folder creation script"""
        for f in fs_folder:
            folder_creation_command = ['mkdir', self.add_quote(os.path.join('$p', f[len(self.input) + 1:]))]
            shell.write(' '.join(folder_creation_command))
            shell.write('\n')

    def write_move_script(self, shell, file, file_name):
        """write restore move script"""
        restore_mv_command = ['mv', self.add_quote(os.path.join('$p', file_name)),
                              self.add_quote(os.path.join('$p', file[len(self.input) + 1:]))]
        shell.write(' '.join(restore_mv_command))
        shell.write('\n')

    @staticmethod
    def write_self_remove_script(shell):
        """write self remove script"""
        shell.write('rm $n\n')

    def run_script(self):
        """run"""
        subprocess.Popen(['bash', os.path.join(self.input, self.restore_script)])


class BatchScript(ScriptUtils):
    """Windows"""

    def __init__(self, in_folder, separator, restore):
        # the name of restore script
        self.restore_script = restore + '.bat'
        # separator of file name
        self.separator = separator
        # input folder
        self.input = os.path.abspath(in_folder)

    @staticmethod
    def write_header_script(shell):
        """write header of shell"""
        # batch header
        shell.write('@ echo off\n')
        # enter the current pwd for the file
        shell.write('set p=%~dp0\n')
        # get the file name
        shell.write('set n=%~f0\n')

    def write_folder_creation_script(self, shell, fs_folder):
        """write folder creation script"""
        for f in fs_folder:
            folder_creation_command = ['md', self.add_quote(os.path.join('%p%', f[len(self.input) + 1:]))]
            shell.write(' '.join(folder_creation_command))
            shell.write('\n')

    def write_move_script(self, shell, file, file_name):
        """write restore move script"""
        restore_mv_command = ['move', self.add_quote(os.path.join('%p%', file_name)),
                              self.add_quote(os.path.join('%p%', file[len(self.input) + 1:]))]
        shell.write(' '.join(restore_mv_command))
        shell.write('\n')

    @staticmethod
    def write_self_remove_script(shell):
        """write self remove script"""
        shell.write('del \"%n%\"\n')

    def run_script(self):
        """run"""
        subprocess.Popen(os.path.join(self.input, self.restore_script), shell=True, stdout=subprocess.PIPE)


class FileSystemFlatten(object):
    """
    flatten and restore the file system
    """

    def __init__(self, in_folder):
        # the name of restore script
        self.restore = '#restore'
        # separator of file name
        self.separator = '__'
        # input folder
        self.input = os.path.abspath(in_folder)
        # get system
        self.system = platform.system()
        # the full name of restore script
        self.restore_script = None
        # get script class
        self.script = self.get_script_class()

    def delete_repeat(self):
        """
        delete the repeated script since unwanted stop will create twice
        :return: None
        """
        path = os.path.join(self.input, self.restore_script)
        # rebuild restoration file
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

    def get_script_class(self):
        """return script class and set script name (poly-morphism)"""
        if self.system == 'Windows':
            script = BatchScript(self.input, self.separator, self.restore)
        else:
            script = BashScript(self.input, self.separator, self.restore)
        self.restore_script = script.restore_script
        return script

    def open_fs(self):
        """
        flatten the file system to the current folder
        :return: None
        """
        print('=' * 50)
        print('-->[{}] flattening ~'.format(self.input))
        # start operation
        print('\r~~>[Read|-->...', end='')
        # search files
        fs = glob.glob(os.path.join(self.input, '**/*'), recursive=True)
        # search hidden files
        fs = fs + glob.glob(os.path.join(self.input, '**/.*'), recursive=True)
        # select files
        fs_file = [x for x in fs if os.path.isfile(x)]
        fs_folder = [x for x in fs if os.path.isdir(x)]
        fs_file.sort()
        fs_folder.sort()
        print('\r~~>[Flatten|-->...', end='')
        # write move script to file
        restore_have = False
        if os.path.exists(os.path.join(self.input, self.restore_script)):
            restore_have = True
        with open(os.path.join(self.input, self.restore_script), 'a+') as shell:
            if not restore_have:
                self.script.write_header_script(shell)
                # write folder creation script
                self.script.write_folder_creation_script(shell, fs_folder)

            # flatten the file and write the script
            for file in fs_file:
                file_name = file[len(self.input) + 1:].replace('/', self.separator).replace('\\', self.separator)
                target_path = os.path.join(self.input, file_name)
                if file != target_path:
                    # write restoration script first in case of unwanted stop
                    # the program may write move script twice if stop
                    self.script.write_move_script(shell, file, file_name)

                    # then move the file
                    shutil.move(file, target_path)

            # write self remove script finally
            self.script.write_self_remove_script(shell)

            # remove folders reversely
            fs_folder.reverse()
            for f in fs_folder:
                shutil.rmtree(f)
        # clean the script
        self.delete_repeat()
        print('\r~~>[Flatten|-->|Done]')
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
        print('\r~~>[Restore|-->...', end='')
        self.script.run_script()
        print('\r~~>[Restore|-->|Done]')
        print('=' * 50)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='flatten and restore the file system')
    parser.add_argument('--input', '-i', help='the target folder for operation', type=str, default='in')
    parser.add_argument('--restore', '-r', action='store_true', help='if have: restore the file system')
    arg = parser.parse_args()

    flatten = FileSystemFlatten(arg.input)
    if arg.restore:
        flatten.close_fs()
    else:
        flatten.open_fs()
