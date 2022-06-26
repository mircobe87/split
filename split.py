#!/usr/bin/env python3

import argparse
import yaml
import os
import re
import sys


def check_source_file(source_file_name):
    if source_file_name is None:
        sys.exit("[ERROR] No source file name specified.")
    if not os.path.exists(source_file_name):
        sys.exit("[ERROR] The provided audio source file does not exist: {}".format(source_file_name))
    return source_file_name


def get_outdir_name():
    max_index = -1
    dir_names = [x[0] for x in os.walk('.')]
    for dirname in dir_names:
        dirname_match = re.match('^\./out_([0-9]+)$', dirname)
        if dirname_match is not None:
            curr_index = int(dirname_match[1])
            if curr_index > max_index:
                max_index = curr_index
    return "out_{}".format(str(max_index + 1))


def tag_data(track_data):
    year = str(track_data['year']) if 'year' in track_data and track_data['year'] is not None else '<year>'
    album = track_data['album'] if 'album' in track_data and track_data['album'] is not None else '<album>'
    artist = track_data['artist'] if 'artist' in track_data and track_data['artist'] is not None else '<artist>'
    title = track_data['title'] if 'title' in track_data and track_data['title'] is not None else '<title>'
    return (year, album, artist, title)


def get_filename(track_data):
    year, album, artist, title = tag_data(track_data)
    return "{}[{}]__{}-{}.mp3".format(year, album, artist, title)


parser = argparse.ArgumentParser(description='Command line tool to split mp3 files and set basical Id3 tags.')
parser.add_argument('-c', '--conf',
                    help='specify the configuration yaml file to use. (dafault splitconf.yml)',
                    action='store', default='splitconf.yml')
namespace = parser.parse_args()

with open(namespace.conf, 'r') as conf_file:
    conf = yaml.safe_load(conf_file)

    source_audio_filename = check_source_file(conf['source'])
    out_dirname = get_outdir_name()
    os.mkdir(out_dirname)

    track_index = 0
    for track in conf['tracks']:
        if track['start_time'] is None:
            print("[WARN] No start time provided for track at index {}. Skipping this track.".format(track_index))
            continue
        if track['end_time'] is None:
            print("[WARN] No end time provided for track at index {}. Skipping this track.".format(track_index))
            continue

        audio_filename = get_filename(track)

        os.system('ffmpeg -i {} -vn -acodec copy -ss {} -to {} "{}/{}"'.format(
            source_audio_filename,
            track['start_time'], track['end_time'],
            out_dirname, audio_filename))

        os.system('eyeD3 --remove-all "{}/{}"'.format(out_dirname, audio_filename))

        command_options = ''
        if 'year' in track and track['year'] is not None:
            command_options = command_options + ' -Y ' + str(track['year'])
        if 'title' in track and track['title'] is not None:
            command_options = command_options + ' -t "' + track['title'] + '"'
        if 'artist' in track and track['artist'] is not None:
            command_options = command_options + ' -a "' + track['artist'] + '"'
        if 'album' in track and track['album'] is not None:
            command_options = command_options + ' -A "' + track['album'] + '"'
        if 'cover' in track and track['cover'] is not None:
            command_options = command_options + ' --add-image="' + track['cover'] + ':FRONT_COVER"'

        os.system('eyeD3 {} "{}/{}"'.format(command_options, out_dirname, audio_filename))

    os.system('replaygain {}/*.mp3'.format(out_dirname))
