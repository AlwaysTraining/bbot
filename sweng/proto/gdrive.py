__author__ = 'dhkarimi'

#!/usr/bin/python

import time
import gdata.spreadsheet.service

email = 'derrick.karimi@gmail.com'
password = 'zzzzzzzzzzz'
weight = '180'
# Find this value in the url with 'key=XXX' and copy XXX below
spreadsheet_key = '0AlItClzrqP_edHoxMmlOcTV3NHJTbU4wZDJGQXVTTXc'
# All spreadsheets have worksheets. I think worksheet #1 by default always
# has a value of 'od6'
worksheet_id = 'od6'

client = gdata.spreadsheet.service.SpreadsheetsService()
client.email = email
client.password = password
client.source = 'Example Spreadsheet Writing Application'
client.ProgrammaticLogin()

query = gdata.spreadsheet.service.CellQuery()
query.max_row='2'
"""
query.min_row = 1
query.max_row = 2
query.min_col = 1
query.max_col = 2
"""

feed = client.GetCellsFeed(spreadsheet_key,query=query)
dir(feed)

for i, entry in enumerate(feed.entry):
    print i,entry.cell.inputValue

"""
for row in feed.entry:
    print row.cell.inputValue
"""

"""
for row in feed.entry:
    print dir(row)
    break
"""



"""
# Prepare the dictionary to write
dict = {}
dict['date'] = time.strftime('%m/%d/%Y')
dict['time'] = time.strftime('%H:%M:%S')
dict['weight'] = weight
print dict


entry = client.InsertRow(dict, spreadsheet_key, worksheet_id)
if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
    print "Insert row succeeded."
else:
    print "Insert row failed."
"""