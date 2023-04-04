import sqlite3

class DataBase:
    def __init__(self,file):
        self.con = sqlite3.connect(file)
        self.cur = self.con.cursor()

    def add_stat(self,articul,reit,kolvo,fday,fdaykol):
        with self.con:
            return self.cur.execute("""INSERT INTO old_stat(articul,reit,kolvo,fday,fdaykol) VALUES(?,?,?,?,?)""",[articul,reit,kolvo,fday,fdaykol])

    def get_stat(self,articul):
        with self.con:
            return self.cur.execute("""SELECT reit,kolvo,fday,fdaykol FROM old_stat  WHERE articul = ? """,[articul]).fetchall()

    def add_articul(self,articul):
        with self.con:
            return self.cur.execute("""INSERT INTO articul(artic) VALUES(?)""",[articul])

    def get_articul(self):
        with self.con:
            return self.cur.execute("""SELECT artic FROM articul """).fetchall()

    def del_articul(self):
        with self.con:
            return self.cur.execute("""DELETE FROM articul """)

    def del_stat(self):
        with self.con:
            return self.cur.execute("""DELETE FROM old_stat""")

    def add_reit(self,new_reit):
        with self.con:
            return self.cur.execute("""UPDATE data SET reit = (?)""",[new_reit])

    def get_reit(self):
        with self.con:
            return self.cur.execute("""SELECT reit FROM data""").fetchall()