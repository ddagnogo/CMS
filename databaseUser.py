#coding:utf8

import sqlite3
import haslib
import uuid


class DatabaseUser(object):

    def __init__(self):
        self.connection = None


    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/user.db')
        return self.connection


    def disconnect(self):
        if self.connection is not None:
            self.connection.close()





        


