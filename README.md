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


## EXAMPLE

here's the test3.tbl file:
```
; here's a more practical example lol

; here's a table for keeping track of meals each day
# meals 1 "date: 'begin time' 'end time': 'food name' 'serving size'"

; here's a day entry
## 12/19/19

; heres a meal from 5:30 AM to 5:40 AM
### 5:30 5:40
"chicken strips" 1  ; i had "one serving of chicken strips" lol

### 9:00 9:01
"tiny cookies" 5    ; and at 9 o'clock i had 5 tiny cookies lol

; at 11:10 AM i took 15 minutes to eat a serving of mashed potatoes and one of green beans
### 11:10 11:25
"mashed potatoes" 1
"green beans"     ^


; next day
## 12/20/19

### 12:00 12:30
"chicken strips" 3

; ... etc etc
```

and parsing it with
```bash
python tblparser.py test3.tbl
```

returns this:
```python
[{'table name': 'meals',
  'version': '1',
  'schema': "date: 'begin time' 'end time': 'food name' 'serving size'",
  'children': [{'date': '12/19/19',
                'children': [{'begin time': '5:30',
                              'end time': '5:40',
                              'children': [{'food name': 'chicken strips',
                                            'serving size': '1',
                                            'children': []}]},
                             {'begin time': '9:00',
                              'end time': '9:01',
                              'children': [{'food name': 'tiny cookies',
                                            'serving size': '5',
                                            'children': []}]},
                             {'begin time': '11:10',
                              'end time': '11:25',
                              'children': [{'food name': 'mashed potatoes',
                                            'serving size': '1',
                                            'children': []},
                                           {'food name': 'green beans',
                                            'serving size': '^',
                                            'children': []}]}]},
               {'date': '12/20/19',
                'children': [{'begin time': '12:00',
                              'end time': '12:30',
                              'children': [{'food name': 'chicken strips',
                                            'serving size': '3',
                                            'children': []}]}]}]}]
```
