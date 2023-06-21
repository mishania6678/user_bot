import pymysql

import osteo_bot.config


class DBADMIN:
    def __init__(self):
        pass

    def add_chatid(self, username: str, chatid: int):
        self.__connect_database()

        with self.db.cursor() as cursor:
            cursor.execute(f'INSERT INTO `userinfo` (username, chatid) VALUES ("{username}", "{chatid}")')
            self.db.commit()

        self.__connect_database()

    def get_chatid(self, username: str) -> int:
        self.__connect_database()

        with self.db.cursor() as cursor:
            cursor.execute(f'SELECT chatid FROM `userinfo` WHERE username LIKE "%{username}"')
            chatid = cursor.fetchall()[0][0]

        self.__connect_database()

        return chatid

    def __connect_database(self):
        self.db = pymysql.connect(
            host='eu-cdbr-west-03.cleardb.net',
            user=osteo_bot.config.db_user,
            password=osteo_bot.config.db_pass,
            database=osteo_bot.config.db_db
        )

    def __close_database(self):
        self.db.close()
