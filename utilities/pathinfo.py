import os
import re


class PathInfo:
    path = None
    path_parts = []
    dirname = None
    basename = None
    extension = None
    filename = None

    def __init__(self, path):
        self.path = path
        self.path_parts = re.split(r"[/\\]", self.path)
        self.dirname = os.path.dirname(self.path)
        self.basename = os.path.basename(self.path)
        self.filename = self.path_parts[-1]
        if os.path.isfile(self.path):
            self.extension = os.path.splitext(self.path)[-1].replace(".", "")
        else:
            self.extension = self.basename.split(".")[-1]

    def __str__(self):
        return self.path
