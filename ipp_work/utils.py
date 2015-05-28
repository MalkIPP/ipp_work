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

    data_frame_by_entity_key_plural = dict(
        individus = pandas.DataFrame(
            dict([(name, simulation.calculate(name)) for name in
            ind_variables])
            ),
#        familles = pandas.DataFrame(
#            dict([(name, simulation.calculate_add(name)) for name in fam_variables])
#            ),
        foyers = pandas.DataFrame(
            dict([(name, simulation.calculate_add(name)) for name in foy_variables])
            ),
#        menages = pandas.DataFrame(
#            dict([(name, simulation.calculate(name)) for name in men_variables])
#            ),
        )

    return data_frame_by_entity_key_plural, simulation


if __name__ == '__main__':
    import logging
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    year = 2009
#    ind_variables = ['idmen', 'quimen', 'idfoy', 'quifoy', 'idfam', 'quifam', 'age', 'champm_individus', 'sal',
#                     'salaire_net']
    ind_variables = ['idmen', 'quimen', 'idfoy', 'sal', 'salaire_net']
    foy_variables = ['irpp']
    used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois', 'smic55']
    df_by_entity_key_plural, simulation = survey_simulate(used_as_input_variables, year, ind_variables,
                                                          foy_variables = foy_variables)
    df_individus = df_by_entity_key_plural['individus']
