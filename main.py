from fprint import Song, Fprint
from database import DBExcutor
import os
from tqdm import tqdm
import sounddevice as sd
from scipy.io.wavfile import write

SONGS_PATH = './songs/'

def buildDB():
    print('Building database.')
    DBExcutor.create()
    for file in tqdm(os.listdir(SONGS_PATH)):
        song = Song(SONGS_PATH + file)
        print(song.name)
        
        song.song_id = DBExcutor.insertSong(song)
        fprints = song.genFprints()
        DBExcutor.insertFprints(fprints)
      
if __name__ == '__main__':
        from time import time
        t = time()
        name = "Không tìm được bài hát."
        while  (name == "Không tìm được bài hát." and time()-t < 100):
                try:
                        fs = 22050  # Sample rate
                        seconds = 10  # Duration of recording
                        print('Recording...')
                        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
                        sd.wait()  # Wait until recording is finished

                        tempFile = './temp/output.wav'
                        write(tempFile, fs, myrecording)

                        song = Song(tempFile)
                        fprints = song.genFprints()
                        name = DBExcutor.findSongByFprints(fprints)
                except:
                        print('Có lỗi.')

        print(name)
        
        print(time() - t)
