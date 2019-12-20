#!/usr/bin/env python3

import sys
import io
import pprint



### TOKENIZER ###

def peek(stream):
    c = stream.peek()
    return c, len(c)

def consume(stream, predicate, peek_func=peek):
    '''Consume bytes from a stream as long as a condition is met.'''

    token = ''
    while True:
        chunk, size = peek_func(stream)
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

def consume_token(stream, peek_func=peek, discrete_tokens=''):
    '''Consume and return a single token from a stream.'''

    def peek_strip(stream):
        '''Look out for comments and ignore them.'''

        # strip comments
        while stream.peek() == ';':
            consume_line(stream)

        return peek_func(stream)

    def peek_token(stream):
        c = peek_strip(stream)[0]

        def peek_delimited():
            pos = stream.tell()
            token = consume_delimited(stream, c)
            stream.seek(pos)
            return token, len(token) + 2

        # check for string delimiters
        return peek_delimited() if c and c in ''''"''' else (c, len(c))

    # consolodate multiple discrete tokens and return them
    for c in discrete_tokens:
        if stream.peek() == c:
            consume_in(stream, c)
            return c

    # discard leading whitespace
    consume_whitespace(stream, peek_func=peek_strip)

    # consume until whitespace or discrete token (catching quoted text as well)
    return consume(stream, lambda c: not c.isspace() and c not in discrete_tokens, peek_func=peek_token)

def tokens(stream, peek_func=peek, discrete_tokens=''):
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
    consume_whitespace(stream)
    while token := consume_token(stream, peek_func, discrete_tokens):
        yield token

def tokenize_string(string, peek_func=peek, discrete_tokens=''):
    '''Yield tokens from a string.'''

    return tokens(io.StringIO(string), peek_func, discrete_tokens)



### TABLE SCHEMAS ###

class Schema:
    '''Represents a schema for a hierarchical table.'''

    @classmethod
    def parse_tokens(cls, tokens: list):
        '''Parse a schema from a token stream.'''

        if tokens:
            fields, rest = (tokens[:tokens.index(':')], tokens[tokens.index(':') + 1:]) if ':' in tokens else (tokens, [])
            return cls(fields, cls.parse_tokens(rest))

    @classmethod
    def parse(cls, spec: str):
        '''Parse a schema from a spec string.'''

        return cls.parse_tokens(list(tokenize_string(spec, discrete_tokens=':')))

    def __init__(self, fields: list, child):
        self.fields = fields
        self.child = child

table_schema = Schema.parse('"table name" version schema')



### PARSER ###

class Block:
    '''Represents a parsed block.'''

    @classmethod
    def read(cls, stream: str, schema: Schema = table_schema, level: int = 0):
        '''Parse a block from a stream according to a schema.'''

        if schema:

            # get the token stream
            pos = stream.tell()
            token_stream = tokens(stream)

            # see what the first token is
            try:
                first_token = next(token_stream)
            except StopIteration:
                return

            # if its a header level indicator
            # then it indicates the level
            # otherwise the level is simply one more than the last
            if all(map(lambda c: c == '#', first_token)):
                next_level = len(first_token)
            else:
                next_level = level + 1
                stream.seek(pos)

            # make sure we arent ascending (that would terminate the recursion)
            if next_level > level:
                header = dict(zip(schema.fields, token_stream))
                child_schema = Schema.parse(header['schema']) if level == 0 else schema.child
                children = list(cls.read_all(stream, child_schema, next_level))
                return cls(header, children)
            else:
                stream.seek(pos)

    @classmethod
    def read_all(cls, stream: str, schema: Schema = table_schema, level: int = 0):
        '''Read and yield all blocks from a stream.'''

        while block := cls.read(stream, schema, level):
            yield block

    @classmethod
    def parse(cls, string: str, schema: Schema):
        '''Parse a block from a string according to a schema.'''

        return cls.read(io.StringIO(string), schema);

    def __init__(self, header: dict, children: list):
        self.header = header     # the header field values
        self.children = children # the sub-elements

    @property
    def dict(self):
        return {**self.header, 'children': [child.dict for child in self.children]}

    def __getitem__(self, item):
        return self.dict[item]

def read_dict(stream):
    '''Parse a list of blocks from a stream and return the dictionary representation.'''

    return list(block.dict for block in Block.read_all(stream))



### MAIN ###

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        print('Please specify the path(s) to the file(s) you want to parse.')
    else:
        for arg in args:
            print(f'{arg}:')
            with open(arg) as f:
                pprint.PrettyPrinter(sort_dicts=False).pprint(read_dict(f))
