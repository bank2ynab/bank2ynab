#!/usr/bin/env python3

# we know it should have headers, but we respect the setting
file_path = "/home/torben/Desktop/kta_ei.dat"
header_rows = 1
delim = "|"

with open(file_path,'r') as input_file:
    output_rows = []
    rownum = 0
    for row in input_file:
        rownum += 1
        new_row = []
        cells = row.split(delim) # define delimiter
        cellnum = 0
        for cell in cells:
            cellnum += 1
            # convert amount (field 4) and just copy any other field:
            # careful not to parse cell 4 that does not exist in row 1:
            if rownum > header_rows and cell == cells[4]:
                ats = cells[4] # read ATS amount
                eur = round(float(ats) / 13.760300331,2) # convert to EUR
                new_row.append(eur)
            else:
                new_row.append(cell.strip())
        # if our row isn't empty, add it to the list of rows
        if new_row:
            output_rows.append(new_row)
        print(new_row)
        if rownum == 3: break # premature exit for comfortable debugging
    #print(str(output_rows))
with open(file_path+'2', 'w') as output_file:
    for row in output_rows:
        output_file.write("{}\n".format("".join(str(row))))
