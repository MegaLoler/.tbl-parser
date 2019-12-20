# .tbl parser

script to parse .tbl format:

messy notes lol:

- heading hearirchies, no # is “last level” , and the rest are the level indicated by number of #s
- _ means NULL
- ? means UNKNOWN (different from null!!!)
- ^ means DITTO
- ' and " are the two string delimiters, can be used exchangable and nested alternatively
- thins are space separated and spacing is IGNORED otherwise, excetp quotede things ofc, like bash!!
- ; is comment
- the table meta schema is '"table name" version schema'
- in schema format, its just a series of columns, but each level starts after a colon!!
- style wise, prefer " before '
- style wise, keep each table in its own file, but different versions as the schemas change can be in the same file at the end
- case retaining


TODO: replace "ditto" (^ character) with copies of the data from the previous row
