""" Module to parse Safari LastSession plist """
import codecs
import logging
import os
import riplib.ccl_bplist
from riplib.plugin import Plugin


__author__ = 'osxripper'
__version__ = '0.1'
__license__ = 'GPLv3'


class UsersSafariLastSession(Plugin):
    """
    Parse information from /Users/username/Library/Safari/LastSession.plist
    """

    def __init__(self):
        """
        Initialise the class.
        """
        super().__init__()
        self.set_name("User Safari Last Session")
        self.set_description("Parse information from /Users/username/Library/Safari/LastSession.plist")
        self.set_data_file("LastSession.plist")
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
                    plist = os.path.join(users_path, username, "Library", "Safari", self._data_file)
                    if os.path.isfile(plist):
                        self.__parse_bplist(plist, username)
                    else:
                        logging.warning("%s does not exist.", plist)
                        print("[WARNING] {0} does not exist.".format(plist))
        else:
            logging.warning("%s does not exist.", users_path)
            print("[WARNING] {0} does not exist.".format(users_path))

    def __parse_bplist(self, file, username):
        """
        Parse /Users/username/Library/Safari/LastSession.plist
        """
        with codecs.open(os.path.join(self._output_dir, "Users_" + username + "_Safari_Last_Session.txt"), "a", encoding="utf-8") as output_file:
            output_file.write("="*10 + " " + self._name + " " + "="*10 + "\r\n")
            output_file.write("Source File: {0}\r\n\r\n".format(file))
            if self._os_version in ["big_sur", "catalina", "mojave", "high_sierra", "sierra", "el_capitan", "yosemite", "mavericks", "mountain_lion", "lion"]:
                if os.path.isfile(file):
                    bplist = open(file, "rb")
                    plist = riplib.ccl_bplist.load(bplist)
                    bplist.close()
                    parse_os = ParseVers110107(output_file, plist)
                    parse_os.parse()
                else:
                    logging.warning("File: %s does not exist or cannot be found.", file)
                    output_file.write("[WARNING] File: {0} does not exist or cannot be found.\r\n".format(file))
                    print("[WARNING] File: {0} does not exist or cannot be found.".format(file))
            elif self._os_version == "snow_leopard":
                if os.path.isfile(file):
                    bplist = open(file, "rb")
                    plist = riplib.ccl_bplist.load(bplist)
                    bplist.close()
                    parse_os = ParseVers106(output_file, plist)
                    parse_os.parse()
                else:
                    logging.warning("File: %s does not exist or cannot be found.", file)
                    output_file.write("[WARNING] File: {0} does not exist or cannot be found.\r\n".format(file))
                    print("[WARNING] File: {0} does not exist or cannot be found.".format(file))
            else:
                logging.warning("Not a known OSX version.")
                print("[WARNING] Not a known OSX version.")
            output_file.write("="*40 + "\r\n\r\n")
        output_file.close()

class ParseVers110107():
    """
    Convenience class for parsing macOS data
    """
    def __init__(self, output_file, data_file):
        self._output_file = output_file
        self._data_file = data_file

    def parse(self):
        """
        Parse data
        """
        try:
            if "SessionWindows" in self._data_file:
                for session_window in self._data_file["SessionWindows"]:
                    if "TabStates" in session_window:
                        self._output_file.write("Tabs:\r\n")
                        self._parse_tab_state(session_window)
        except KeyError:
            pass

    def _parse_tab_state(self, plist_chunk):
        for tab_state in plist_chunk["TabStates"]:
            if "TabURL" in tab_state:
                self._output_file.write("\tTab URL  : {0}\r\n".format(tab_state["TabURL"]))
            if "TabTitle" in tab_state:
                self._output_file.write("\tTab Title: {0}\r\n".format(tab_state["TabTitle"]))
            self._output_file.write("\r\n")


class ParseVers106():
    """
    Convenience class for parsing macOS data
    """
    def __init__(self, output_file, data_file):
        self._output_file = output_file
        self._data_file = data_file

    def parse(self):
        """
        Parse data
        """
        try:
            if "SessionWindows" in self._data_file:
                for session_window in self._data_file["SessionWindows"]:
                    if "TabStates" in session_window:
                        self._output_file.write("Tabs:\r\n")
                        self._parse_tab_state(session_window)
        except KeyError:
            pass

    def _parse_tab_state(self, plist_chunk):
        for tab_state in plist_chunk["TabStates"]:
            if "BackForwardList" in tab_state:
                for back_forward_list in tab_state["BackForwardList"]:
                    if "URL" in back_forward_list:
                        self._output_file.write("\tTab URL  : {0}\r\n".format(back_forward_list["URL"]))
                    if "Title" in back_forward_list:
                        self._output_file.write("\tTab Title: {0}\r\n".format(back_forward_list["Title"]))
            self._output_file.write("\r\n")
