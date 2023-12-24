#!/usr/bin/env python3

import argparse
import yaml
import os
import re
import sys


def check_source_file(source_file_name :str, cli_source_file_name :str) -> str:
    if source_file_name is None and cli_source_file_name is None:
        sys.exit("[ERROR] No source file name specified.")
    file_name = cli_source_file_name if cli_source_file_name is None else source_file_name

    if not os.path.exists(file_name):
        sys.exit("[ERROR] The provided audio source file does not exist: {}".format(file_name))
    return file_name


def get_outdir_name(dirname:str) -> str:
    if dirname is not None and len(dirname) > 0:
        return dirname
    else:
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
    year = str(track_data['year']) if 'year' in track_data and track_data['year'] is not None else ''
    album = track_data['album'] if 'album' in track_data and track_data['album'] is not None else ''
    artist = track_data['artist'] if 'artist' in track_data and track_data['artist'] is not None else ''
    title = track_data['title'] if 'title' in track_data and track_data['title'] is not None else ''
    number = str(track_data['number']) if 'number' in track_data and track_data['number'] is not None else ''
    return (year, album, artist, title, number)


def get_filename(track_data):
    year, album, artist, title, number = tag_data(track_data)
    if len(album) == 0:
        return "{}_{}-{}-{}.mp3".format(year, number, artist, title)
    return "{}[{}]_{}-{}-{}.mp3".format(year, album, number, artist, title)


parser = argparse.ArgumentParser(description='Command line tool to split mp3 files and set basical Id3 tags.')
parser.add_argument('source',
                    help='source audio file (overrides what specified in conf. file)',
                    metavar="SRC_FILE",
                    nargs='?',
                    default=None)
parser.add_argument('-c', '--conf',
                    help='specify the configuration yaml file to use. (dafault splitconf.yml)',
                    action='store', default='splitconf.yml')
parser.add_argument('-d', '--out-dir',
                    help='the name of the output directory where splits will put into',
                    action='store',
                    metavar='DIR',
                    dest='out_dir',
                    required=False)
namespace = parser.parse_args()

with open(namespace.conf, 'r') as conf_file:
    conf = yaml.safe_load(conf_file)

    source_audio_filename = check_source_file(conf['source'], namespace.source)
    out_dirname = get_outdir_name(namespace.out_dir)
    if not os.path.exists(out_dirname):
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

        os.system('ffmpeg -y -i {} -vn -acodec copy -ss {} -to {} "{}/{}"'.format(
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
        if 'number' in track and track['number'] is not None:
            command_options = command_options + ' -n "' + str(track['number']) + '"'

        os.system('eyeD3 {} "{}/{}"'.format(command_options, out_dirname, audio_filename))

    os.system('replaygain {}/*.mp3'.format(out_dirname))
