"""
A representation of a folder in the form of dictionary
So, you can access any directory in the form of a dict.
Keys - Files in the folder
Values - Their content

CONSTRAINT:-
1) It supports files opened in r and w mode. Not in rb or wb mode.
2) No support for appending to a file
3) No support for setdefault


For example
folder_dict = FolderDict(FOLDER_PATH)
"""
import os


class FolderDict(dict):

    def get_absolute_path(self, file_name):
        return os.path.join(self.folder_path, file_name)

    def get_only_files(self):
        for file_name in os.listdir(self.folder_path):
            absolute_file_path = self.get_absolute_path(file_name)
            if os.path.isfile(absolute_file_path):
                yield absolute_file_path

    def __init__(self, folder_path, create_new=False):
        self.folder_path = folder_path
        self._dict = {}
        if os.path.exists(self.folder_path) and os.path.isdir(self.folder_path):
            for absolute_file_path in self.get_only_files():
                file_name = os.path.split(absolute_file_path)[1]
                with open(absolute_file_path, "r") as reader:
                    self._dict[file_name] = reader.read()
        else:
            if create_new:
                os.makedirs(folder_path, exist_ok=True)
            else:
                raise IOError("[Errno 2] No such file or directory: '{}'".format(self.folder_path))

    def __getitem__(self, item):
        """
        https://stackoverflow.com/questions/20677923/python-print-last-traceback-only
        We'll swallow the KeyError and we'll just raise FNF, as that's what the KeyError specifies
        """
        try:
            return self._dict[item]
        except KeyError:
            raise IOError("[Errno 2] No such file or directory: '{}'".
                                    format(os.path.join(self.folder_path, item)))

    def __setitem__(self, key, value):
        """
        Be careful,it will overwrite the existing file.
        We support w mode not a mode now
        """
        with open(self.get_absolute_path(key), "w") as writer:
            self._dict[key] = value
            writer.write(value)

    def keys(self):
        return self._dict.keys()

    def __iter__(self):
        for key in self.keys():
            yield key

    def values(self):
        for key in self.keys():
            yield self._dict[key]

    def items(self):
        for key in self.keys():
            yield key, self[key]

    def __contains__(self, item):
        return item in self.keys()

    def __delitem__(self, key):
        del self._dict[key]
        os.remove(self.get_absolute_path(key))

    def get(self, k, default=None):
        return self[k] if k in self.keys() else default

    def pop(self, k):
        content = self[k]
        self.__delitem__(k)
        return content

    def __repr__(self):
        return "FolderDict({!r})".format(self.folder_path)

