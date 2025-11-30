class FileDescriptor:
    def __init__(self, id, type, size):
        self.id = id
        self.type = type
        self.nlink = 1
        self.size = size
        self.nblock = size
        self.data = ''
        self.offset = 0
        self.block_size = 128
        self.write_flag = True
        self.read_flag = True

    def write(self, size=0, content=''):
        if not self.write_flag or self.type == 'directory':
            print("Не можна виконати операцію запису в цей файл.")
            return None

        if content:
            self.data = content
            return

        if self.size - size < 0:
            print(f"Ви бажаєте записати {size} байт даних у файл розміром {self.size} байт.",
                  f"Змініть розмір файлу за допомогою truncate та повторіть спробу.")
            return None

        remaining_space = self.size - self.offset
        if size > remaining_space:
            print(f"Ви можете записати лише {remaining_space} байт даних в цей файл.",
                  f"Змініть розмір файлу за допомогою truncate та повторіть спробу.")
            return None

        bytes_to_write = min(size, remaining_space)
        data_to_write = ''.join(chr(ord('a') + i % 26) for i in range(bytes_to_write))
        self.data = self.data[:self.offset] + data_to_write + self.data[self.offset + bytes_to_write:]
        self.offset += bytes_to_write
        return data_to_write

    def read(self, size):
        if not self.read_flag or self.type == 'directory':
            print("Не можна виконати операцію читання цього файлу.")
            return None

        if self.offset >= self.size:
            print("Кінець файлу досягнуто.")
            return None

        remaining_data = self.data[self.offset:]
        bytes_to_read = min(size, len(remaining_data))
        data_to_read = remaining_data[:bytes_to_read]
        self.offset += bytes_to_read
        return data_to_read
