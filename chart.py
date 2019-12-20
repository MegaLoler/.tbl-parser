#!/usr/bin/env python3

import sys
import parse



### CHART ###

def chart(tables):
    '''Display a visual chart given tables.'''

    # TODO



### MAIN ###

def load(path):
    '''Load tables from a file give its path.'''

    with open(path) as f:
        return list(parse.Block.read_all(f))

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        print('Please specify the path(s) to the file(s) you want to visualize.')
    else:
        chart(sum(map(load, args), []))
