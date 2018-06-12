# coding: utf8
import sqlite3
import datetime

def build_article(row):
    return {"titre": row[1], "identifiant": row[2], "auteur": row[3],
            "date_publication": row[4], "paragraphe": row[5]}

def build_for_api(row):
    return {"titre": row[1], "auteur": row[3], "url": "localhost:5000/article/"
            + row[2]}

class Database(object):

    def __init__(self):
        self.connection = None


    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/article.db')
        return self.connection


    def disconnect(self):
        if self.connection is not None:
            self.connection.close()


    def get_articles(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        date_courante = str(datetime.date.today())
        try:
            cursor.execute(("select * from article where date_publication <= ? order by date_publication desc limit 5"), (date_courante,))
            articles = cursor.fetchall()
            return [build_article(article) for article in articles]
        except Exception as e:

            return False


    def get_published(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        date_courante = str(datetime.date.today())
        try:
            cursor.execute(("select * from article where date_publication <= ? order by date_publication desc"), (date_courante,))
            articles = cursor.fetchall()
            return [build_for_api(article) for article in articles]
        except Exception as e:
            return False


    def insert_article(self, titre, identifiant, auteur, date_publication,
            paragraphe):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(("insert into article(titre, identifiant, auteur, date_publication, paragraphe) values(?, ?, ?, ?, ?)"),
            (titre, identifiant, auteur, date_publication, paragraphe))
        connection.commit()


    def verify_suggestion(self, suggestion):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(("select * from article where identifiant = ?"),
                (suggestion,))
        suggestion = cursor.fetchone()
        return suggestion


    def search_words(self, mots):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(("select * from article where paragraphe LIKE ? "), ('%{}%'.format(mots),))
            results = cursor.fetchall()
            return [build_article(result) for result in results]
        except Exception as x:
            return False


    def search_article(self, identifier):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(("select * from article where identifiant = ?"), (identifier,))
            articles = cursor.fetchall()
            if articles is None:
                return None
            return [build_article(article) for article in articles]
        except Exception as e:
            return None


    def search_all(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("select * from article")
            articles = cursor.fetchall()
            return [build_article(article) for article in articles]
        except Exception as x:
            return None


    def update(self, titre, paragraphe, identifiant):
        connection = self.connection()
        cursor = connection.cursor()
        try:
            cursor.execute(("update article set titre = ? paragraphe = ? where identifiant = ?"), (titre, paragraphe, identifiant,))
            connection.commit()
        except Exception as e:
            return None

    def create_user(self, username, email, salt, hashed_password):
        connection = self.get_connection()
        connection.execute(("insert into users (utilisateur, email," 
            "salt, hash)" "values(?, ?, ?, ?)"),
            (username, email, salt, hashed_password))
        connection.commit()


    def get_user_login_info(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute(("select salt, hash from users where utilisateur=?"),
                (username,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0], user[1]


    def get_user_login_info_email(self, email):
        cursor = self.get_connection().cursor()
        cursor.execute(("select salt, hash from users where utilisateur=?"),
                (email,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0], user[1]


    def save_session(self, id_session, username):
        connection = self.get_connection()
        connection.execute(("insert into sessions(id_session, utilisateur) values(?, ?)"), (id_session, username))
        connection.commit()


    def get_session(self, id_session):
        cursor = self.get_connection().cursor()
        cursor.execute(("select utilisateur from sessions where id_session=?"),
                       (id_session,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]


    def delete_session(self, id_session):
        connection = self.get_connection()
        connection.execute(("delete from sessions where id_session=?"),
                              (id_session,))
        connection.commit()
