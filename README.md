# split.py
Command line tool to split MP3 audio file un multiple subtracks, assign ID3 tags and normalize audio volume.

## Dependencies
- python3
- python3-venv (`sudo apt install python3-venv`)
- eyeD3 (`sudo apt install eyed3`)
- ffmpeg (`sudo apt install ffmpeg`)
- replaygain
  ```
  sudo apt install libgirepository1.0-dev libcairo2-dev
  ```
  enable venv and install all requirements:
  ```
  pip install -r requirements.txt
  ```

## Usage
```
usage: split.py [-h] [-c CONF] [-d DIR] [SRC_FILE]

Command line tool to split mp3 files and set basical Id3 tags.

positional arguments:
  SRC_FILE              source audio file (overrides what specified in conf. file)

optional arguments:
  -h, --help            show this help message and exit
  -c CONF, --conf CONF  specify the configuration yaml file to use. (dafault splitconf.yml)
  -d DIR, --out-dir DIR
                        the name of the output directory where splits will put into
```
### YAML Configuration file format
Following an example of configuration file:
```
source: record_03.mp3
tracks:
  - start_time: "00:00:02.310"
    end_time: "00:02:21.400"
    title: 1x1
    artist: Galantis
    album:
    year: 2022
    cover:
    number: 1

  - start_time: "00:02:22.279"
    end_time: "00:05:38.000"
    title: Silver Screen (Shower Scene) [Club Mix]
    artist: Felix Da Housecat, David Guetta
    year: 2022

  - start_time: "00:05:38.641"
    end_time: "00:08:37.700"
    title: Run Away
    artist: Ian Storm, Ron van den Beuken, Menno
    year: 2020

  - start_time: "00:09:38.880"
    end_time: "00:12:56.000"
    title: Piece Of Art
    artist: Kryder
    year: 2021

  - start_time: "00:12:56.680"
    end_time: "00:15:32.000"
    title: It's A Fine Day
    artist: Maria Nayler
    year: 2019

  - start_time: "00:15:33.750"
    end_time: "00:24:20.000"
    title: Find (Andy Moor Remix)
    artist: Ridgewalkers, EL
    year: 2004

  - start_time: "00:24:25.068"
    end_time: "00:27:51.700"
    title: Chase The Sun (Consoul Trainin Remix)
    artist: Planet Funk, Consoul Trainin
    year: 2017

  - start_time: "00:27:51.744"
    end_time: "00:30:52.185"
    title: Space Melody (Edward Artemyev)
    artist: VIZE, Alan Walker, Edward Artemyev
    year: 2020
```
* __source__: name of the mp3 source file we want to split.
* __tracks__: the list of track the source file is made of.
* __tracks[*].title__: the title of the track (optional)
* __tracks[*].album__: the album of the track (optional)
* __tracks[*].artist__: the artist of the track (optional)
* __tracks[*].year__: the release year of the track (optional)
* __tracks[*].number__: the track number (optional)
* __tracks[*].cover__: the name of the file to set as cover image (optional)
* __tracks[*].start_time__: the start time of the track (mandatory)
* __tracks[*].end_time__: the end time of the track (mandatory)

`start_time` and `end_time` are used to cut the source audio file to extract the related audio track.

## Notes
- The source file will left intact after the splitting proces.
- Every time `split.py` runs, a new output directory will be created in the current working directory. The name for output directory follows this pattern `^out_[0-9]+$`. If a destination folder is specified, that folder will be used instead.
- After the plitting of all the tracks, the volume of each one is normalized.
