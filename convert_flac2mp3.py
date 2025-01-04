#!.venv/bin/python
# file : convert_flac2mp3.py
# convert flac to mp3 recursively and in place
# can delete flac if required.
__author__ = "Marcel Gerber"
__date__ = "2025-01-04"


# system modules
import os, sys
import argparse
import subprocess
import multiprocessing

# variables
processes = []

# classes

class Help(object):
	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('path', type=str, help='Path from which to start conversion')
		parser.add_argument('-d, --delete', action='store_true', help='Delete FLAC file after conversion')
		# parse_args defaults to [1:] for args, but you need to
		# exclude the rest of the args too, or validation will fail
		self.args = parser.parse_args()


class Process(multiprocessing.Process):
	def __init__(self, path:str, delete:bool=False): 
		super(Process, self).__init__() 
		self.path = path
		self.base, self.ext = os.path.splitext(path)
		self.delete = delete
				 
	def run(self):
		print(f"Converting file '{self.path}'.")
		# run conversion
		subprocess.run(['ffmpeg', '-i', self.path, '-ab', '320k', '-map_metadata', '0', '-id3v2_version', '3', '-qscale:a', '0', f"{self.base}.mp3"])
		
		# delete source file if requested
		if self.delete:
			try:
				os.remove(self.path)
				print(f"Successfully removed '{self.path}'.")
			except:
				print(f"Warning: could not remove '{self.path}'. {sys.exc_info()[0]}")


def recurse_folders(path:str, delete:bool):
	global processes
	print(f"Entering folder: '{path}'.")

	for item in os.listdir(path):
		item = os.path.join(path, item)
		if os.path.isfile(item):
			base, ext = os.path.splitext(item)
			if ext.lower() == '.flac':
				p = Process(item, delete)
				processes += [p]
				p.start()
				# p.join()
		elif os.path.isdir(item):
			recurse_folders(item, delete)
		else:
			print(f"skip item '{item}' because it's neither a file nor a folder.")



if __name__ == "__main__":
	help = Help()
	path = os.path.abspath(help.args.path)
	if not os.path.isdir(path):
		print(f"Path '{path}' is not a directory. Exiting.")
		sys.exit(1)
	
	recurse_folders(path, False)
