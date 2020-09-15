import sys
import os
import shutil
import glob
import subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'eyed3'])
import eyed3


TEMP_PATH = "{rootdir}.sorter_tmp"
SORTED_PATH = "{rootdir}.sorted"


class Sorter(object):
    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.temp_path = "{root}.sorter_tmp".format(root=self.rootdir)
        self.sorted_path = "{root}.sorted".format(root=self.rootdir)

    def handle_file(self, path):
        track = eyed3.load(path)
        dst_tree = "{}\\{}\\{}".format(self.temp_path,
                                         track.tag.artist,
                                         track.tag.album)
        new_path = "{}\\{}.mp3".format(dst_tree, track.tag.title).replace("/",
                                                                          "")
        os.makedirs(dst_tree)
        # change to os.move when working properly
        shutil.copy(path, dst_tree)
        os.rename("{}\\{}".format(dst_tree, os.path.basename(path)), new_path)
        # TODO: log an indicative message about moving the song file to 
            # another folder

    def sort(self):
        os.mkdir(self.temp_path)
        ifiles = glob.iglob("{}\**".format(self.rootdir), recursive=True)
        # TODO - log an indicative message about discarding the non-mp3 file
            # from the sorter and keeping it where it is.
        ifiles = filter(
            lambda p: True if os.path.splitext(p)[1] == ".mp3" else False,
            ifiles)
        for file in ifiles:
            self.handle_file(file)


def main():
    music_folder = sys.argv[1]
    if os.path.isdir(music_folder):
        sorter = Sorter(music_folder)
        sorter.sort()
    else:
        # log an indicative error message
        sys.exit(1)

if __name__ == '__main__':
    main()