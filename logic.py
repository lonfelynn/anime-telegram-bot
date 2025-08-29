import sqlite3
from config import database

class DB_Manager:
    def __init__(self, database):
        self.database = database
        self.create_tables()

    def create_tables(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS anime (
                    Ranked INTEGER PRIMARY KEY,
                    Title TEXT,
                    Score TEXT,
                    Vote TEXT,
                    Popularity INTEGER,
                    Episodes INTEGER,
                    Status TEXT,
                    Aired TEXT,
                    Premiered TEXT,
                    Producers TEXT,
                    Licensors TEXT,
                    Studios TEXT,
                    Source TEXT,
                    Duration TEXT,
                    Rating TEXT
                )
            """)
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER,
                    Ranked INTEGER,
                    PRIMARY KEY (user_id, Ranked)
                )
            """)
            conn.commit()

    
    def _executemany(self, sql, data):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.executemany(sql, data)
            conn.commit()

    def _execute(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            conn.commit()

    def _select(self, sql, data=tuple()):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(sql, data)
            return cur.fetchall()

    
    def get_random_anime(self):
        return self._select("SELECT * FROM anime ORDER BY RANDOM() LIMIT 1")

    def search_anime(self, text):
        return self._select("SELECT * FROM anime WHERE LOWER(title) LIKE ?", (f"%{text.lower()}%",))

    def get_anime_by_id(self, Ranked):
        res = self._select("SELECT * FROM anime WHERE Ranked=?", (Ranked,))
        return res[0] if res else None

    
    def add_favorite(self, user_id, Ranked):
        try:
            self._execute("INSERT INTO favorites (user_id, Ranked) VALUES (?, ?)", (user_id, Ranked))
            return True
        except sqlite3.IntegrityError:
            return False 

    def remove_favorite(self, user_id, Ranked):
        self._execute("DELETE FROM favorites WHERE user_id=? AND Ranked=?", (user_id, Ranked))
        return True

    def get_favorites(self, user_id):
        return self._select("""
            SELECT anime.*
            FROM anime
            JOIN favorites ON anime.Ranked = favorites.Ranked
            WHERE favorites.user_id = ?
        """, (user_id,))
    
        

if __name__ == '__main__':
    manager = DB_Manager(database)