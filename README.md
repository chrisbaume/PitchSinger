PitchSinger.py
===

## Introduction

This python script reads a .csv containing time/pitch values and generates an
audio signal based on that. It can be written as a .wav file or played using
the sound card.

## Usage

    python pitchsinger.py [--shape=triangle] input.csv [output.wav]

####Shape options:

* triangle (default)
* sine
* sawtooth

## Input format

    <time in seconds>,<pitch in Hz>

Example:

    0.058,214.92
    0.069,287.87
    0.081,361.61
    0.092,368.18
    0.104,376.28
