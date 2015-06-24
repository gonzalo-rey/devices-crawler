#!/usr/bin/python

import os
import re
import sys
import urllib
import urllib2
import multiprocessing as mp

def getDeviceFromSMAUG(url):
	# Have to specify a User-Agent so that it doesn't return a 403 Forbidden
	request = urllib2.Request(url = url, headers = {'User-Agent': 'Mozilla/5.0'})
	response = urllib2.urlopen(request).read()

	match = re.match('.*\"web_platform\":\"([a-zA-Z0-9]+)\".*', response)
	if match is not None:
		device = match.group(1)
	else:
		device = 'NO DEVICE_SMAUG'
		print "No web_platform obtained:'" + response + "'"

	return device


def getDeviceFromATLAS(url):
	match = re.match('.*devices\/(.*)', url)
	if match is not None:
		user_agent = match.group(1)
		
		request = urllib2.Request(url = "http://myolx.com.ar/i2/ajax/token/mytest/", headers = {'User-Agent': user_agent})
		response = urllib2.urlopen(request).read()

		match = re.match("^.*'>'(.*)'<.*\n.*", response)

		if match is not None:
			device = match.group(1)
		else:
			device = 'NO_DEVICE_ATLAS'
	else:
		print "No User-Agent obtained:'" + url + "'"
		device = 'NO_USER_AGENT'

	return device


def printDot():
	sys.stdout.write('.')
	sys.stdout.flush()


def printX():
	sys.stdout.write('x')
	sys.stdout.flush()


def printNewLine():
	sys.stdout.write('\n')
	sys.stdout.flush()


def printDict(name, dict, total):
	print name + ' ' + str(map(lambda x: (x[0], '%.2f%%' % (x[1] * 100.0 / total)), dict.items()))


def mergeDicts(dicts):
	if len(dicts) == 0:
		return dicts
	else: 
		return mergeDictsAux(dicts.pop(), dicts)


def mergeDictsAux(head, tail):
	if len(tail) == 0:
		return head
	else:
		p = tail.pop()
		for v in p.items():
			if v[0] in head:
				head[v[0]] += v[1]
			else:
				head[v[0]] = v[1]

		return mergeDictsAux(head, tail)


def printDicts(processors):
	result_dict = {'SMAUG':[], 'ATLAS':[]}

	for p in processors:
		while not p.output.empty():
			d = p.output.get()
			result_dict[d[0]].append(d[1])

	ATLAS_merged = mergeDicts(result_dict['ATLAS'])
	SMAUG_merged = mergeDicts(result_dict['SMAUG'])

	total = 0
	for v in ATLAS_merged.values():
		total += v
	
	printDict('ATLAS:', ATLAS_merged, total)
	printDict('SMAUG:', SMAUG_merged, total)
	print 'Total devices:' + str(total)


def processFile(file_name, output):
	# Open a file
	file = open(file_name, "r")
	print "Name of the file: ", file.name

	SMAUG_dict = dict()
	ATLAS_dict = dict()

	for line in file:
		try:
			match = re.match('.*(http:\/\/.*)\ HTTP.*', line)
			if match is not None:
				url = match.group(1)

				SMAUG_device = getDeviceFromSMAUG(url)
				ATLAS_device = getDeviceFromATLAS(url)

				if SMAUG_device in SMAUG_dict:
					SMAUG_dict[SMAUG_device] += 1
				else:
					SMAUG_dict[SMAUG_device] = 1

				if ATLAS_device in ATLAS_dict:
					ATLAS_dict[ATLAS_device] += 1
				else:
					ATLAS_dict[ATLAS_device] = 1

				printDot()
			else:
				printX()

		except KeyboardInterrupt, e:
			printNewLine()
			print 'Execution stopped!'
			break
		except Exception, e:
			printX()
	
	file.close()
	output.put(('SMAUG', SMAUG_dict))
	output.put(('ATLAS', ATLAS_dict))


class FileProcessor:
	def __init__(self, file_name):
		self.output = mp.Queue()
		self.file_name = file_name

		self.process = mp.Process(target = processFile, args = (self.file_name, self.output))


def processDir(dir):
	dir_aux = (dir + '/' if dir[-1:] != '/' else dir)
	file_names = [ dir_aux + f for f in os.listdir(dir_aux) if os.path.isfile(dir_aux + f) ]
	return [ FileProcessor(f) for f in file_names ]


def main():
	if(len(sys.argv) < 2):
		print 'Provide a least one file directory with several ones to analyse, i.e. ./devices-crawler.py file1|dir1 [file2|dir2 [...]]'
	else:
		try:
			file_paths = sys.argv[1:]

			processors = []
			total = 0

			for fp in file_paths:
				if os.path.isdir(fp):
					processors += processDir(fp)
				else:
					processors.append(FileProcessor(fp))

			for p in processors:
				p.process.start()			

			for p in processors:
				p.process.join()

		except Exception, e:
			print 'Que paso? ' + str(e)

		finally:
			printNewLine()
			printDicts(processors)


if __name__ == main():
    main()