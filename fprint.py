import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from skimage.feature import peak_local_max
import hashlib
MD=20 #min_dítance
NOP = 5 # number of points in target zone

class Song():
  
  def __init__(self, filePath):
    self.song_id = 0
    self.filePath = filePath
    self.name = filePath.split('/')[-1].split('.')[0]
    self.audio, sr = librosa.load(self.filePath, mono=True)
    self.spectrogram = None
    self.peaks = self.__findPeaks() # mảng tọa độ đỉnh (i, j)
    
  
  def __findPeaks(self):
    self.spectrogram = librosa.amplitude_to_db(
      np.abs(
        librosa.stft(self.audio, n_fft=1024)
        ), 
      ref=np.max)
    D = self.spectrogram
    peaks = peak_local_max(D.T, min_distance=MD)
    peaks = np.fliplr(peaks)[::-1]
    med = np.median(D[peaks[:,0], peaks[:,1]])
    peaks = np.array([(i, j) for i,j in peaks if D[i][j] > med]) # lọc các đỉnh
    
    return peaks 

  def plotSpectrogram(self, plotPeaks=True):
    plt.figure(figsize=(25,4), facecolor='white')
    librosa.display.specshow(self.spectrogram)
    plt.colorbar(format='%+2.0f dB')
    if plotPeaks:
      plt.scatter(self.peaks[:, 1], self.peaks[:, 0])
    plt.title('Log power spectrogram')
    plt.show()

  def genFprints(self):
    n = len(self.peaks)
    fprints = []
    for i in range(n):
      for j in range(3, NOP + 3):
        if i+j < n:
          freq1 = self.peaks[i, 0]
          freq2 = self.peaks[i + j, 0]
          t1 = self.peaks[i, 1]
          t2 = self.peaks[i + j, 1]
          delta_t = t2 - t1
          hash = hashlib.sha1(
            ('%s|%s|%s' % (str(freq1), str(freq2), str(delta_t)))
            .encode('utf-8')
          )
          fprints.append(
            Fprint(self.song_id, t1, hash.hexdigest())
          )
    return np.array(fprints)


class Fprint:
  def __init__(self, song_id, offset, hash):
    self.song_id = song_id
    self.offset = offset
    self.hash = hash
  
