""" Module to parse information from /Users/<username>/Library/Accounts/Accounts3.sqlite """
import codecs
import logging
import os
import sqlite3
import riplib.osxripper_time
from riplib.plugin import Plugin


__author__ = 'osxripper'
__version__ = '0.1'
__license__ = 'GPLv3'


class UsersAccounts3(Plugin):
    """
    Parse information from /Users/<username>/Library/Accounts/Accounts3.sqlite
    """

    def __init__(self):
        """
        Initialise the class.
        """
        super().__init__()
        self.set_name("User Accounts3")
        self.set_description("Parse information from /Users/<username>/Library/Accounts/Accounts3.sqlite")
        self.set_data_file("Accounts3.sqlite")
        self.set_output_file("")  # this will have to be defined per user account
        self.set_type("sqlite")

    def parse(self):
        """
        Iterate over /Users directory and find user sub-directories
        """
        users_path = os.path.join(self._input_dir, "Users")
        # username = None
        if os.path.isdir(users_path):
            user_list = os.listdir(users_path)
            for username in user_list:
                if os.path.isdir(os.path.join(users_path, username)) and not username == "Shared":
                    sqlite_db = os.path.join(users_path, username, "Library", "Accounts", self._data_file)
                    if os.path.isfile(sqlite_db):
                        self.__parse_sqlite_db(sqlite_db, username)
                    else:
                        logging.warning("%s does not exist.", sqlite_db)
                        print("[WARNING] {0} does not exist.".format(sqlite_db))
        else:
            logging.warning("%s does not exist.", users_path)
            print("[WARNING] {0} does not exist.".format(users_path))

    def __parse_sqlite_db(self, file, username):
        """
        Read the Accounts3.sqlite SQLite database
        """
        with codecs.open(os.path.join(self._output_dir, "Users_" + username + ".txt"), "a", encoding="utf-8") as output_file:
            output_file.write("="*10 + " " + self._name + " " + "="*10 + "\r\n")
            output_file.write("Source File: {0}\r\n\r\n".format(file))
            if self._os_version in ["el_capitan", "yosemite"]:
                parse_os = ParseVers10111010(output_file, file)
                parse_os.parse()
            elif self._os_version in ["mavericks", "mountain_lion"]:
                parse_os = ParseVers110106(output_file, file)
                parse_os.parse()
            elif self._os_version in ["big_sur", "catalina", "mojave", "high_sierra", "sierra", "lion", "snow_leopard"]:
                logging.info("This version of OSX is not supported by this plugin.")
                print("[INFO] This version of OSX is not supported by this plugin.")
                output_file.write("[INFO] This version of OSX is not supported by this plugin.\r\n")
            else:
                logging.warning("Not a known OSX version.")
                print("[WARNING] Not a known OSX version.")
            output_file.write("="*40 + "\r\n\r\n")
        output_file.close()

class ParseVers10111010():
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
        query = "SELECT zat.zaccounttypedescription,za.zusername,za.zactive,za.zauthenticated,za.zvisible," \
                "za.zdate,za.zaccountdescription,za.zowningbundleid " \
                "FROM zaccount za,zaccounttype zat WHERE za.zaccounttype = zat.z_pk"
        conn = None
        try:
            conn = sqlite3.connect(self._data_file)
            conn.row_factory = sqlite3.Row
            with conn:
                cur = conn.cursor()
                cur.execute(query)
                rows = cur.fetchall()
                if len(rows) != 0:
                    for row in rows:
                        zdate = riplib.osxripper_time.get_cocoa_seconds(row["zdate"])
                        self._output_file.write("Account            : {0}\r\n".format(row["zaccounttypedescription"]))
                        self._output_file.write("Username           : {0}\r\n".format(row["zusername"]))
                        self._output_file.write("Active             : {0}\r\n".format(row["zactive"]))
                        self._output_file.write("Authenticated      : {0}\r\n".format(row["zauthenticated"]))
                        self._output_file.write("Visible            : {0}\r\n".format(row["zvisible"]))
                        self._output_file.write("Date               : {0}\r\n".format(zdate))
                        self._output_file.write("Account Description: {0}\r\n".format(row["zaccountdescription"]))
                        self._output_file.write("Owning Bundle ID   : {0}\r\n".format(row["zowningbundleid"]))
                        self._output_file.write("\r\n")
                else:
                    self._output_file.write("\r\nNo Account information found\r\n")
        except sqlite3.Error as error:
            logging.error("%s", error.args[0])
            print("[ERROR] {0}".format(error.args[0]))
        finally:
            if conn:
                conn.close()

class ParseVers110106():
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
        query = "SELECT zusername,zactive,zauthenticated,zdate," \
                "zaccountdescription,zowningbundleid FROM zaccount"
        conn = None
        try:
            conn = sqlite3.connect(self._data_file)
            conn.row_factory = sqlite3.Row
            with conn:
                cur = conn.cursor()
                cur.execute(query)
                rows = cur.fetchall()
                if len(rows) != 0:
                    for row in rows:
                        zdate = riplib.osxripper_time.get_cocoa_seconds(row["zdate"])
                        self._output_file.write("Username           : {0}\r\n".format(row["zusername"]))
                        self._output_file.write("Active             : {0}\r\n".format(row["zactive"]))
                        self._output_file.write("Authenticated      : {0}\r\n".format(row["zauthenticated"]))
                        self._output_file.write("Date               : {0}\r\n".format(zdate))
                        self._output_file.write("Account Description: {0}\r\n".format(row["zaccountdescription"]))
                        self._output_file.write("Owning Bundle ID   : {0}\r\n".format(row["zowningbundleid"]))
                        self._output_file.write("\r\n")
                else:
                    self._output_file.write("\r\nNo Account information found\r\n")
        except sqlite3.Error as error:
            logging.error("%s", error.args[0])
            print("[ERROR] {0}".format(error.args[0]))
        finally:
            if conn:
                conn.close()
