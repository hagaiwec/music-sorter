import sys
import os
import shutil
import glob
import subprocess
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'eyed3'])
import eyed3


class Sorter(object):
    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.sorted_path = "{root}.sorted".format(root=self.rootdir)
        self.track_names = filter(self.is_mp3,
                                  glob.iglob("{}\\**".format(self.rootdir),
                                             recursive=True))
        self.dirtree_format = "{tmp}\\{artist}\\{album}"
        self.noalbum_dirtree_format = "{tmp}\\{artist}"
        self.trackfile_path_format = "{dirtree}\\{title}"

    def is_mp3(self, path):
        return True if os.path.splitext(path)[1] == ".mp3" else False
        # TODO - log an indicative message about discarding the non-mp3 file
            # from the sorter and keeping it where it is.

    def validate_titlename(self, title):
        """
        Solves problems such as:
            - When certain characters collide with python literals
        """
        if title:
            trans = str.maketrans({"/": "-", "*": "", "?": "", '"': "'"})
            return title.translate(trans)
        else:
            return track_name

    def validate_album_artist(self, name):
        """
        Solves problems such as:
            - os.mkdir auto-strips spaces. Then when trying to find the dir 
              created, no dir is found.
        """
        if name:
            trans = str.maketrans({":": "-", '"': "'"})
            name = name.translate(trans)
            name = name.strip()
            return name
        else:
            return name

    def relocate_track(self, track):
        track_name = os.path.basename(track.path)
        artist = self.validate_album_artist(track.tag.artist)
        album = self.validate_album_artist(track.tag.album)
        title = self.validate_titlename(track.tag.title) 
        if not album:
            dirtree = self.noalbum_dirtree_format.format(tmp=self.sorted_path,
                                                         artist=artist)
        else:
            dirtree = self.dirtree_format.format(tmp=self.sorted_path,
                                                 artist=artist,
                                                 album=album)
        new_path = self.trackfile_path_format.format(dirtree=dirtree,
                                                     title=track_name)
        renamed = self.trackfile_path_format.format(dirtree=dirtree,
                                                    title=title) + ".mp3"
        if os.path.exists(renamed): # song already in destination folder
            pass
        else:
            os.makedirs(dirtree, exist_ok=True)
            # change to os.move when working properly
            shutil.copy(track.path, new_path)
            os.rename(new_path, renamed)
            # TODO: log an indicative message about moving the song file to
                # another folder

    def handle_track(self, path):
        track = eyed3.load(path)
        if not track.tag or any((not track.tag.artist, not track.tag.title)):
            return None
        else:
            self.relocate_track(track)

    def sort(self):
        os.mkdir(self.sorted_path)
        for track in self.track_names:
            print(track)
            self.handle_track(track)


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