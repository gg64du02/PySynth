#!/usr/bin/env python

"""
##########################################################################
#                       * * *  PySynth  * * *
#       A very basic audio synthesizer in Python (www.python.org)
#
#          Martin C. Doege, 2017-06-20 (mdoege@compuserve.com)
##########################################################################
# Based on a program by Tyler Eaves (tyler at tylereaves.com) found at
#   http://mail.python.org/pipermail/python-list/2000-August/041308.html
##########################################################################

# 'song' is a Python list (or tuple) in which the song is defined,
#   the format is [['note', value]]

# Notes are 'a' through 'g' of course,
# optionally with '#' or 'b' appended for sharps or flats.
# Finally the octave number (defaults to octave 4 if not given).
# An asterisk at the end makes the note a little louder (useful for the beat).
# 'r' is a rest.

# Note value is a number:
# 1=Whole Note; 2=Half Note; 4=Quarter Note, etc.
# Dotted notes can be written in two ways:
# 1.33 = -2 = dotted half
# 2.66 = -4 = dotted quarter
# 5.33 = -8 = dotted eighth
"""

from __future__ import division
from demosongs import *
from mkfreq import getfreq

pitchhz, keynum = getfreq(pr = True)

##########################################################################
#### Main program starts below
##########################################################################
# Some parameters:

# Beats (quarters) per minute
# e.g. bpm = 95

# Octave shift (neg. integer -> lower; pos. integer -> higher)
# e.g. transpose = 0

# Pause between notes as a fraction (0. = legato and e.g., 0.5 = staccato)
# e.g. pause = 0.05

# Volume boost for asterisk notes (1. = no boost)
# e.g. boost = 1.2

# Output file name
#fn = 'pysynth_output.wav'
##########################################################################

import wave, math, struct
from mixfiles import mix_files

from math import sin
from math import exp
from math import pi


def make_wav(song,bpm=120,transpose=0,pause=.05,boost=1.1,repeat=0,fn="out.wav", silent=False):
	f=wave.open(fn,'w')

	f.setnchannels(1)
	f.setsampwidth(2)
	f.setframerate(44100)
	f.setcomptype('NONE','Not Compressed')

	bpmfac = 120./bpm

	def length(l):
		return 88200./l*bpmfac

	def waves2(hz,l):
		a=44100./hz
		b=float(l)/44100.*hz
		return [a,round(b)]

	def sixteenbit(x):
		return struct.pack('h', round(32000*x))

	def render2(a,b,vol,note):
		print(a,b,vol)
		b2 = (1. - pause) * b
		l = waves2(a, b2)
		ow = b''
		q = int(l[0] * l[1])
		print('q',q)

		halfp = l[0] / 2.
		sp = 0
		fade = 1

		notes = (
			# 'a', 'a#', 'b', 'c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#'
			# ('note',('frequencies'),('amplitude'),('phase'))
			('a',(886.658,1326.6,1772.5),(2150.2,171.1,35.6)),
			('a#',(943.029,1886.2,2829.1),(2893.2,230.8,90)),

			('b',(998.325,1995.5,2993.7),(1716.6,225.9,120.1)),

			('c',(526.205,1051.5,1579.7,2103.2,2633.1),(1522.4,611.3,412.6,195.7,66.1)),
			('c#',(558.039,1115.9,1674.5,2232.3,2786.4),(1086.9,438.5,243.4,69.7,54.7)),

			('d',(589.977,1176.9,1765.6,2360.1,2942.7),(809.6,646.93,177.55,104.92,56.93)),
			('d#',(624.512,1248.8,1873.9,2494.2),(1108.1,467.8,219.7,85.6)),

			('e', (662.061,1324.3,1986.6), (1358.2,404.9,345.9)),

			('f', (700.045,1399.5,2099), (2137.4,504.1,392.4)),
			('f#', (747.028,1493.4,2239), (1876.7,482,216)),

			('g', (786.977,1573.4,2360.2), (1649.2,228.8,184.2)),
			('g#', (833.219,1666.3,2489.6), (1328.3,501.3,38.6)),

		)

		for l in notes:
			print('l',l)
			# l[0] is the note
			if(l[0] == note):
				print('note',note)
				frequencies_note = l[1]
				amplitudes_note = l[2]
				print('frequencies_note',frequencies_note)
				print('amplitudes_note',amplitudes_note)
				# number_harms = len(l[1])
				# for k in range(number_harms):
				# 	break

		for x in range(q):

			# factor = .0001
			factor = 1 / b * 2 * pi

			sp = .3*sin(a * (1) * factor * x)
			sp = sp + (.3/4)*sin(a * (1 + 1) * factor * x)
			# sp = sp + .3*sin(a * (1 + 2) * factor * x)
			# sp = sp + .1*sin(a * (1 + 3) * factor * x)
			# sp = sp * (1 + .1* sin(0.001*x))

			ow = ow + sixteenbit(.5 * vol * sp)
		fill = max(int(ex_pos - curpos - q), 0)
		f.writeframesraw((ow) + (sixteenbit(0) * fill))
		return q + fill

	##########################################################################
	# Write to output file (in WAV format)
	##########################################################################

	if silent == False:
		print("Writing to file", fn)
	curpos = 0
	ex_pos = 0.
	for rp in range(repeat+1):
		for nn, x in enumerate(song):
			if not nn % 4 and silent == False:
				print("[%u/%u]\t" % (nn+1,len(song)))
			if x[0]!='r':
				if x[0][-1] == '*':
					vol = boost
					note = x[0][:-1]
				else:
					vol = 1.
					note = x[0]
				try:
					print("note:",note)
					a=pitchhz[note]
				except:

					a=pitchhz[note + '4']	# default to fourth octave
				a = a * 2**transpose
				if x[1] < 0:
					b=length(-2.*x[1]/3.)
				else:
					b=length(x[1])
				ex_pos = ex_pos + b
				curpos = curpos + render2(a,b,vol,note)

			if x[0]=='r':
				b=length(x[1])
				ex_pos = ex_pos + b
				f.writeframesraw(sixteenbit(0)*int(b))
				curpos = curpos + int(b)

	f.writeframes(b'')
	f.close()
	print()

##########################################################################
# Synthesize demo songs
##########################################################################

if __name__ == '__main__':
	print()
	print("Creating Demo Songs... (this might take about a minute)")
	print()

	# LOL1
	make_wav(lol1, fn = "lol1.wav")

	# # SONG 1
	# make_wav(song1, fn = "pysynth_scale.wav")
    #
	# # SONG 2
	# make_wav(song2, bpm = 95, boost = 1.2, fn = "pysynth_anthem.wav")
    #
	# # SONG 3
	# make_wav(song3, bpm = 132/2, pause = 0., boost = 1.1, fn = "pysynth_chopin.wav")

	# SONG 4
	#   right hand part
	# make_wav(song4_rh, bpm = 130, transpose = 1, pause = .1, boost = 1.15, repeat = 1, fn = "pysynth_bach_rh.wav")
	#   left hand part
	# make_wav(song4_lh, bpm = 130, transpose = 1, pause = .1, boost = 1.15, repeat = 1, fn = "pysynth_bach_lh.wav")
	#   mix both files together
	# mix_files("pysynth_bach_rh.wav", "pysynth_bach_lh.wav", "pysynth_bach.wav")

