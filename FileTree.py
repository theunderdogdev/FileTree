#!python
import os
import pathlib
from rich import print
import mimetypes

mimetypes.init()
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
            self.ext = tuple(
                [
                    exten if exten.startswith(".") else "." + exten
                    for exten in file_extension
                ]
            )

    # Builder function used to build the entire directory tree
    # Main thing to call
    def build_tree(self):
        self.tree_head()
        self.tree_body(self.root_dir)
        return self.tree

    # Binds the main directory in which the program is called
    # This goes at the top of the directory
    def tree_head(self):
        self.tree.append(f"{self.root_dir}{os.sep}")
        self.tree.append(PIPE)

    # After the root each directories and their traversal are appended here
    # The iterdir function iteratest the present directory giving the list of all items
    # in it
    def tree_body(self, directory, prefix=""):
        entries = directory.iterdir()
        # The items so obtained are sorted depending on filetype
        # i.e. if the directory has files then they should be listed
        # prior to the directories
        # The files so obtained are connected via connector
        # If its last file end it with elbow else continue with a tee
        entries = sorted(entries, key=lambda fentry: fentry.is_file())
        entries_count = len(entries)
        for index, entry in enumerate(entries):
            try:
                connector = ELBOW if index == entries_count - 1 else TEE
                # If the type of file is directory then append it using directory type
                # connection whilst traversing it again ahead recursively
                if entry.is_dir():
                    self.add_directory(entry, index, entries_count, prefix, connector)
                # Else the type is file so append it using file type connection throughout
                else:
                    self.add_file(entry, prefix, connector)
            except PermissionError:
                continue

    def add_directory(self, directory, index, entries_count, prefix, connector):
        # First the name of the directory is appended before traversing
        self.tree.append(
            f"{prefix}{connector} [bright_yellow]{directory.name}[/]{os.sep}"
        )
        # if its not last element (file element) then provide a gap in the nesting so formed
        # ex if we have dir1, dir2 in fold which is in pfold
        # pfold
        # │   └──fold
        # │<----->├── dir1
        # │<----->└── dir2
        # Else if its last element then just escape it out with a gap
        # ex if we have dir1, dir2 in fold which is in pfold and then next fold in pfold is fold2
        # pfold
        # │   └──fold
        # │       ├── dir1
        # │       └── dir2
        # │<-----> last element gap
        # ├── fold2

        if index != entries_count - 1:
            prefix += PIPE_PREFIX
        else:
            prefix += SPACE_PREFIX
        # Recursively traverse everything down the directory
        self.tree_body(
            directory=directory,
            prefix=prefix,
        )
        self.tree.append(prefix.rstrip())

    def add_file(self, file, prefix, connector):
        # Obtain file types just for pretty coloring out different file
        # types in different colors
        ftype = mimetypes.guess_type(file)[0]
        # Check if user specified any file extensions
        # helps to locate out specific file types thoughout
        # your search directory
        if self.ext:
            if file.name.endswith(self.ext):
                if ftype is not None:
                    match ftype.split("/")[0]:
                        # If file type is media highlight it with blue
                        case "image" | "audio" | "video":
                            self.tree.append(
                                f"{prefix}{connector} [blue]{file.name}[/]"
                            )
                        # If file type is executable highlight it with red
                        case "application":
                            self.tree.append(f"{prefix}{connector} [red]{file.name}[/]")
                        # If file type is source or text highlight it with green
                        case "text":
                            self.tree.append(
                                f"{prefix}{connector} [spring_green3]{file.name}[/]"
                            )
                # If file type is unknown to os then grey it out
                else:
                    self.tree.append(
                        f"{prefix}{connector} [bright_black]{file.name}[/]"
                    )
        else:
            if ftype is not None:
                match ftype.split("/")[0]:
                    # If file type is media highlight it with blue
                    case "image" | "audio" | "video":
                        self.tree.append(f"{prefix}{connector} [blue]{file.name}[/]")
                    # If file type is executable highlight it with red
                    case "application":
                        self.tree.append(f"{prefix}{connector} [red]{file.name}[/]")
                    # If file type is source or text highlight it with green
                    case "text":
                        self.tree.append(
                            f"{prefix}{connector} [spring_green3]{file.name}[/]"
                        )
            # If file type is unknown to os then grey it out
            else:
                self.tree.append(f"{prefix}{connector} [bright_black]{file.name}[/]")


# Another class more abstraction ¯\(°_o)/¯
class DirectoryTree:
    def __init__(self, root_dir, *extension):
        self._generator = TreeGenerator(root_dir, extension)

    # This generates the tree
    def generate(self):
        tree: list[str] = self._generator.build_tree()
        write = input("Want to write it to file (y/n):").lower() == "y"
        fname = None
        if write:
            fname = input(
                "Enter full path to file (Leaving empty will create a temp.txt file where this prog executes)\n File Name: "
            )
            if fname is not None and os.path.exists(fname) and os.path.isfile(fname):
                fpoint = open(fname, "w")
            else:
                fpoint = open("temp.txt", "w+")
            for entry in tree:
                print(entry, file=fpoint)
            print(f"└───[bright_white] Done ────[/]", file=fpoint)
        else:
            for entry in tree:
                print(entry)
            print(f"└───[bright_white] Done ────[/]")


dir_path = input("Enter absolute path to directory: ")
ext = input(
    "Enter file extension(s) separated with space. Leave blank to list everything: "
)
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
