#!/usr/bin/python

import sys
import os

def main():
	if(len(sys.argv) < 3):
		print 'Provide one file and the number of lines it should be splitted to, i.e. ./file-splitter.py file_path lines_per_file [new_directory]'
	else:
		try:
			# Get the initialization parameters			
			file_path = sys.argv[1]
			lines_per_file = long(sys.argv[2])
			new_directory = ''
			if sys.argv >= 4:
				new_directory = sys.argv[3]
				if new_directory[-1:] != '/':
					new_directory += '/'
				try:
					os.mkdir(new_directory)
				except OSError:
					pass

			# Open a file
			f = open(file_path, "r")
			print "Name of the file: ", f.name

			i = 0
			j = 0
			fi = open(new_directory + file_path + '_' + str(j), "w")
			for line in f:
				if i == lines_per_file:
					fi.close()
					i = 0
					j += 1
					fi = open(new_directory + file_path + '_' + str(j), "w")

				i += 1
				fi.write(line)

			fi.close()

		except Exception, e:
			print e


if __name__ == main():
    main()