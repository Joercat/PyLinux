class Editor:
    def __init__(self, filesystem):
        self.filesystem = filesystem
        self.current_file = None
        self.buffer = []
        self.mode = 'normal'
        self.cursor_line = 0
        self.modified = False

    def open_file(self, filepath):
        if self.filesystem.exists(filepath):
            content = self.filesystem.read_file(filepath)
            if content is not None:
                self.buffer = content.decode('utf-8', errors='ignore').split('\n')
                self.current_file = filepath
                self.cursor_line = 0
                self.modified = False
                return True
        else:
            self.buffer = ['']
            self.current_file = filepath
            self.cursor_line = 0
            self.modified = False
            return True
        return False

    def save_file(self):
        if self.current_file:
            content = '\n'.join(self.buffer)
            success = self.filesystem.write_file(self.current_file, content)
            if success:
                self.modified = False
                return True
        return False

    def insert_line(self, line_num, text):
        if 0 <= line_num <= len(self.buffer):
            self.buffer.insert(line_num, text)
            self.modified = True
            return True
        return False

    def delete_line(self, line_num):
        if 0 <= line_num < len(self.buffer):
            self.buffer.pop(line_num)
            self.modified = True
            return True
        return False

    def get_buffer(self):
        return self.buffer

    def close(self):
        self.current_file = None
        self.buffer = []
        self.cursor_line = 0
        self.modified = False
