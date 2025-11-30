from FileSystem import FileSystem


def create_commands_syntax_and_functions(commands):
    syntax = ['<pathname>', '', '<pathname>', '<pathname>',  '<file_descriptor>', '<file_descriptor> <offset>',
              '<file_descriptor> <size>', '<file_descriptor> <size>', '<pathname1> <pathname2>', '<pathname>',
              '<pathname> <size>', '<N>', '', '<pathname>', '<pathname>', '<pathname>', '<str> <pathname>']
    functions = [fs.stat, fs.ls, fs.create, fs.open, fs.close, fs.seek, fs.read, fs.write, fs.link, fs.unlink,
                 fs.truncate, fs.mkfs, fs.pwd, fs.mkdir, fs.rmdir, fs.cd, fs.symlink]

    commands_syntax = {}
    commands_functions = {}

    for i in range(len(commands)):
        commands_syntax[commands[i]] = syntax[i]
        commands_functions[commands[i]] = functions[i]

    return commands_syntax, commands_functions


def command_is_found(command):
    syntax = commands_syntax[command[0]]
    needed_parameters = syntax.count('<')
    got_parameters = len(command) - 1

    if needed_parameters > got_parameters:
        print(f"Не вистачає параметрів. Правильний синтаксис: {command[0]} {syntax}")
        return
    elif needed_parameters < got_parameters:
        print(f"Передано забагато параметрів. Правильний синтаксис: {command[0]} {syntax}")
        return

    if fs.max_descriptions_count == 0 and command[0] != 'mkfs':
        print("Ініціалізуйте файлову систему командою mkfs.")
        return

    ok, parameters = check_parameters(command[1:], syntax)
    if ok:
        func = commands_functions[command[0]]
        func(*parameters)


def command_not_found():
    possible_commands = [cmd for cmd in commands if cmd.startswith(command[0])]
    if not possible_commands:
        print("Невідома команда.")
    else:
        print("Можливі команди:", ", ".join(possible_commands))


def check_parameters(parameters, syntax):
    if not syntax:
        return True, parameters

    syntax_param = syntax.split(" ")
    for i, param in enumerate(syntax_param):
        if any(word in param for word in ["file_descriptor", "size", "offset", "N"]):
            try:
                parameters[i] = int(parameters[i])
            except:
                print(f"Неправильний тип даних для параметра {param}")
                return False, parameters

    return True, parameters


if __name__ == '__main__':
    fs = FileSystem()

    commands = ['stat', 'ls', 'create', 'open', 'close', 'seek', 'read', 'write', 'link', 'unlink', 'truncate', 'mkfs',
                'pwd', 'mkdir', 'rmdir', 'cd', 'symlink']
    commands_syntax, commands_functions = create_commands_syntax_and_functions(commands)

    while True:
        command = input(f"\n{fs.current_directory} > ").split()
        if command:
            if command[0] in commands:
                command_is_found(command)
            elif command[0] in ['exit', 'quit']:
                break
            elif command[0] not in commands:
                command_not_found()
