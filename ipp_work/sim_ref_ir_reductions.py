# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014, 2015 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import pandas
import matplotlib.pyplot as plt


from ipp_work.reforms import ir_reduc
from ipp_work.utils import df_weighted_average_grouped, reform_survey_simulation


if __name__ == '__main__':
    import logging
    import time
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    start = time.time()

    year = 2009
    reform = ir_reduc
    ind_variables = ['idmen', 'quimen', 'idfoy', 'salaire_imposable', 'salaire_net']
    fam_variables = None
    foy_variables = ['rfr', 'irpp', 'rbg', 'iaidrdi', 'rng', 'ip_net', 'reductions']
    men_variables = None
    reform_specific_foy_variables = ['decile_rfr', 'weight_foyers']
    used_as_input_variables = ['salaire_imposable', 'cho', 'rst', 'age_en_mois', 'smic55']
    reform_data_frame_by_entity_key_plural, reference_data_frame_by_entity_key_plural \
        = reform_survey_simulation(reform, year, ind_variables, fam_variables, foy_variables, men_variables,
                                   used_as_input_variables, reform_specific_foy_variables)

    reform = reform_data_frame_by_entity_key_plural['foyers']
    reference = reference_data_frame_by_entity_key_plural['foyers']
    simulation = reference_data_frame_by_entity_key_plural['foyers']
    for col in reform.columns.drop(['decile_rfr', 'weight_foyers']):
        reform = reform.rename(columns={'{}'.format(col): 'reform_{}'.format(col)})
    for col in reference.columns:
        reference = reference.rename(columns={'{}'.format(col): 'reference_{}'.format(col)})
    df = pandas.concat([reference, reform], axis = 1)
    df['diff_irpp'] = df.reference_irpp - df.reform_irpp
    df['diff_ip_net'] = df.reference_ip_net - df.reform_ip_net
    Wconcat = df_weighted_average_grouped(
        dataframe = df,
        groupe = 'decile_rfr',
        varlist = [
            'diff_irpp', 'diff_ip_net', 'reform_ip_net', 'reference_ip_net', 'reference_reductions', 'reference_rfr'
            ],
        )
    Wconcat['tx_irpp'] = Wconcat['diff_irpp'] / Wconcat['reference_rfr']
    Wconcat['tx_ip'] = Wconcat['reform_ip_net'] / Wconcat['reference_rfr']
    Wconcat['tx_d_ip_net'] = Wconcat['diff_ip_net'] / Wconcat['reference_rfr']
    Wconcat['tx_reductions'] = Wconcat['reference_reductions'] / Wconcat['reference_rfr']
    df_to_plot = Wconcat[['tx_ip', 'tx_reductions']]
    df_to_plot = Wconcat[['reform_ip_net', 'reference_reductions']]

    # Plot du graphe avec matplotlib
    plt.figure()
    df_to_plot.plot(kind = 'bar', stacked = True)
    plt.axhline(0, color = 'k')

    (df.reference_reductions*df.weight_foyers).sum()
#       2 837 273 843
    (df.reference_irpp * df.weight_foyers).sum()
#    - 48 725 131 459
    (df.reform_irpp * df.weight_foyers).sum()
#    - 51 562 300 405
    (df.reference_irpp * df.weight_foyers).sum() - (df.reform_irpp * df.weight_foyers).sum()
#    2 745 569 678

