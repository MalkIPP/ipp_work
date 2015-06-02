# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 16:03:27 2015

@author: malkaguillot
"""
from __future__ import division

import pandas
import numpy as np
from openfisca_france_data.input_data_builders import get_input_data_frame
from ipp_work.compute_quantiles import quantile
from ipp_work.utils import survey_simulate
from math import log10, ceil


def make_weighted_deciles_of_variable(df, variable, weight, number_of_quantile):
    nb_decimal = int(ceil(log10(number_of_quantile)))
    qs = np.arange(0, 1, 1 / number_of_quantile).round(nb_decimal).tolist()
    qs.remove(0)
    df['decile_of_{}'.format(variable)] = 0
    for q in qs:
        p = int(q * number_of_quantile)
        df['p{}'.format(p)] = quantile(df[variable], df[weight], q)
        df['is{}'.format(p)] = (df[variable] < df['p{}'.format(p)])
        df['decile_of_{}'.format(variable)] = df['decile_of_{}'.format(variable)] + df['is{}'.format(p)].astype('int')
        del df['is{}'.format(p)], df['p{}'.format(p)]
    df['decile_of_{}'.format(variable)] = number_of_quantile - df['decile_of_{}'.format(variable)]
    return


if __name__ == '__main__':
    import logging
    import time
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    start = time.time()

    year = 2009
    input_data_frame = get_input_data_frame(year)
    revimp = input_data_frame[['revimp', 'salaire_imposable', 'quifoy', 'idfoy_original']][input_data_frame.quifoy == 0]
    revimp.revimp[np.isnan(revimp.revimp)] = 0

    ind_variables = ['idmen', 'quimen', 'idfoy', 'salaire_imposable', 'salaire_net']
    foy_variables = ['irpp', 'decile_rfr', 'decile_rni', 'weight_foyers', 'idfoy_original', 'rfr']
    used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois', 'smic55']
    df_by_entity_key_plural, simulation = survey_simulate(used_as_input_variables, year, ind_variables,
                                                          foy_variables = foy_variables)
    df_foyers = df_by_entity_key_plural['foyers'][['weight_foyers', 'idfoy_original', 'rfr']]
    df = pandas.merge(df_foyers, revimp, on = 'idfoy_original')

    weight = 'weight_foyers'
    number_of_quantile = 10
    make_weighted_deciles_of_variable(df, 'revimp', weight, number_of_quantile)
    make_weighted_deciles_of_variable(df, 'rfr', weight, number_of_quantile)
