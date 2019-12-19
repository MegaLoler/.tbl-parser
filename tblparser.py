#!/usr/bin/env python3

import sys
import io



### TOKENIZER ###

def peek(stream):
    c = stream.peek()
    return c, len(c)

def consume(stream, predicate, peek_func=None):
    '''Consume bytes from a stream as long as a condition is met.'''

    token = ''
    while True:
        chunk, size = (peek_func or peek)(stream)
        if size and predicate(chunk):
            stream.read(size)
            token += chunk
        else:
            break

    return token

def consume_whitespace(stream, *args, **kwargs):
    '''Consume bytes from a stream until no more whitespace is found.'''

    return consume(stream, lambda c: c.isspace(), *args, **kwargs)

def consume_not_whitespace(stream, *args, **kwargs):
    '''Consume bytes from a stream until whitespace is found.'''

    return consume(stream, lambda c: not c.isspace(), *args, **kwargs)

def consume_in(stream, chars, *args, **kwargs):
    '''Consume bytes as long as they are in a given set of characters.'''

    return consume(stream, lambda c: c in chars, *args, **kwargs)

def consume_not_in(stream, chars, *args, **kwargs):
    '''Consume bytes as long as they are NOT in a given set of characters.'''

    return consume(stream, lambda c: c not in chars, *args, **kwargs)

def consume_line(stream, *args, **kwargs):
    '''Consume the rest of the line without the newline.'''

    return consume_not_in(stream, '\n')

def consume_delimited(stream, delimiter):
    '''Consume a delimited string until the non-escaped delimiter is found.'''

    def peek_escape(stream):
        c = stream.peek()
        return ((stream.read(1) and stream.peek()) if c == '\\' else c), len(c)

    def read_delimiter():
        assert(stream.read(1) == delimiter)

    # read the initial delimiter
    read_delimiter()

    # read until the final delimiter
    string = consume_not_in(stream, delimiter, peek_func=peek_escape)

    # read the final delimiter
    read_delimiter()

    return string

def consume_token(stream):
    '''Consume and return a single token from a stream.'''

    def peek_strip(stream):
        '''Look out for comments and ignore them.'''

        # strip comments
        while stream.peek() == ';':
            consume_line(stream)

        return peek(stream)

    def peek_token(stream):
        c = peek_strip(stream)[0]

        def peek_delimited():
            pos = stream.tell()
            token = consume_delimited(stream, c)
            stream.seek(pos)
            return token, len(token) + 2

        # check for string delimiters
        return peek_delimited() if c and c in ''''"''' else (c, len(c))

    # newlines are their own token
    # consolodate multiple newlines into one
    if stream.peek() == '\n':
        consume_in(stream, '\n')
        return '\n'

    # discard leading whitespace
    consume_whitespace(stream, peek_func=peek_strip)

    # consume until whitespace (catching quoted text as well)
    return consume_not_whitespace(stream, peek_func=peek_token)

def tokens(stream):
    '''Yield tokens from a stream.'''

    class Reader:
        def __init__(self, stream):
            self.stream = stream

        def __getattr__(self, name):
            return getattr(self.stream, name)

        def peek(self):
            pos = self.stream.tell()
            c = self.stream.read(1)
            self.stream.seek(pos)
            return c

    stream = Reader(stream)
    while token := consume_token(stream):
        yield token

def tokenize_string(string):
    '''Yield tokens from a string.'''

    return tokens(io.StringIO(string))



### TABLE SCHEMAS ###

# the spec string of tables themselves
TABLE_SCHEMA = '"table name" version schema'

class Schema:
    '''Represents a schema for a hierarchical table.'''

    def __init__(self, spec: str):
        '''Parse a schema from a spec string.'''



### PARSER ###

class Block:
    '''Represents a parsed block.'''

    @classmethod
    def read(cls, stream: str, schema: Schema):
        '''Parse a block from a stream according to a schema.'''

    @classmethod
    def parse(cls, string: str, schema: Schema):
        '''Parse a block from a string according to a schema.'''

        return cls.read(io.StringIO(string), schema);

    def __init__(self, header: dict, children: list):
        self.header = header     # the header field values
        self.children = children # the sub-elements



### MAIN ###

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Please specify the path to the file you want to parse.')
    else:
        with open(sys.argv[1]) as f:
            for token in tokens(f):
                print(token)
