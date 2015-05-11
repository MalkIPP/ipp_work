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


import openfisca_france_data
from openfisca_france_data.input_data_builders import get_input_data_frame
from openfisca_france_data.surveys import SurveyScenario
from openfisca_france.reforms import ir_reduc


def wavg(groupe, var):
    '''
    Fonction qui calcule la moyenne pondérée par groupe d'une variable
    '''
    d = groupe[var]
    w = groupe['weight_foyers']
    return (d * w).sum() / w.sum()


def collapse(dataframe, groupe, var):
    '''
    Pour une variable, fonction qui calcule la moyenne pondérée au sein de chaque groupe.
    '''
    grouped = dataframe.groupby([groupe])
    var_weighted_grouped = grouped.apply(lambda x: wavg(groupe = x, var = var))
    return var_weighted_grouped


def df_weighted_average_grouped(dataframe, groupe, varlist):
    '''
    Agrège les résultats de weighted_average_grouped() en une unique dataframe pour la liste de variable 'varlist'.
    '''
    return pandas.DataFrame(
        dict([
            (var, collapse(dataframe, groupe, var)) for var in varlist
            ])
        )

def test_survey_simulation():
    year = 2009
    TaxBenefitSystem = openfisca_france_data.init_country()
    tax_benefit_system = TaxBenefitSystem()
    reform = ir_reduc.build_reform(tax_benefit_system)
    input_data_frame = get_input_data_frame(year)
    survey_scenario_reform = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois', 'smic55'],
        year = year,
        tax_benefit_system = reform
        )

    reform_simulation = survey_scenario_reform.new_simulation(debug = False)
    reform_data_frame_by_entity_key_plural = dict(
        foyers = pandas.DataFrame(
            dict([(name, reform_simulation.calculate_add(name)) for name in [
                'rfr',
                'irpp',
                'rbg',
                'iaidrdi',
                'rng',
                'ip_net',
                'reductions',
                ]])
            ),
        )

    survey_scenario_reference = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois', 'smic55'],
        year = year,
        tax_benefit_system = tax_benefit_system
        )

    reference_simulation = survey_scenario_reference.new_simulation(debug = False, reference = True)
    reference_data_frame_by_entity_key_plural = dict(
        foyers = pandas.DataFrame(
            dict([(name, reference_simulation.calculate_add(name)) for name in [
                'rfr',
                'irpp',
                'rbg',
                'iaidrdi',
                'rng',
                'ip_net',
                'reductions',
                'decile_rfr',
                'weight_foyers',
                ]])
            ),
        )

    return reform_data_frame_by_entity_key_plural, reference_data_frame_by_entity_key_plural


if __name__ == '__main__':
    import logging
    import time
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    start = time.time()

    reform_data_frame_by_entity_key_plural, reference_data_frame_by_entity_key_plural \
        = test_survey_simulation()

    reform = reform_data_frame_by_entity_key_plural['foyers']
    reference = reference_data_frame_by_entity_key_plural['foyers']
    simulation = reference_data_frame_by_entity_key_plural['foyers']
    for col in reform.columns:
        reform = reform.rename(columns={'{}'.format(col): 'reform_{}'.format(col)})
    columns = reference.columns.drop(['decile_rfr', 'weight_foyers'])
    for col in columns:
        reference = reference.rename(columns={'{}'.format(col): 'reference_{}'.format(col)})
    df = pandas.concat([reference, reform], axis = 1)
    df['diff_irpp'] = df.reference_irpp - df.reform_irpp
    df['diff_ip_net'] = df.reference_ip_net - df.reform_ip_net
    Wconcat = df_weighted_average_grouped(
        dataframe = df,
        groupe = 'decile_rfr',
        varlist = ['diff_irpp', 'diff_ip_net', 'reform_ip_net', 'reference_ip_net', 'reference_reductions', 'reference_rfr']
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

#    (simulation.reductions*simulation.weight_foyers).sum()
#       2 837 273 843
    (simulation.irpp*simulation.weight_foyers).sum()
#    - 48 725 131 459
    (reform.reform_irpp*simulation.weight_foyers).sum()
#    - 51 562 300 405
    (simulation.irpp*simulation.weight_foyers).sum() - (reform.reform_irpp*simulation.weight_foyers).sum()
#    2 837 168 946

