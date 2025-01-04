# flac2mp3
Convert FLAC files to MP3 recursively using a python script and ffmpeg

The script uses multiprocessing to convert multiple flac files to mp3.
It uses the system's cpu count to determine the number of processes to 
start.

The path given as command-line argument will be recursed through in search
for flac files, which will be queued for conversion. The conversion takes
place in the same folder structure.

## Usage

```shell
python3 convert_flac2mp3.py <path>
```

## Improvments
- `argparse` usage for delete is not working: to correct.
