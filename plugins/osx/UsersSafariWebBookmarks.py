""" Module to parse Safari webbookmarks """
import codecs
import logging
import os
import riplib.ccl_bplist
from riplib.plugin import Plugin


__author__ = 'osxripper'
__version__ = '0.1'
__license__ = 'GPLv3'


class UsersSafariWebBookmarks(Plugin):
    """
    Parse information from /Users/username/Library/Caches/Metadata/Safari/Bookmarks/*.webbookmark
    """

    def __init__(self):
        """
        Initialise the class.
        """
        super().__init__()
        self.set_name("User Safari Web Bookmarks")
        self.set_description("Parse information from /Users/username/Library/Caches/Metadata/Safari/Bookmarks/*.webbookmark plists")
        self.set_data_file("")  # None as scanning through multiple files
        self.set_output_file("")  # this will have to be defined per user account
        self.set_type("bplist")

    def parse(self):
        """
        Iterate over /Users directory and find user sub-directories
        """
        users_path = os.path.join(self._input_dir, "Users")
        if os.path.isdir(users_path):
            user_list = os.listdir(users_path)
            for username in user_list:
                if os.path.isdir(os.path.join(users_path, username)) and not username == "Shared":
                    plist_dir = os.path\
                        .join(users_path, username, "Library", "Caches", "Metadata", "Safari", "Bookmarks")
                    if os.path.isdir(plist_dir):
                        self.__parse_bplist(plist_dir, username)
                    else:
                        logging.warning("%s does not exist.", plist_dir)
                        print("[WARNING] {0} does not exist.".format(plist_dir))
        else:
            logging.warning("%s does not exist.", users_path)
            print("[WARNING] {0} does not exist.".format(users_path))

    def __parse_bplist(self, file, username):
        """
        Parse /Users/username/Library/Caches/Metadata/Safari/Bookmarks/*.webbookmark
        """
        with codecs.open(os.path.join(self._output_dir, "Users_" + username + "_Safari_Web_Bookmarks.txt"), "a", encoding="utf-8") as output_file:
            output_file.write("="*10 + " " + self._name + " " + "="*10 + "\r\n")
            output_file.write("Source Directory: {0}\r\n\r\n".format(file))
            if self.set_os_version in ["big_sur", "catalina", "mojave"]:
                # Does not exist
                pass
            elif self.set_os_version in ["high_sierra"]:
                logging.warning("File: Bookmarks files not in this version.")
                output_file.write("[INFO] File: Bookmarks files not in this version.\r\n")
                print("[INFO] File: Bookmarks files not in this version.")
            elif self._os_version in ["sierra", "el_capitan", "yosemite", "mavericks", "mountain_lion", "lion", "snow_leopard"]:
                plist_dir_list = os.listdir(file)
                for wb_file in plist_dir_list:
                    wb_plist = os.path.join(file, wb_file)
                    output_file.write("Bookmark Plist: {0}\r\n".format(wb_plist))
                    if os.path.isfile(wb_plist):
                        bplist = open(wb_plist, "rb")
                        plist = riplib.ccl_bplist.load(bplist)
                        bplist.close()
                        try:
                            if "Name" in plist:
                                output_file.write("Name: {0}\r\n".format(plist["Name"]))
                            if "URL" in plist:
                                output_file.write("URL: {0}\r\n".format(plist["URL"]))
                        except KeyError:
                            pass
                        output_file.write("\r\n")
                    else:
                        logging.warning("File: %s does not exist or cannot be found.", file)
                        output_file.write("[WARNING] File: {0} does not exist or cannot be found.\r\n".format(file))
                        print("[WARNING] File: {0} does not exist or cannot be found.".format(file))
            else:
                logging.warning("Not a known OSX version.")
                print("[WARNING] Not a known OSX version.")
            output_file.write("="*40 + "\r\n\r\n")
        output_file.close()
