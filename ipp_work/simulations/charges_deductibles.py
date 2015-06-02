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
from ipp_work.utils import survey_simulate


def test_weights_building():
    year = 2009
    input_data_frame = get_input_data_frame(year)
    survey_scenario = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois'],
        year = year,
        )
    survey_scenario.new_simulation()
    return survey_scenario.simulation

if __name__ == '__main__':
    import logging
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)

    year = 2009
    ind_variables = ['idmen', 'quimen', 'idfoy', 'quifoy', 'idfam', 'quifam', 'age', 'champm_individus',
                     'salaire_imposable', 'salaire_net', 'txtppb']
    foy_variables = ['irpp', 'cd_grorep', 'cd_pension_alimentaire', 'cd_acc75a', 'cd_deddiv', 'cd_eparet', 'rfr',
                     'decile_rfr', 'weight_foyers', 'idfoy_original']
    used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois', 'smic55']
    data_frame_by_entity_key_plural, simulation = survey_simulate(used_as_input_variables, year, ind_variables,
                                                          foy_variables = foy_variables)

    data_frame_individus = data_frame_by_entity_key_plural['individus']
    data_frame_foyers = data_frame_by_entity_key_plural['foyers']
#    (data_frame_familles.weight_familles * data_frame_familles.af).sum() / 1e9 > 10

    import numpy
    pension_alim_not_null = data_frame_foyers.cd_pension_alimentaire[data_frame_foyers.cd_pension_alimentaire != 0]
    print data_frame_foyers.cd_pension_alimentaire.describe()
    print pension_alim_not_null.describe()

    epargne_retraite_not_null = data_frame_foyers.cd_eparet[data_frame_foyers.cd_eparet != 0]
    print data_frame_foyers.cd_eparet.describe()
    print epargne_retraite_not_null.describe()

    import matplotlib
    matplotlib.pyplot.hist(numpy.histogram(pension_alim_not_null))

    import matplotlib.pyplot as plt

    cd_pension_alimentaire2 = data_frame_foyers[
        data_frame_foyers.cd_pension_alimentaire < 6000] \
        .cd_pension_alimentaire.values
    # the histogram of the data
    n, bins, patches = plt.hist(cd_pension_alimentaire2[cd_pension_alimentaire2 >0], 20)

