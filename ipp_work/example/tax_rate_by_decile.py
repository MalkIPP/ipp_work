# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 17:07:33 2015

@author: malkaguillot
"""

from ipp_work.utils import survey_simulate, df_weighted_average_grouped
from ipp_work.simulations.ir_marg_rate import varying_survey_simulation
from ipp_work.example.quantiles_of_revimp import make_weighted_deciles_of_variable
import pandas

year = 2009
ind_variables = ['idmen', 'quimen', 'idfoy', 'salaire_imposable', 'salaire_net']
foy_variables = ['irpp', 'decile_rfr', 'weight_foyers', 'idfoy_original', 'rfr']
used_as_input_variables = ['salaire_imposable', 'cho', 'rst', 'age_en_mois', 'smic55']
df_by_entity_key_plural, simulation = survey_simulate(used_as_input_variables, year, ind_variables,
                                                      foy_variables = foy_variables)
df_individus = df_by_entity_key_plural['individus']
df_foyers = df_by_entity_key_plural['foyers']


tax_rates = varying_survey_simulation(year = 2009, increment = 10, target = 'irpp', varying = 'rni',
                                   used_as_input_variables = used_as_input_variables)
tax_rates = tax_rates[['idfoy_original', 'marginal_rate', 'average_rate']]
df_foyers = pandas.merge(df_foyers, tax_rates, on = 'idfoy_original')

make_weighted_deciles_of_variable(df_foyers, 'rfr', 'weight_foyers', 100)


Wconcat = df_weighted_average_grouped(
    dataframe = df_foyers,
    groupe = 'decile_of_rfr',
    varlist = [
        'marginal_rate', 'average_rate'
        ],
    )
print Wconcat
df_foyers['decile_rfr'].count()
df_foyers['rfr'].describe()
df_foyers['weight_foyers'].describe()