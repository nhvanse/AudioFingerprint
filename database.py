from fprint import Fprint, Song
import mysql.connector

MIN_HASHES = 100
class DBExcutor:
    
    __config = {
        'database': 'audio_fingerprint',
        'user': 'root',
        'password': '*********',
        'host': 'localhost',
        'port': '3306'
    }

    def __init__(self):
        pass
    
    @staticmethod
    def excute(query):
        try:
            conn = mysql.connector.connect(**DBExcutor.__config)
            
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                conn.commit()
        except Exception as e:
            print('Lỗi: '+ str(e))
        finally:
            if (conn.is_connected()):
                cursor.close()
                conn.close()
    @staticmethod
    def select(query): 
        rows = None
        try:
            conn = mysql.connector.connect(**DBExcutor.__config)
            if conn.is_connected():
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
        except Exception as e:
            print('Lỗi: '+ str(e))
        finally:
            if (conn.is_connected()):
                cursor.close()
                conn.close()
        return rows

    @staticmethod
    def create():

        DBExcutor.excute('''CREATE TABLE IF NOT EXISTS songs (
                song_id int primary key auto_increment,
                name varchar(100),
                is_printed tinyint default 0
            );''')

        DBExcutor.excute('''CREATE TABLE IF NOT EXISTS fingerprints (
                song_id int not null,
                offset int not null,
                hash varchar(50) not null,
                index(hash),
                unique(song_id, offset, hash)

            );''')

    @staticmethod
    def insertFprints(fprints):
        values = []
        song_ids = set()
        for fprint in fprints:
            values.append("""(%s, %s, '%s')""" 
                % (fprint.song_id, fprint.offset, fprint.hash))
            song_ids.add(str(fprint.song_id))

        values_string = ', '.join(values)
        song_ids_string = ', '.join(song_ids)

        DBExcutor.excute("""
            INSERT IGNORE INTO %s 
            VALUES %s;
        """ % ("fingerprints", values_string))

        DBExcutor.excute("""
            UPDATE songs
            SET is_printed = 1
            WHERE song_id IN (%s);
        """ % (song_ids_string))
        

    @staticmethod
    def insertSong(song):
        DBExcutor.excute("""
            INSERT INTO %s 
            (name)
            VALUES ('%s');
        """ % ("songs", song.name))
        rows = DBExcutor.select("""SELECT MAX(song_id) from songs;""")
        song_id = rows[0][0]
        return song_id

    @staticmethod
    def findSongByFprints(fprints):
        hashes = []
        for f in fprints:
            hashes.append(""" '%s' """ % (f.hash))
        values_string = ', '.join(hashes)

        rows = DBExcutor.select("""
            SELECT song_id, count(hash)
            FROM fingerprints
            WHERE hash IN (%s)
            GROUP BY song_id
            ORDER BY count(hash) DESC;
        """ % (values_string))

        if rows==None or len(rows) < 1 or rows[0][1] < MIN_HASHES:
            return "Không tìm được bài hát."
        else:
            song_id = rows[0][0]
            name_rows = DBExcutor.select("""
                SELECT name
                FROM songs
                WHERE song_id = %s;
            """ % (song_id))
            return name_rows[0][0], rows

    



