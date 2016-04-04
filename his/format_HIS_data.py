### Author: Edward Huang

#!/usr/bin/python
# -*- coding: utf-8 -*-

import xlrd

def upload_xls(filename):
    # Use cp1252 encoding protocol.
    book = xlrd.open_workbook(filename, encoding_override='cp1252')   ##To specify UTF8-encoding
    return book

if __name__ == '__main__':
    f = upload_xls('./data/HIS_spreadsheet.xls')
    # Get the first spreadsheet.
    sheet = f.sheet_by_index(0)
    # Get the first column.
    col = sheet.col_values(0)
    out = open('./data/HIS_spreadsheet.txt', 'w')
    for row in col:
        # Encode each row and write out to file.
        out.write(row.encode('utf-8') + '\n')
    out.close()