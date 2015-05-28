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


def test_survey_simulation(increment = 10, target = 'irpp', varying = 'rni'):
    increment = 10
    target = 'irpp'
    varying = 'rni'
    year = 2009
    TaxBenefitSystem = openfisca_france_data.init_country()
    tax_benefit_system = TaxBenefitSystem()

    column_by_name = tax_benefit_system.column_by_name
    column_by_name['sal'].formula_class.function

    input_data_frame = get_input_data_frame(year)
    survey_scenario = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois', 'smic55'],
        year = year,
        tax_benefit_system = tax_benefit_system
        )
    input_data_frame_by_entity_key_plural = survey_scenario.from_input_df_to_entity_key_plural_df()

    simulation = survey_scenario.new_simulation(debug = False)
    simulation_data_frame_by_entity_key_plural = dict(
        foyers = pandas.DataFrame(
            dict([(name, simulation.calculate_add(name)) for name in [
                target, varying
                ]])
            ),
        )
    simulation_data_frame_by_entity_key_plural['foyers'][varying] = \
        simulation_data_frame_by_entity_key_plural['foyers'][varying] + increment
        varying = simulation_data_frame_by_entity_key_plural['foyers'][varying]
    input_data_frame_incremented = input_data_frame

    return simulation_data_frame_by_entity_key_plural

ind_vars = ['index', 'idfam', 'idfoy', 'idmen', 'quifam', 'quifoy', 'quimen', 'sal', 'noi', 'age_en_mois']
fam_vars = ['idfam',]
foy_vars = ['idfoy','f7ce']
men_vars = ['idmen',]
individus = input_data_frame[ind_vars]
familles = input_data_frame[fam_vars][input_data_frame.quifam == 0]
foyers = input_data_frame[foy_vars][input_data_frame.quifoy == 0]
menages = input_data_frame[men_vars][input_data_frame.quimen == 0]

input_data_frame_by_entity_key_plural={}
input_data_frame_by_entity_key_plural['individus'] = individus
input_data_frame_by_entity_key_plural['familles'] = familles
input_data_frame_by_entity_key_plural['foyers'] = foyers
input_data_frame_by_entity_key_plural['menages'] = menages

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
    simulation = reference_data_frame_by_entity_key_plural['foyers']
#    simulation = reference_data_frame_by_entity_key_plural['foyers']

    for col in ['irpp', 'rng', 'rni']:
        reform = reform.rename(columns={'{}'.format(col): '{}_ref'.format(col)})
        simulation = simulation.rename(columns={'{}'.format(col): '{}_sim'.format(col)})

    df_compar = simulation[['irpp_sim', 'rng_sim', 'rni_sim']].merge(reform[['irpp_ref', 'rng_ref', 'rni_ref']], left_index=True, right_index=True)
