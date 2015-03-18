#!/usr/bin/python

import time
import sys
import argparse
import simplejson
import os

file_actions = ['upload', 'get']

ap = argparse.ArgumentParser()
ap.add_argument('--action', choices=file_actions)
ap.add_argument('--debug', action='store_const', dest='isDebug', const=True, default=False)
ap.add_argument('--file')
rap = ap.parse_args()
print rap

if rap.action in file_actions and not rap.file:
    print 'Please specify file for <', rap.action, '>'

if rap.isDebug:
    print 'Debug mode is ON'


if __name__ == '__main__':

    filename = __file__[:__file__.rfind('.')+1]




