import zipfile
import tarfile
from zipfile import ZipFile
import sys


def interaction_cycle(filesystem_image_read, archive_type):
    current_dir = ""
    current_dir_short = ""
    commands = ("ls", "cat", "pwd", "cd", "")
    if archive_type == "zip":
        all_files = filesystem_image_read.namelist()
    elif archive_type == "tar":
        all_files = filesystem_image_read.getnames()
        for i in range(len(all_files)):
            if filesystem_image_read.getmember(all_files[i]).isdir():
                all_files[i] += '/'
    else:
        return
    while True:
        print(f"[me@vshell {current_dir_short if current_dir else '~'}]$ ", end='')

        input_command = input().split()

        if len(input_command) == 0:
            continue

        if input_command[0] not in commands:
            print(f"vshell: {input_command[0]}: command not found")

        elif input_command[0] == "ls":
            print_ls(all_files, current_dir, input_command)

        elif input_command[0] == "cat":
            for command in input_command[1:]:
                if command == '.' or command == ".." or command == '/':
                    print(f"{input_command[0]}: {command}: Is a directory")
                    continue
                elif command[0] == '/':
                    check_file = command[1:]
                else:
                    check_file = current_dir + command
                if check_file in all_files:
                    cat_for_current_dir(filesystem_image_read, all_files, check_file, archive_type)
                elif check_file + '/' in all_files:
                    cat_for_current_dir(filesystem_image_read, all_files, check_file + '/', archive_type)
                else:
                    print(f"{input_command[0]}: {command}: No such file or directory")

        elif input_command[0] == "pwd":
            if current_dir == "":
                print('/')
            else:
                print('/' + current_dir[0:-1])

        elif input_command[0] == "cd":
            current_and_short_dir = cd_handler(input_command, current_dir, all_files)
            if current_and_short_dir[0] is not None:
                current_dir = current_and_short_dir[0]
            if current_and_short_dir[1] is not None:
                current_dir_short = current_and_short_dir[1]


def print_ls(all_files, current_dir, input_command):
    if len(input_command) == 1:
        ls_for_current_dir(all_files, current_dir)
        print()
    else:
        if len(input_command) > 2:
            for command in input_command[1:]:
                if command == '.':
                    print(".:")
                    ls_for_current_dir(all_files, current_dir)
                    print()
                    continue
                elif command == "..":
                    print("..:")
                    if current_dir[:-1].rfind('/') != -1:
                        ls_for_current_dir(all_files, current_dir[:current_dir[:-1].rfind('/') + 1])
                    else:
                        ls_for_current_dir(all_files, "")
                    print()
                    continue
                elif command == "/":
                    print("/:")
                    ls_for_current_dir(all_files, "")
                    print()
                    continue
                elif command[0] != '/':
                    if command.endswith('/'):
                        check_directory = current_dir + command
                    else:
                        check_directory = current_dir + command + '/'
                else:
                    if command.endswith('/'):
                        check_directory = command[1:]
                    else:
                        check_directory = command[1:] + '/'

                if check_directory in all_files:
                    print(f"{check_directory[:-1]}:")
                    ls_for_current_dir(all_files, check_directory)
                else:
                    print(f"{input_command[0]}: cannot access '{command}': No such file or directory")
                print()
        else:
            for command in input_command[1:]:
                if command == '.':
                    ls_for_current_dir(all_files, current_dir)
                    print()
                    continue
                elif command == "..":
                    if current_dir[:-1].rfind('/') != -1:
                        ls_for_current_dir(all_files, current_dir[:current_dir[:-1].rfind('/') + 1])
                    else:
                        ls_for_current_dir(all_files, "")
                    print()
                    continue
                elif command == "/":
                    ls_for_current_dir(all_files, "")
                    print()
                    continue
                elif command[0] != '/':
                    if command.endswith('/'):
                        check_directory = current_dir + command
                    else:
                        check_directory = current_dir + command + '/'
                else:
                    if command.endswith('/'):
                        check_directory = command[1:]
                    else:
                        check_directory = command[1:] + '/'

                if check_directory in all_files:
                    ls_for_current_dir(all_files, check_directory)
                else:
                    print(f"{input_command[0]}: cannot access '{command}': No such file or directory")
                print()


def ls_for_current_dir(all_files, current_dir):
    for file in all_files:
        file_suffix = file[len(current_dir):]
        if file_suffix == "":
            continue
        if file.find(current_dir) == 0:
            if file_suffix.find('/') == -1:
                print(file[len(current_dir):], end=" ")
            elif file_suffix.find('/') == (len(file_suffix) - 1):
                print("\033[34m" + file[len(current_dir):-1] + "\033[0m", end=" ")


def cat_for_current_dir(filesystem_image_read, all_files, current_file, archive_type):
    if current_file.endswith('/'):
        print(f"cat: {current_file[0:-1]}: Is a directory")
    else:
        if archive_type == "zip":
            print(filesystem_image_read.read(current_file).decode("utf-8"))
        elif archive_type == "tar":
            file = filesystem_image_read.extractfile(filesystem_image_read.getmember(current_file))
            print(file.read().decode("utf-8"))


def cd_handler(input_command, current_dir, all_files):
    if len(input_command) == 1 or input_command[1] == '~':
        return ["", ""]
    elif len(input_command) > 2:
        print(f"vshell: {input_command[0]}: too many arguments")
        return [None, None]
    else:
        if input_command[1][0] != '/':  # Not absolute path
            if input_command[1] == ".":
                return[None, None]
            if input_command[1] == "..":
                if current_dir[:-1].rfind('/') != -1:
                    current_dir = current_dir[:current_dir[:-1].rfind('/') + 1]
                    current_dir_short = current_dir[current_dir[:-1].rfind('/') + 1:-1]
                else:
                    current_dir = ""
                    current_dir_short = ""
                return [current_dir, current_dir_short]
            elif input_command[1].endswith('/'):
                check_directory = current_dir + input_command[1]
            else:
                check_directory = current_dir + input_command[1] + '/'

            return cd_check_directory_for_existence(all_files, check_directory, input_command)

        elif input_command[1] != '/':  # Absolute path

            input_command[1] = input_command[1][1:]
            if input_command[1].endswith('/'):
                check_directory = input_command[1]
            else:
                check_directory = input_command[1] + '/'

            return cd_check_directory_for_existence(all_files, check_directory, input_command)

        else:

            return ["", ""]


def cd_check_directory_for_existence(all_files, check_directory, input_command):
    if check_directory in all_files:
        current_dir = check_directory
        if current_dir[:-1].rfind('/') != -1:
            current_dir_short = current_dir[current_dir[:-1].rfind('/') + 1:-1]
        else:
            if current_dir == '':
                current_dir_short = ""
            else:
                current_dir_short = current_dir[:-1]
        return [current_dir, current_dir_short]

    else:
        if check_directory[:-1] in all_files:
            print(f"vshell: {input_command[0]}: {input_command[1]}: Not a directory")
        else:
            print(f"vshell: {input_command[0]}: {input_command[1]}: No such file or directory")
        return [None, None]


def main():
    filesystem_image_path = sys.argv[1]
    if zipfile.is_zipfile(filesystem_image_path):
        with ZipFile(filesystem_image_path, 'r') as filesystem_image_read:
            interaction_cycle(filesystem_image_read, "zip")
    elif tarfile.is_tarfile(filesystem_image_path):
        with tarfile.open(filesystem_image_path, 'r') as filesystem_image_read:
            interaction_cycle(filesystem_image_read, "tar")


if __name__ == '__main__':
    main()
