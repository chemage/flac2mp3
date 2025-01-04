#!.venv/bin/python
# file : convert_flac2mp3.py
# convert flac to mp3 recursively and in place
# can delete flac if required.
# Source: https://www.digitalocean.com/community/tutorials/python-multiprocessing-example
__author__ = "Marcel Gerber"
__date__ = "2025-01-04"

# system modules
import os, sys
import argparse
import subprocess
import multiprocessing, queue, time


'''
Argument Parser
'''
class Help(object):
	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('path', type=str, help='Path from which to start conversion')
		parser.add_argument('-d, --delete', action='store_true', help='Delete FLAC file after conversion')
		self.args = parser.parse_args()


'''
Process function which converts flac to mp3.
Process will look for more files to be converted in the queue 
and add them to the second queue when completed.
- files_to_convert: Queue object of files to be converted.
- files_converted: Queue object of iles that have been converted.
'''
def do_job(files_to_convert, files_converted):
	while True:
		try:
			'''
				try to get task from the queue. get_nowait() function will 
				raise queue.Empty exception if the queue is empty. 
				queue(False) function would do the same task also.
			'''
			path = files_to_convert.get_nowait()
			base, ext = os.path.splitext(path)
			command = ['ffmpeg', '-i', path, '-ab', '320k', '-map_metadata', '0', '-id3v2_version', '3', '-qscale:a', '0', f"{base}.mp3"]
			sp = subprocess.run(command)
			# print(' '.join(command))

		except queue.Empty:
			break

		else:
			'''
				if no exception has been raised, add the task completion 
				message to task_that_are_done queue
			'''
			files_converted.put(path + ' is converted by ' + multiprocessing.current_process().name)
			time.sleep(.5)
	
	return True


'''
Build Queue by searching for flac files in folder structure.
- path: base directory
- delete: whether to delete flac files or not (not implemented)
'''
def recurse_folders(path:str, delete:bool):
	global files_to_convert
	print(f"Entering folder: '{path}'.")

	for item in os.listdir(path):
		item = os.path.join(path, item)
		if os.path.isfile(item):
			base, ext = os.path.splitext(item)
			if ext.lower() == '.flac':
				files_to_convert.put(item)
		elif os.path.isdir(item):
			recurse_folders(item, delete)
		else:
			print(f"Skip item '{item}' because it's neither a file nor a folder.")


if __name__ == "__main__":
	help = Help()
	cpu_count = multiprocessing.cpu_count()
	print("Number of cpu : ", cpu_count)
	path = os.path.abspath(help.args.path)
	if not os.path.isdir(path):
		print(f"Path '{path}' is not a directory. Exiting.")
		sys.exit(1)
	
	# initialize queues and process list
	files_to_convert = multiprocessing.Queue()
	files_converted = multiprocessing.Queue()
	processes = []

	# add jobs to queue
	recurse_folders(path, delete=False)

	# creating processes
	for w in range(cpu_count):
		p = multiprocessing.Process(target=do_job, args=(files_to_convert, files_converted))
		processes.append(p)
		p.start()

	# completing process
	for p in processes:
		p.join()

	# print the output
	print("")
	print("-- SUMMARY --")
	while not files_converted.empty():
		print(files_converted.get())
