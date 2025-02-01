#!/usr/bin/env python

import time
import glob
import keyboard
import subprocess
import vlc

import sys
import tty
import termios
import select
#import tkinter as tk


def get_dir_files(dir_):
    where = dir_ + "/*.mp3"
    files = sorted(glob.glob(where))
    return files

def play_one_file(player):
    killit = False
    try:
        player.play()
        time.sleep(0.5)
        while True:
            # Check for input with timeout
            if select.select([sys.stdin], [], [], 0.1)[0]:  # 0.1 second timeout
                c = sys.stdin.read(1)
                if c == 'p':
                    if player.is_playing():
                        player.pause()
                        print("Paused\r")
                    else:
                        player.play()
                        print("Playing\r")
                elif c == 'q':
                    player.stop()
                    break
                elif c == 'z':
                    player.stop()
                    killit = True
                    break

            # Check if song has finished
            if not player.is_playing() and player.get_state() == vlc.State.Ended:
                print("Playback finished\r")
                break
            time.sleep(0.1)
    except Exception as ex:
        print(ex)
    return killit


def play_files(files):
    global instance, player
    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        # Set terminal to raw mode
        tty.setraw(fd)
        instance = vlc.Instance('--aout=pulse')
        player = instance.media_player_new()
        for afile in files:
            print("\rplaying {}\r".format(afile))
            media = instance.media_new(afile)
            player.set_media(media)
            killit = play_one_file(player)
            if killit:
                break


    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)



def play_mp3_select(player, filename):
    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        # Set terminal to raw mode
        tty.setraw(fd)

        # Setup player
        player = vlc.MediaPlayer(filename)
        player.play()

        print("\rPlaying... Press 'p' to pause/resume, 'q' to quit")

        while True:
            # Check for input with timeout
            if select.select([sys.stdin], [], [], 0.1)[0]:  # 0.1 second timeout
                c = sys.stdin.read(1)
                if c == 'p':
                    if player.is_playing():
                        player.pause()
                        print("Paused")
                    else:
                        player.play()
                        print("Playing")
                elif c == 'q':
                    player.stop()
                    break

            # Check if song has finished
            if not player.is_playing() and player.get_state() == vlc.State.Ended:
                print("\nPlayback finished")
                break

    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def play_mp3(file_path):
    # Create a VLC instance
    instance = vlc.Instance()
    
    # Create a media player
    player = instance.media_player_new()
    
    # Create a media object
    media = instance.media_new(file_path)
    
    # Set the media to the player
    player.set_media(media)
    
    # Play the media
    player.play()
    
    # Wait for the media to start playing
    time.sleep(0.5)
    
    # Get the duration (in milliseconds)
    duration = player.get_length() / 1000
    
    print(f"Playing: {file_path}")
    print(f"Duration: {duration:.2f} seconds")
    
    # Keep the script running while the audio plays
    while True:
        if keyboard.is_pressed('space'):
            if player.is_playing():
                player.pause()
                print("Paused")
            else:
                player.play()
                print("Resumed")
            time.sleep(0.3)  # Prevent multiple triggers
            
        if keyboard.is_pressed('q'):
            player.stop()
            print("Playback stopped")
            break
            
        if not player.is_playing() and player.get_state() == vlc.State.Ended:
            print("Playback finished")
            break
            
        time.sleep(0.1)



if __name__ == '__main__':
    
    if False:
        from argparse import ArgumentParser
        parser = ArgumentParser()
        parser.add_argument('-d', '--directory', help='directory of files to play')
        parser.add_argument('-s', '--song', help='play one song')
        parser.add_argument('-p', '--picker', help='open picker', action="store_true")
        files = []
        args = parser.parse_args()
        if args.directory:
            files = get_dir_files(args.directory)
        if args.picker:
            print("not today")
        if args.song:
            files = [args.song]
    else:
        files = get_dir_files(sys.argv[1])
    play_files(files)


