'''
Created on 02/02/2018

@author: artur
'''

from threading import Thread
import time
import datetime
import os
import traceback

# Global Dictionary with instruments data
d = {}

# Flag to start send data
START_UPDATEDATA = False

# Exit Flag
STOP_PRINTDATA = False

# Start check time, from user
CURRENT_TIME = datetime.datetime.now()

# 20180124 020010 6360000;89.815;89.81;89.815;2
def parseData(row_data):

	d_tmp = {}
	data = row_data.split(';')
	if(len(data) > 0):
		date_time = data[0].split(' ')
		if(len(date_time) > 0):
			d_tmp['date'] = date_time[0]
			d_tmp['time'] = date_time[1]
			d_tmp['millis'] = date_time[2]
			d_tmp['tick'] = data[1]
	return d_tmp

# add the file list in the ListOfInstruments.txt, one per line
# e.g:
# DX 03-18.Last.txt
# ES 03-18.Last.txt
# CL 03-18.Last.txt
def getListOfInstruments(filename):

	l = []
	with open(filename,'a+') as myfile:
		for line in myfile:
			l.append(line[:-1])

	return l

def getInstData(filename):

	try:

		# Global Dictionary to acess all data
		global d
		global LIST_FIRST_DATETIME

		d[filename] = -1

		#l = compressData(filename)

		# Wait for the signal to start update data
		while(not START_UPDATEDATA):
			time.sleep(0.1)

		first = True
		with open(filename,'a+') as myfile:
			for line in myfile:
				dict_data = parseData(line)
				tm = dict_data['time']
				tick = dict_data['tick']

				if(first):
					percent = 0.0
					tick_base = float(tick)
					old_tick = tick_base
					first = False
				else:
					percent = percent + ((float(tick)-float(old_tick))/tick_base)*100

				dt_tm = str2dt(tm)
				while(not CURRENT_TIME == dt_tm):
					if(CURRENT_TIME > dt_tm):
						flag_continue = True
						break
					if(STOP_PRINTDATA):
						break
					time.sleep(0.1)

				old_tick = tick

				if(flag_continue):
					flag_continue = False
					continue

				d[filename] = (tick,percent)

				if(STOP_PRINTDATA):
					d[filename] = -1
					break
		return

	except:
		print(traceback.format_exc())
		d[filename] = -1

def str2dt(s):

	dt = datetime.datetime.strptime(s,'%H%M%S')
	return dt

def main():

	try:
		global START_UPDATEDATA
		global CURRENT_TIME

		# Get the List of Instruments from ListOfInstruments.txt
		loi = getListOfInstruments('ListOfInstruments.txt')
		list_threads = []

		# Create a list of Threads
		for filename in loi:
			t_getData = Thread(target = getInstData, args = (filename,))
			list_threads.append(t_getData)
		
		# Start all Threads, but keep them waiting
		for th in list_threads:
			th.daemon = True
			th.start()

		CURRENT_TIME = str2dt(raw_input('Start Time (e.g 093000):'))

		START_UPDATEDATA = True
		while(1):
			print(chr(27) + "[2J")
			os.system('clear')
			for key,value in d.iteritems():
				if(not value == -1):
					print '%s [%s] = %.4f %.2f%%' % (CURRENT_TIME.time(),key,float(value[0]),float(value[1]))
				else:
					print '%s [%s] = ----' % (CURRENT_TIME.time(),key)
			time.sleep(1)
			CURRENT_TIME += datetime.timedelta(seconds=1)

		return

	except KeyboardInterrupt:
		
		print 'Exiting...'

		global STOP_PRINTDATA
		STOP_PRINTDATA = True

		lenght = len(d)
		c = 0
		while(c < lenght):
			for key,value in d.iteritems(): 
				if(value == -1):
					c += 1
			if(c >= lenght):
				break
		return

def compressData(filename):

	d_compressed = {}
	with open(filename,'a+') as myfile:
		for line in myfile:
			dict_data = parseData(line)
			d_compressed[dict_data['time']] = dict_data['tick']

	l = []
	for key,value in sorted(d_compressed.items()):
		t = (key,value)
		l.append(t)

	return l

if __name__=="__main__":
	main()

