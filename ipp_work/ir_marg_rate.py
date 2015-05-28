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


def from_input_df_to_entity_key_plural_df(input_data_frame, tax_benefit_system, simulation, used_as_input_variables = None):
    '''
    En entrée il faut:
        une input_data_frame
        une liste des variables nécessaires et leurs entités => il faut le tax_benefit_system
    Objectif: créer une input_data_frame_by_entity_key_plural
        Il faut ensuite créer une 2e fonction qui transforme cette df en Array
        '''
    assert input_data_frame is not None
    assert tax_benefit_system is not None

    id_variables = [
        entity.index_for_person_variable_name for entity in simulation.entity_by_key_singular.values()
        if not entity.is_persons_entity]

    role_variables = [
        entity.role_for_person_variable_name for entity in simulation.entity_by_key_singular.values()
        if not entity.is_persons_entity]

    column_by_name = tax_benefit_system.column_by_name

#        Check 1 (ici ou dans la méthode de classe ?)
    for column_name in input_data_frame:
        if column_name not in column_by_name:
            log.info('Unknown column "{}" in survey, dropped from input table'.format(column_name))
            # waiting for the new pandas version to hit Travis repo
            input_data_frame = input_data_frame.drop(column_name, axis = 1)
            # , inplace = True)  # TODO: effet de bords ?

#        Check 2 (ici ou dans la méthode de classe ?)
    for column_name in input_data_frame:
        if column_name in id_variables + role_variables:
            continue
#TODO: make that work (MG, may 15)
#        if column_by_name[column_name].formula_class.function is not None:
#            if column_name in column_by_name.used_as_input_variables:
#                log.info(
#                    'Column "{}" not dropped because present in used_as_input_variabels'.format(column_name))
#                continue
#
#            log.info('Column "{}" in survey set to be calculated, dropped from input table'.format(column_name))
#            input_data_frame = input_data_frame.drop(column_name, axis = 1)
            # , inplace = True)  # TODO: effet de bords ?

#   Work on entities
    for entity in simulation.entity_by_key_singular.values():
        if entity.is_persons_entity:
            entity.count = entity.step_size = len(input_data_frame)
        else:
            entity.count = entity.step_size = (input_data_frame[entity.role_for_person_variable_name] == 0).sum()
            entity.roles_count = input_data_frame[entity.role_for_person_variable_name].max() + 1

#   Classify column by entity:
    columns_by_entity = {}
    columns_by_entity['individu'] = []
    columns_by_entity['quifam'] = []
    columns_by_entity['quifoy'] = []
    columns_by_entity['quimen'] = []
    for column_name, column_serie in input_data_frame.iteritems():
        holder = simulation.get_or_new_holder(column_name)
        entity = holder.entity
        if entity.is_persons_entity:
            columns_by_entity['individu'].append(column_name)
        else:
            columns_by_entity[entity.role_for_person_variable_name].append(column_name)

    input_data_frame_by_entity_key_plural = {}
    for entity in simulation.entity_by_key_singular.values():
        if entity.is_persons_entity:
            input_data_frame_by_entity_key_plural['individus'] = \
                input_data_frame[columns_by_entity['individu']]
            entity.count = entity.step_size = len(input_data_frame)
        else:
            input_data_frame_by_entity_key_plural[entity.index_for_person_variable_name] = \
                input_data_frame[columns_by_entity[entity.role_for_person_variable_name]][input_data_frame[entity.role_for_person_variable_name] == 0]
    return input_data_frame_by_entity_key_plural

def test_survey_simulation(increment = 10, target = 'irpp', varying = 'rni'):
    increment = 10
    target = 'irpp'
    varying = 'rni'
    year = 2009
    TaxBenefitSystem = openfisca_france_data.init_country()
    tax_benefit_system = TaxBenefitSystem()

    input_data_frame = get_input_data_frame(year)
#    Simulation 1 : get varying and target
    survey_scenario = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois', 'smic55'],
        year = year,
        tax_benefit_system = tax_benefit_system
        )
    simulation = survey_scenario.new_simulation(debug = False)

    output_data_frame = pandas.DataFrame(
       dict([(name, simulation.calculate_add(name)) for name in [
           target, varying, 'idfoy_original'
           ]]))

#    Make input_data_frame_by_entity_key_plural from the previous input_data_frame and simulation
    input_data_frame_by_entity_key_plural = \
        from_input_df_to_entity_key_plural_df(input_data_frame, tax_benefit_system, simulation)
    foyers = input_data_frame_by_entity_key_plural['idfoy']
    foyers = pandas.merge(foyers, output_data_frame, on = 'idfoy_original')

#    Incrementation of varying:
    foyers[varying] = foyers[varying] + increment

#    On remplace la nouvelle base dans le dictionnaire
    input_data_frame_by_entity_key_plural['idfoy'] = foyers

#   2e simulation à partir de input_data_frame_by_entity_key_plural:
#   TODO: fix used_as_input_variabels in the from_input_df_to_entity_key_plural_df() function
    used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois', 'smic55', varying],

#    survey_scenario = SurveyScenario().init_from_data_frames(
#        input_data_frames = input_data_frame_by_entity_key_plural,
#        used_as_input_variables = used_as_input_variables,
#        year = year,
#        tax_benefit_system = tax_benefit_system
#        )
#    simulation = survey_scenario.new_simulation(debug = False)

#    output_data_frame2 = pandas.DataFrame(
#       dict([(name, simulation.calculate_add(name)) for name in [
#           target, varying, 'idfoy_original'
#           ]]))


if __name__ == '__main__':
    import logging
    import time
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    start = time.time()
