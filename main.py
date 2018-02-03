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
START_PRINTDATA = False

# Exit Flag
STOP_PRINTDATA = False

# 20180124 020010 6360000;89.815;89.81;89.815;2
def getData(row_data):

	d = {}
	data = row_data.split(';')
	if(len(data) > 0):
		date_time = data[0].split(' ')
		if(len(date_time) > 0):
			d['date'] = date_time[0]
			d['time'] = date_time[1]
			d['millis'] = date_time[2]
			d['tick'] = data[1]
	return d

def waitMilis(dict_data,old_time):

	date_tmp = '%s %s' % (dict_data['date'],dict_data['time'])
	millis_tmp = int(dict_data['millis'])/10000
	dt = datetime.datetime.strptime(date_tmp,'%Y%m%d %H%M%S') + datetime.timedelta(milliseconds=millis_tmp)

	date_tmp = '%s %s' % (old_time['date'],old_time['time'])
	millis_tmp = int(old_time['millis'])/10000
	dt_old = datetime.datetime.strptime(date_tmp,'%Y%m%d %H%M%S') + datetime.timedelta(milliseconds=millis_tmp)

	delta = dt-dt_old
	sleep_time = float(delta.total_seconds())
	time.sleep(sleep_time)

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

def printData(filename):

	try:
		# Global Dictionary to acess all data
		global d
		d[filename] = 0

		# Wait for the signal to start send data
		while(not START_PRINTDATA):
			time.sleep(0.1)

		current_day = 20000101
		first = True
		lista = []
		# Get the first data
		with open(filename,'a+') as myfile:
			for line in myfile:
				dict_data = getData(line)

				if(not dict_data['date'] == current_day):
					first = True
					current_day = dict_data['date']

				if(first):
					old_time = dict_data
					percent = 0.0
					tick_base = float(dict_data['tick'])
					first = False
				else:
					percent = percent + ((float(dict_data['tick'])-float(old_time['tick']))/tick_base)*100

				waitMilis(dict_data,old_time)
				old_time = dict_data

				d[filename] = (dict_data['date'],dict_data['time'],float(dict_data['tick']),'%.2f' % percent)

				if(STOP_PRINTDATA):
					d[filename] = -1
					return
	except:
		print(traceback.format_exc())
		d[filename] = -1

def main():

	try:
		global START_PRINTDATA

		# Get the List of Instruments from ListOfInstruments.txt
		loi = getListOfInstruments('ListOfInstruments.txt')
		list_threads = []

		# Create a list of Threads
		for filename in loi:
			thPrintData = Thread(target = printData, args = (filename,))
			list_threads.append(thPrintData)
		
		# Start all Threads, but keep them waiting
		for th in list_threads:
			th.daemon = True
			th.start()

		time.sleep(1)

		START_PRINTDATA = True
		while(1):
			print(chr(27) + "[2J")
			os.system('clear')
			for key,value in d.iteritems():
				print '[%s] = %s' % (key,value)
			time.sleep(1)

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

if __name__=="__main__":
	main()

