# -*- coding: utf-8 -*-
"""
Created on Wed May  6 16:49:42 2015

@author: malkaguillot
"""

import pandas
import os


path_file_input = os.path.join('/Users/malkaguillot/Documents/PhD/reductions_deductions','list_deductions_in.xlsx')

reductions_by_year = {
    '{}'.format(year): pandas.read_excel(path_file_input, sheetname = '{}'.format(year))
    for year in range(2002, 2014)
    }
concat = pandas.concat([reductions_by_year['{}'.format(year)]['reductions_{}'.format(year)]
                        for year in range(2002, 2014)
                        ])

reduction_list = sorted(concat.drop_duplicates())
reduction_df = pandas.DataFrame(reduction_list)
reduction_df = reduction_df.rename(columns = {0: 'reductions'})

reductions_by_year = {
    '{}'.format(year): pandas.merge(reduction_df, reductions_by_year['{}'.format(year)],
    left_on = 'reductions', right_on = 'reductions_{}'.format(year), how = 'outer')
    for year in range(2002, 2014)
    }

for year in range(2002, 2014):
    reductions_by_year['{}'.format(year)].set_index('reductions', inplace = True)

reductions = pandas.concat([reductions_by_year['{}'.format(year)]['reductions_{}'.format(year)]
                           for year in range(2002, 2014)],
                           axis = 1
                           ).set_index(reduction_df.reductions)
reductions.fillna('', inplace = True)

# Nombre de réduction par année:
for year in range(2002, 2014):
    reductions['reductions_{}'.format(year)][reductions['reductions_{}'.format(year)] != ''] = 1
    reductions['reductions_{}'.format(year)][reductions['reductions_{}'.format(year)] == ''] = 0

reductions.loc['total'] = [reductions['reductions_{}'.format(year)].sum()
                           for year in range(2002, 2014)
                           ]
labels = pandas.read_excel(path_file_input, sheetname = 'list')
path_file_output = os.path.join('/Users/malkaguillot/Documents/PhD/reductions_deductions','list_deductions_out.xlsx')
reductions = pandas.concat([reductions, labels], axis = 1)
reductions.to_excel(path_file_output, sheet_name = 'aggregation')

######
# Recreate input based on output
df = pandas.read_excel(path_file_output)
labels = df[['label',]]
df['list'] = df.index.copy()
for year in range(2002, 2014):
    df['reductions2_{}'.format(year)] = df['list']
    df['reductions2_{}'.format(year)][df['reductions_{}'.format(year)] == 0] = ''
    del df['reductions_{}'.format(year)]
    df.rename(columns = {'reductions2_{}'.format(year): 'reductions_{}'.format(year)}, inplace = True)
del df['list']

path_file_original_input = os.path.join('/Users/malkaguillot/Documents/PhD/reductions_deductions','list_deductions_in.xlsx')
writer = pandas.ExcelWriter(path_file_original_input)

for year in range(2002, 2014):
    df2 = pandas.DataFrame(df['reductions_{}'.format(year)])
    df2 = df2[df2['reductions_{}'.format(year)] != '']
    df2.reset_index(inplace = True)
    del df2['index']
    df2 = df2.drop(df2.index[len(df2) -1])
    df2.to_excel(writer, sheet_name = '{}'.format(year))
    del df2

labels = labels.drop(labels.index[len(labels) -1])
labels.to_excel(writer, sheet_name = 'list')

writer.save()
