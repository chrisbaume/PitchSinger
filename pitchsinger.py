#
# PitchSinger.py
#
# (c) 2013 Chris Baume
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#-----------------
#
# Generates an audio signal based on time/pitch values provided in a
# comma-separated value file and writes it to a .wav file (if a filename is
# given) or plays it using the default sound card.
#
# Input .csv format:
# <time in seconds>,<pitch in Hz>
#
# Example input:
# 0.058,214.92
# 0.069,287.87
# 0.081,361.61
# 0.092,368.18
# 0.104,376.28

import csv
import sys, getopt
import numpy as np
import pygame as pg
from scipy import signal
from scipy.io import wavfile

DEFAULT_SHAPE='triangle'
FS, BITS, BUF_LEN, CHANNELS = 22050, -16, 4096, 1
MAX_INT=2**15 - 1

# Generate one period of a waveform at a given frequency and return as a 16-bit
# signed integer numpy array
def wavegen(freq, shape=None):

  if shape is None:
    shape='sine'

  if shape=='sine':
    wave = MAX_INT * np.sin(2.0 * np.pi * float(freq) * \
           np.arange(0, np.floor(FS/freq)) / float(FS))
  elif shape=='sawtooth':
    wave = MAX_INT * signal.sawtooth(2.0 * np.pi * float(freq) * \
           np.arange(0, np.floor(FS/freq)) / float(FS))
  elif shape=='triangle':
    wave = np.concatenate( [\
           MAX_INT * signal.sawtooth(2.0 * np.pi * float(freq) * \
           np.arange(0, np.floor(FS/freq/2)) / float(FS)), \
           MAX_INT * signal.sawtooth(2.0 * np.pi * float(freq) * \
           np.arange(np.floor(FS/freq/2), np.floor(FS/freq)) / float(FS), \
           width=0)] )

  return np.array(wave, dtype=np.int16)

# Play the given 16-bit signed integer numpy array
def playwave(wave):

  # send wave to sound card
  sound = pg.sndarray.make_sound(wave)
  sound.play()

  # wait until sound has stopped
  endtime=int(wave.shape[0]/FS*1000)
  time=0
  print ""
  while (time<endtime):
    sys.stdout.write("\r{}  ".format(time/1000.0))
    sys.stdout.flush()
    time=time+pg.time.delay(100)

# Returns the pitch (in Hz) at a requested time, given the time/pitch data
def findpitch(time, data):

  for i in range(1,len(data)):
    if time<data[i][0] and data[i-1][1] > 0:
      return data[i-1][1]

# Prints the correct usage and exits
def printUsage():

  print 'Usage: pitchsinger.py [--shape=triangle] input.csv [output.wav]'
  sys.exit(-1)

if __name__ == '__main__':

  # parse arguments
  try:
    opts, args = getopt.getopt(sys.argv[1:],"",["shape="])
  except getopt.GetoptError:
    printUsage()

  # process options
  shape=DEFAULT_SHAPE
  for opt, arg in opts:
    if opt == '--shape':
      if arg in ('sine','triange','sawtooth'):
        shape=arg
      else:
        print("WARNING: Unrecognised wave shape,"\
              " using {} instead").format(DEFAULT_SHAPE)

  # process arguments
  if len(args)<1 or len(args)>2:
    printUsage()
  infilename=args[0]
  outfilename=None
  if len(args)>1:
    outfilename=args[1]

  # Set up PyGame
  print("Initialising pygame...")
  pg.mixer.pre_init(FS, BITS, CHANNELS, BUF_LEN)
  pg.init()

  # Import pitch data
  print("Importing data...")
  data=[]
  endtime=0
  with open(infilename) as infile:
    reader=csv.reader(infile)
    for row in reader:
      time=float(row[0])
      pitch=float(row[1])
      if time > endtime: endtime=time
      data.append( (time, pitch) )

  # Generate waves
  print("Generating audio..."),
  time=0.0
  wave=np.array([], dtype=np.int16)
  while (time<endtime):
    pitch = findpitch(time, data)
    waveform = wavegen(pitch, shape=shape)
    wave = np.concatenate( [wave, waveform] )
    time = time + waveform.shape[0]/float(FS)
    sys.stdout.write("\rGenerating audio... {}% ".format(int(time/endtime*100)))
  print ""

  # write or play waveform
  if outfilename!=None:
    print("Writing .wav file...")
    wavfile.write(outfilename, FS, wave)
  else:
    print("Playing audio...")
    playwave(wave)

