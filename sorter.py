import sys
import os
import shutil
import glob
import subprocess
subprocess.check_call([sys.executable, '-m', 'pip', '-q', 'install', 'eyed3'])
import eyed3
import argparse
from os.path import join


INVCHAR_TRANS = str.maketrans({
    "\\" : "-",
    "/" : "-",
    ":" : "-",
    "*" : "",
    "?" : "",
    '"' : "'",
    "<" : "-",
    ">" : "-",
    "|" : "-"
    })


def get_attr(obj, attr, default):
    return getattr(obj, attr, "") or ""


class AudioFileNavigator(object):
    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.track_names = filter(
            self.is_mp3, 
            glob.iglob(join(self.rootdir, "**"), recursive=True))

    def is_mp3(self, path):
        return True if os.path.splitext(path)[1] == ".mp3" else False
        # TODO - log an indicative message about discarding the non-mp3 file
            # from the sorter and keeping it where it is.


class Searcher(AudioFileNavigator):
    def __init__(self, folder, **kwargs):
        super(self.__class__, self).__init__(folder)
        self.fields = kwargs

    def filter_fields(self, track_name):
        """
        filter_fields :: str -> bool
        """
        sys.stderr = open(os.devnull, "w")
        track = eyed3.load(track_name)
        sys.stderr = sys.__stderr__
        if not track.tag:
            return False
        else:
            return all(map(
                lambda f: self.fields[f].lower() in get_attr(track.tag, f, "").lower(), 
                self.fields))

    def search(self):
        return filter(self.filter_fields, self.track_names)


class Sorter(AudioFileNavigator):
    def __init__(self, rootdir):
        super(self.__class__, self).__init__(rootdir)
        self.sorted_path = "{}.sorted".format(self.rootdir)

    def validate_titlename(self, title):
        """
        Solves problems such as:
            - When certain characters collide with python literals
        """
        return title.translate(INVCHAR_TRANS) if title else title

    def validate_album_artist(self, name):
        """
        Solves problems such as:
            - When certain characters collide with python literals
            - os.mkdir auto-strips spaces. Then when trying to find the dir 
              created, no dir is found.
        """
        if name:
            name = name.translate(INVCHAR_TRANS)
            name = name.strip()
            return name

    def relocate_track(self, track):
        track_name = os.path.basename(track.path)
        artist = self.validate_album_artist(track.tag.artist)
        album = self.validate_album_artist(track.tag.album)
        title = self.validate_titlename(track.tag.title) 
        
        if not album:
            dirtree = join(self.sorted_path, artist)
        else:
            dirtree = join(self.sorted_path, artist, album)
        
        new_path = join(dirtree, track_name)
        renamed = join(dirtree, title + ".mp3")
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


def sort(args):
    s = Sorter(args.folder)
    s.sort()


def search(args):
    args = vars(args)
    folder = args.pop("folder")
    fields = {k: args[k][0] for k in args if k != "func" and args[k] != None}
    s = Searcher(folder, **fields)
    for song in s.search():
        print(song)

def main():
    parser = argparse.ArgumentParser(description=
        """
provides actions such as sorting an audio folder or searching for an audio file
in an audio folder"""
    )
    subparser = parser.add_subparsers()
    parser_sort = subparser.add_parser("sort", help="""
take a messy, unsorted music folder and sort it by artist and album""")
    parser_sort.add_argument("folder", help="the folder to be sorted")
    parser_sort.set_defaults(func=sort)

    parser_search = subparser.add_parser("search", help="""
search for an audio file by metadata field and its value. default can be 
searching any metadata field. 
optional fields are: artist, album, title""")
    parser_search.add_argument("--artist", nargs=1)
    parser_search.add_argument("--album", nargs=1)
    parser_search.add_argument("--title", nargs=1)
    # parser_search.add_argument("--year", nargs=1)
    # parser_search.add_argument("--composer", nargs=1)
    parser_search.add_argument("folder", help="the folder to search in")
    parser_search.set_defaults(func=search)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()