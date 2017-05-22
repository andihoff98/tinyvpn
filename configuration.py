

class Configuration:

    def __init__(self):
        self.table = {}

    def load(self, path):
        try:
            configfile = open(path, "r")
        except:
            raise IOError
            return

        lines = configfile.readlines()
        configfile.close()
        for line in lines:
            line = line.strip()
            if line[:1] != "#":
                if line.find('=') != -1:
                    self.table[line[:line.find("=")].strip()] = line[line.find("=")+1:].strip()

    def get(self, key, defaultValue=""):
        if key in self.table:
            return self.table[key]
        else:
            return defaultValue
