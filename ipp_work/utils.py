# -*- coding: utf-8 -*-
"""
Created on Tue May  5 11:54:08 2015

@author: malkaguillot
"""

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

import openfisca_france_data
from openfisca_france_data.input_data_builders import get_input_data_frame
from openfisca_france_data.surveys import SurveyScenario


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


def from_simulation_to_data_frame_by_entity_key_plural(simulation, ind_variables = None, fam_variables = None,
                                                       foy_variables = None, men_variables = None):
    '''
    '''
    data_frame_by_entity_key_plural = dict()
    if ind_variables is not None:
        data_frame_by_entity_key_plural['individus'] = pandas.DataFrame(
            dict([(name, simulation.calculate(name)) for name in ind_variables])
            )
    if fam_variables is not None:
        data_frame_by_entity_key_plural['familles'] = pandas.DataFrame(
            dict([(name, simulation.calculate(name)) for name in fam_variables])
            )
    if foy_variables is not None:
        data_frame_by_entity_key_plural['foyers'] = pandas.DataFrame(
            dict([(name, simulation.calculate(name)) for name in foy_variables])
            )
    if men_variables is not None:
        data_frame_by_entity_key_plural['menages'] = pandas.DataFrame(
            dict([(name, simulation.calculate(name)) for name in men_variables])
            )
    return data_frame_by_entity_key_plural


def survey_simulate(used_as_input_variables, year, ind_variables = None, fam_variables = None, foy_variables = None,
                    men_variables = None):
    year = year
    input_data_frame = get_input_data_frame(year)
    survey_scenario = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        used_as_input_variables = used_as_input_variables,
        year = year,
        )
    simulation = survey_scenario.new_simulation()

    data_frame_by_entity_key_plural = from_simulation_to_data_frame_by_entity_key_plural(
        simulation, ind_variables, fam_variables, foy_variables, men_variables)

    return data_frame_by_entity_key_plural, simulation


def reform_survey_simulation(reform = None, year = None, ind_variables = None, fam_variables = None,
                             foy_variables = None, men_variables = None, used_as_input_variables = None,
                             reform_specific_foy_variables = None):
    assert reform is not None
    assert year is not None

    TaxBenefitSystem = openfisca_france_data.init_country()
    tax_benefit_system = TaxBenefitSystem()
    reform = reform.build_reform(tax_benefit_system)
    input_data_frame = get_input_data_frame(year)
    survey_scenario_reform = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        used_as_input_variables = used_as_input_variables,
        year = year,
        tax_benefit_system = reform
        )

    reference_simulation = survey_scenario_reform.new_simulation(debug = False, reference = True)

    reference_data_frame_by_entity_key_plural = from_simulation_to_data_frame_by_entity_key_plural(
        reference_simulation, ind_variables, fam_variables, foy_variables, men_variables)

    reform_simulation = survey_scenario_reform.new_simulation(debug = False)

    reform_data_frame_by_entity_key_plural = from_simulation_to_data_frame_by_entity_key_plural(
        reform_simulation, ind_variables, fam_variables, foy_variables + reform_specific_foy_variables, men_variables)

    return reform_data_frame_by_entity_key_plural, reference_data_frame_by_entity_key_plural


if __name__ == '__main__':
    import logging
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    year = 2009
#    ind_variables = ['idmen', 'quimen', 'idfoy', 'quifoy', 'idfam', 'quifam', 'age', 'champm_individus', 'sal',
#                     'salaire_net']
    ind_variables = ['idmen', 'quimen', 'idfoy', 'salaire_imposable', 'salaire_net']
    foy_variables = ['irpp']
    used_as_input_variables = ['salaire_imposable', 'cho', 'rst', 'age_en_mois', 'smic55']
    df_by_entity_key_plural, simulation = survey_simulate(used_as_input_variables, year, ind_variables,
                                                          foy_variables = foy_variables)
    df_individus = df_by_entity_key_plural['individus']

    data_frame_by_entity_key_plural = from_simulation_to_data_frame_by_entity_key_plural(
        simulation = simulation, ind_variables = ind_variables, foy_variables = foy_variables)
