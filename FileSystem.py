from FileDescriptor import FileDescriptor


class FileSystem:
    def __init__(self):
        self.max_descriptions_count = 0
        self.current_descriptions_count = 0
        self.num_id = 1
        self.open_files = {}
        self.directory_structure = {}
        self.current_directory = ""
        self.current_descriptors = {}
        self.file_descriptor_paths = {}

    def mkfs(self, n):
        self.max_descriptions_count = n

        root_descriptor = FileDescriptor(0, 'directory', 0)
        self.current_directory = "/"
        self.directory_structure[self.current_directory] = {}
        self.current_descriptors = self.directory_structure[self.current_directory]
        self.file_descriptor_paths[root_descriptor] = self.current_directory

        self.directory_structure[self.current_directory]["."] = root_descriptor
        root_descriptor.nlink += 1

        print(f"Ініціалізовано файлову систему з максимальною кількістю файлів - {n}.")

    def stat(self, pathname):
        if not pathname.startswith('/'):
            descriptor = self.current_descriptors.get(pathname)
            if descriptor:
                print(f"id={descriptor.id}   type={descriptor.type}   nlink={descriptor.nlink}   size={descriptor.size}"
                      f"   nblock={descriptor.nblock}")
            else:
                print(f"Файл з іменем '{pathname}' не знайдено.")
            return

        path_parts = pathname.strip('/').split('/')
        current_directory = '/'
        current_descriptors = self.directory_structure[current_directory]

        for i, part in enumerate(path_parts):
            if part not in current_descriptors.keys():
                print(f"Файл з іменем '{pathname}' не знайдено.")
                return
            part_descriptor = current_descriptors[part]
            if i == len(path_parts) - 1:
                print(f"id={part_descriptor.id}   type={part_descriptor.type}   nlink={part_descriptor.nlink}   "
                      f"size={part_descriptor.size}   nblock={part_descriptor.nblock}")
                return
            if part_descriptor.type != 'directory':
                print(f"В директорії {current_directory} не знайдено директорії {part}")
                return

            current_directory += part + '/'
            current_descriptors = self.directory_structure[current_directory]

    def ls(self):
        for name, descriptor in self.current_descriptors.items():
            if descriptor.type == 'symlink':
                print(f"{name:<12}  =>  {descriptor.type}, {descriptor.id} -> {descriptor.data}")
            else:
                print(f"{name:<12}  =>  {descriptor.type}, {descriptor.id}")

    def pwd(self):
        print("dir struct = ", self.directory_structure)
        print("curr dir = ", self.current_directory)
        print("curr descs = ", self.current_descriptors)

    def create(self, pathname):
        def _create_file(directory, filename):
            new_descriptor = FileDescriptor(self.num_id, 'regular', 0)
            self.num_id += 1
            self.current_descriptions_count += 1
            self.directory_structure[directory][filename] = new_descriptor
            print(f"Файл '{filename}' створено у директорії '{directory}'.")

        if self.current_descriptions_count == self.max_descriptions_count:
            print("Досягнуто максимально можливої кількості файлів.")
            return
        if not pathname.startswith('/'):
            if pathname in self.current_descriptors.keys():
                print(f"Файл або директорія з іменем '{pathname}' вже існує.")
                return
            _create_file(self.current_directory, pathname)
            return

        path_parts = pathname.strip('/').split('/')
        path = '/' if len(path_parts) == 1 else '/' + '/'.join(path_parts[:-1]) + '/'
        if path not in self.directory_structure:
            print(f"Шлях {path} не знайдено.")
            return
        file_name = path_parts[-1]
        if file_name in self.directory_structure[path]:
            print(f"Файл або директорія з іменем '{file_name}' вже існує.")
            return
        _create_file(path, path_parts[-1])

    def open(self, pathname):
        def _open_file(descriptor, filename):
            if descriptor.type == 'symlink':
                symlink_path = descriptor.data
                if not symlink_path.startswith('/'):
                    symlink_path = self.file_descriptor_paths[descriptor].rsplit('/', 1)[0] + '/' + symlink_path

                self.cd(symlink_path) if symlink_path.endswith('/') else self.open(symlink_path)
                return

            file_descriptor = max(self.open_files.keys()) + 1 if self.open_files else 0
            self.open_files[file_descriptor] = descriptor
            print(f"Файл '{filename}' відкрито з дескриптором {file_descriptor}.")

        if not pathname.startswith('/'):
            descriptor = self.current_descriptors.get(pathname)
            _open_file(descriptor, pathname) if descriptor else print(f"Файл '{pathname}' не знайдено.")
            return

        path_parts = pathname.strip('/').split('/')
        path = '/' if len(path_parts) == 1 else '/' + '/'.join(path_parts[:-1]) + '/'
        if path not in self.directory_structure:
            print(f"Шлях {path} не знайдено.")
            return
        filename = path_parts[-1]
        if filename not in self.directory_structure[path] or \
                self.directory_structure[path][filename].type == 'directory':
            print(f"Файл '{pathname}' не знайдено.")
            return

        descriptor = self.directory_structure[path][path_parts[-1]]
        _open_file(descriptor, pathname)

    def close(self, fd):
        if fd in self.open_files:
            del self.open_files[fd]
            print(f"Файл з дескриптором {fd} закрито.")
        else:
            print(f"Файл з дескриптором {fd} не є відкритим зараз.")

    def seek(self, fd, offset):
        for open_descriptor in self.open_files.keys():
            if open_descriptor == fd:
                file_descriptor = self.open_files.get(open_descriptor)
                if 0 <= offset <= file_descriptor.size:
                    file_descriptor.offset = offset
                    print(f"Зміщення файлу з дескриптором {fd} встановлено на {offset}.")
                else:
                    print(f"Неправильне зміщення для файлу з дескриптором {fd}.")
                return
        print(f"Файл з дескриптором {fd} не є відкритим зараз.")

    def read(self, fd, size):
        for open_descriptor in self.open_files.keys():
            if open_descriptor == fd:
                file_descriptor = self.open_files.get(open_descriptor)
                read_data = file_descriptor.read(size)
                if read_data is not None:
                    print(f"Прочитано {size} байтів з файлу з дескриптором {fd}: {read_data}")
                return
        print(f"Файл з дескриптором {fd} не є відкритим зараз.")

    def write(self, fd, size):
        for open_descriptor in self.open_files.keys():
            if open_descriptor == fd:
                file_descriptor = self.open_files.get(open_descriptor)
                written_data = file_descriptor.write(size=size)
                if written_data is not None:
                    print(f"Записано {size} байт у файл з дескриптором {fd}: {written_data}")
                return
        print(f"Файл з дескриптором {fd} не є відкритим зараз.")

    def link(self, pathname1, pathname2):
        if not pathname1.startswith('/'):
            descriptor = self.current_descriptors.get(pathname1)
            if not descriptor:
                print(f"Файл з іменем '{pathname1}' не знайдено.")
                return
        else:
            path_parts = pathname1.strip('/').split('/')
            path1 = '/' if len(path_parts) == 1 else '/' + '/'.join(path_parts[:-1]) + '/'
            if path1 not in self.directory_structure or path_parts[-1] not in self.directory_structure[path1]:
                print(f"Файл з іменем '{pathname1}' не знайдено.")
                return
            descriptor = self.directory_structure[path1][path_parts[-1]]

        if descriptor.type == 'directory':
            print(f"Неможливо створити жорстке посилання на '{pathname1}'.")
            return

        if not pathname2.startswith('/'):
            if pathname2 in self.current_descriptors:
                print(f"Файл або директорія з іменем '{pathname2}' вже існує.")
                return
            self.current_descriptors[pathname2] = descriptor
        else:
            path_parts = pathname2.strip('/').split('/')
            path2 = '/' if len(path_parts) == 1 else '/' + '/'.join(path_parts[:-1]) + '/'
            if path2 not in self.directory_structure:
                print(f"Шлях {path2} не знайдено.")
                return
            if path_parts[-1] in self.directory_structure[path2]:
                print(f"Файл або директорія з іменем '{pathname2}' вже існує.")
                return
            self.directory_structure[path2][path_parts[-1]] = descriptor

        descriptor.nlink += 1
        print(f"Створено жорстке посилання з іменем '{pathname2}' на файл '{pathname1}'.")

    def unlink(self, pathname):
        if not pathname.startswith('/'):
            if pathname not in self.current_descriptors:
                print(f"Файл з іменем '{pathname}' не знайдено.")
                return
            descriptor = self.current_descriptors[pathname]
            descriptor.nlink -= 1
            self.current_descriptors.pop(pathname)
        else:
            path_parts = pathname.strip('/').split('/')
            path = '/' if len(path_parts) == 1 else '/' + '/'.join(path_parts[:-1]) + '/'
            if path not in self.directory_structure or path_parts[-1] not in self.directory_structure[path]:
                print(f"Файл з іменем '{pathname}' не знайдено.")
                return
            descriptor = self.directory_structure[path][path_parts[-1]]
            descriptor.nlink -= 1
            self.directory_structure[path].pop(path_parts[-1])

        print(f"Жорстке посилання на файл '{pathname}' успішно видалено.")

    def truncate(self, pathname, size):
        if not pathname.startswith('/'):
            descriptor = self.current_descriptors.get(pathname)
            current_path = self.current_directory
        else:
            path_parts = pathname.strip('/').split('/')
            path = '/' if len(path_parts) == 1 else '/' + '/'.join(path_parts[:-1]) + '/'
            descriptor = self.directory_structure.get(path, {}).get(path_parts[-1])
            current_path = path

        if not descriptor or descriptor.type != 'regular':
            print(f"Файл з іменем '{pathname}' не знайдено.")
            return

        old_size = descriptor.size
        descriptor.size = size
        if size > old_size:
            descriptor.data += '\0' * (size - old_size)
        elif size < old_size:
            descriptor.data = descriptor.data[:size]
        descriptor.nblock = (descriptor.size // descriptor.block_size) + 1
        print(f"Новий розмір файлу '{pathname}' - {size} байтів.")

        size_diff = size - old_size
        self._update_directory_sizes(current_path, size_diff)

    def mkdir(self, pathname):
        def create_directory(path, directory_name):
            new_descriptor = FileDescriptor(self.num_id, 'directory', 0)
            new_descriptor.nlink += 1
            self.num_id += 1
            self.current_descriptions_count += 1
            self.directory_structure[path].update({directory_name: new_descriptor})
            new_path = path + directory_name + "/"
            self.directory_structure[new_path] = {}
            self.directory_structure[new_path]["."] = new_descriptor
            self.directory_structure[new_path][".."] = self.directory_structure[path]["."]
            self.file_descriptor_paths[new_descriptor] = new_path
            self.directory_structure[path]["."].nlink += 1
            print(f"Директорію з іменем '{directory_name}' створено.")

        if self.current_descriptions_count == self.max_descriptions_count:
            print("Досягнуто максимально можливої кількості файлів.")
            return
        if pathname in self.current_descriptors.keys():
            print(f"Файл або директорія з іменем '{pathname}' вже існує.")
            return
        if not pathname.startswith('/'):
            create_directory(self.current_directory, pathname)
            return

        path_parts = pathname.strip('/').split('/')
        path = '/' if len(path_parts) == 1 else '/' + '/'.join(path_parts[:-1]) + '/'
        if path not in self.directory_structure:
            print(f"Шлях {path} не знайдено.")
            return

        directory_name = path_parts[-1]
        if directory_name in self.directory_structure[path]:
            print(f"Файл або директорія з іменем '{directory_name}' вже існує.")
            return

        create_directory(path, directory_name)

    def rmdir(self, pathname):
        def remove_directory(path, directory_name):
            del self.directory_structure[path + directory_name + "/"]
            self.directory_structure[path]["."].nlink -= 1
            del self.directory_structure[path][directory_name]
            print(f"Директорію '{directory_name}' було видалено.")

        def validate_directory(directory_name):
            if len(self.directory_structure[directory_name]) > 2:
                print(f"Неможливо видалити директорію '{pathname}' оскільки вона не є порожньою.")
                return False
            return True

        if not pathname.startswith('/'):
            if pathname not in self.current_descriptors or self.current_descriptors[pathname].type != "directory":
                print(f"Директорії з іменем '{pathname}' в поточній директорії не існує.")
                return
            if not validate_directory(self.current_directory + pathname + "/"):
                return
            remove_directory(self.current_directory, pathname)
        else:
            if pathname.endswith('/'):
                pathname = pathname[:-1]
            path = '/' + '/'.join(pathname.strip('/').split('/')[:-1]) + '/'
            if path not in self.directory_structure:
                print(f"Шлях {path} не знайдено.")
                return
            directory_name = pathname.split('/')[-1]
            if directory_name not in self.directory_structure[path] or \
                    self.directory_structure[path][directory_name].type != "directory":
                print(f"В директорії {path} не існує директорії з іменем '{directory_name}'.")
                return
            if not validate_directory(path + directory_name + "/"):
                return
            remove_directory(path, directory_name)

    def cd(self, pathname):
        if pathname not in ['.', '..'] and pathname.startswith("/") and not pathname.endswith("/"):
            pathname += "/"

        if pathname == ".":
            self.current_directory = self.file_descriptor_paths[self.current_descriptors[pathname]]
        elif pathname == "..":
            if self.current_directory == "/":
                print("Неможливо перейти вище кореневої директорії.")
            else:
                self.current_directory = self.file_descriptor_paths[self.current_descriptors[pathname]]
        elif pathname in self.current_descriptors:
            self.current_directory = self.file_descriptor_paths[self.current_descriptors[pathname]]
        elif pathname in self.directory_structure:
            self.current_directory = pathname
        else:
            print(f"Директорії '{pathname}' не існує.")
            return

        self.current_descriptors = self.directory_structure[self.current_directory]

    def symlink(self, content, pathname):
        def create_symlink(path, filename):
            new_descriptor = FileDescriptor(self.num_id, 'symlink', len(content))
            new_descriptor.write(content=content)
            self.num_id += 1
            self.current_descriptions_count += 1
            self.directory_structure[path][filename] = new_descriptor
            self.file_descriptor_paths[new_descriptor] = path + filename
            print(f"Створено символічне посилання {filename} на {content}.")
            self._update_directory_sizes(path, len(content))

        if len(content) > 128:
            print("Розмір рядка-вмісту перевищує розмір одного блоку.")
            return

        if not pathname.startswith('/'):
            if pathname in self.current_descriptors:
                print(f"Файл або директорія з іменем '{pathname}' вже існує.")
                return
            create_symlink(self.current_directory, pathname)
            return

        path_parts = pathname.strip('/').split('/')
        path = '/' if len(path_parts) == 1 else '/' + '/'.join(path_parts[:-1]) + '/'
        if path not in self.directory_structure:
            print(f"Шлях {path} не знайдено.")
            return
        filename = path_parts[-1]
        if filename in self.directory_structure[path]:
            print(f"Файл або директорія з іменем '{filename}' вже існує.")
            return
        create_symlink(path, filename)

    def _update_directory_sizes(self, path, size_diff):
        while path != "/":
            current_descriptor = self.directory_structure[path]["."]
            current_descriptor.size += size_diff
            current_descriptor.nblock = (current_descriptor.size // current_descriptor.block_size) + 1
            parent_directory = self.directory_structure[path][".."]
            path = self.file_descriptor_paths[parent_directory]
        root_descriptor = self.directory_structure["/"]["."]
        root_descriptor.size += size_diff
        root_descriptor.nblock = (root_descriptor.size // root_descriptor.block_size) + 1