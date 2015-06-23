#!/usr/bin/python

import re
import sys
import urllib
import urllib2

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


def printValues(SMAUG_dict, ATLAS_dict):
	SMAUG_total = 0
	ATLAS_total = 0

	for v in SMAUG_dict.values():
		SMAUG_total += v

	for v in ATLAS_dict.values():
		ATLAS_total += v

	print 'SMAUG:' + str(map(lambda x: (x[0], '%.2f%%' % (x[1] * 100.0 / SMAUG_total)), SMAUG_dict.items()))
	print 'ATLAS:' + str(map(lambda x: (x[0], '%.2f%%' % (x[1] * 100.0 / ATLAS_total)), ATLAS_dict.items()))


def processFile(log, SMAUG_dict, ATLAS_dict):

	for line in log:
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

		except Exception, e:
			printX()


def main():
	if(len(sys.argv) < 2):
		print 'Provide at least one log to analyse, i.e. ./devices-crawler.py file1.log [file2.log [...]]'
	else:
		try:
			files = sys.argv[1:]

			SMAUG_dict = dict()
			ATLAS_dict = dict()
			total = 0

			for f in files:
				# Open a file
				log = open(f, "r")
				print "Name of the file: ", log.name

				processFile(log, SMAUG_dict, ATLAS_dict)

		except KeyboardInterrupt:
			printNewLine()
			print 'Execution stopped!'
		except Exception, e:
			print e

		finally:
			printNewLine()
			printValues(SMAUG_dict, ATLAS_dict)

			# Close opend file
			log.close()


if __name__ == main():
    main()