
class IOException(Exception):
    pass

class TextIO:
    def __init__(self,jack_file,xml_file):
        self.text_file = jack_file
        self.lines = []
        if self.text_file:
            flow = open(jack_file,mode='r')
            self.lines = flow.readlines()
            flow.close()
        self.count = 0
        self.file_to_write = None
        if xml_file:
            self.file_to_write = open(xml_file,mode='w+')

    def get_line(self):
        if not self.lines:
            raise IOException('try to get line from a empty IO, please check IO text_file{0}'.format(self.text_file))
        if self.count<len(self.lines):
            line = self.lines[self.count]
            self.count+=1
            return line
        else:
            return None
    
    def write_line(self,sentense):
        if not self.file_to_write:
            raise IOException('try to write line from a empty IO, please check IO file_to_write{0}'.format(self.file_to_write))
        if self.file_to_write:
            self.file_to_write.write(sentense)

    def close_write(self):
        if self.file_to_write:
            self.file_to_write.close()

    def reset(self,jack_file,xml_file):
        self.close_write()
        self.__init__(jack_file,xml_file)

    def reset_line_count(self):
        self.count = 0
    
    def get_all_lines(self):
        return self.lines