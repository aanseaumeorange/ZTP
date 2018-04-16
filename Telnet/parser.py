import xlrd

wb = xlrd.open_workbook('ztp.xlsx')
ws = wb.sheet_by_index(0)
ztp = []

num_rows = ws.nrows
num_cols = ws.ncols

# Strore constructor
constructor = ws.cell(1, 1).value

# Store data in a list
nb_switch = 0
for row_index in range(7, num_rows):
    nb_switch = nb_switch + 1
    sn = ws.cell(row_index, 0).value
    cfg = ws.cell(row_index, 1).value
    iso = ws.cell(row_index, 2).value
    ztp.append((sn, cfg, iso))
