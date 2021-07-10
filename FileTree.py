import os
import pathlib
PIPE = "│"
ELBOW = "└──"
TEE = "├──"
PIPE_PREFIX = "│   "
SPACE_PREFIX = "    "


class TreeGenerator:
    ext = None

    def __init__(self, root_dir, file_extension):
        self.root_dir = pathlib.Path(root_dir)
        self.tree = []
        if file_extension:
            self.ext = tuple([exten if exten.startswith(".") else "." + exten for exten in file_extension])

    def build_tree(self):
        self.tree_head()
        self.tree_body(self.root_dir)
        return self.tree

    def tree_head(self):
        self.tree.append(f"{self.root_dir}{os.sep}")
        self.tree.append(PIPE)

    def tree_body(self, directory, prefix=""):
        entries = directory.iterdir()
        entries = sorted(entries, key=lambda fentry: fentry.is_file())
        entries_count = len(entries)
        for index, entry in enumerate(entries):
            try:
                connector = ELBOW if index == entries_count - 1 else TEE
                if entry.is_dir():
                    self.add_directory(entry, index, entries_count, prefix, connector)
                else:
                    self.add_file(entry, prefix, connector)
            except PermissionError:
                continue

    def add_directory(self, directory, index, entries_count, prefix, connector):
        self.tree.append(f"{prefix}{connector} {directory.name}{os.sep}")
        if index != entries_count - 1:
            prefix += PIPE_PREFIX
        else:
            prefix += SPACE_PREFIX
        self.tree_body(
            directory=directory,
            prefix=prefix,
        )
        self.tree.append(prefix.rstrip())

    def add_file(self, file, prefix, connector):
        if self.ext:
            if file.name.endswith(self.ext):
                self.tree.append(f"{prefix}{connector} {file.name}")
        else:
            self.tree.append(f"{prefix}{connector} {file.name}")


class DirectoryTree:
    def __init__(self, root_dir, *extension):
        self._generator = TreeGenerator(root_dir, extension)

    def generate(self):
        tree = self._generator.build_tree()
        for entry in tree:
            print(entry)
        tree.append("────")
        print(tree[-1] + "END────")


dir_path = input("Enter absolute path to directory: ")
ext = input("Enter file extension(s) separated with space. Leave blank to list everything: ")
if ext != "":
    ext = ext.split(" ")
else:
    ext = None
if os.path.exists(dir_path) and os.path.isdir(dir_path):

    if ext is not None:
        f_tree = DirectoryTree(dir_path, *ext)
        f_tree.generate()
    else:
        f_tree = DirectoryTree(dir_path)
        f_tree.generate()
else:
    print("Entered directory doesn't exists")



