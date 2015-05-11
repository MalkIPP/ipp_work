# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 16:16:40 2015

@author: malkaguillot
"""
import os

import pandas as pd
from pandas import read_excel

directory_path = '/Users/malkaguillot/Dropbox/IPP/Mannheim_chapter_FR/'
rpo_path = os.path.join(directory_path, "analyse_RPO_long.xlsx")
rpo_df = read_excel(rpo_path, sheetname = "alpha_order")


print rpo_df.columns
menage_rpo_df= rpo_df[rpo_df.menage == 1]
menage_rpo_df= menage_rpo_df[['source','id','id_mesure','an2009','an2010','an2011','an2012','an2013','an2014']]
menage_rpo_df['date_source']=menage_rpo_df['source'].apply(lambda x: x[3:])

mesure62_rpo_df= menage_rpo_df[menage_rpo_df.id_mesure == 62]
mesure62_rpo_df = mesure62_rpo_df.fillna(0)

mesure62_rpo_df['an2009_prev'] = mesure62_rpo_df['an2009'] 
print mesure62_rpo_df[mesure62_rpo_df.date_source == '2011']['an2011'] 
a mesure62_rpo_df[mesure62_rpo_df.date_source == '2011']['an{}'.format(2011)] 

mesure62_rpo_df.loc[168]= mesure62_rpo_df.loc[167]

print mesure62_rpo_df
print mesure62_rpo_df.loc[167]['an2009']

def choose_right_information_from_RPO(groupe, an=2011):
    
    return

grouped_by_mesure = menage_rpo_df.groupby(['id_mesure'])
grouped_by_mesure2 = grouped_by_mesure.apply(lambda x: choose_right_information_from_RPO(groupe = x, an = 2011))
