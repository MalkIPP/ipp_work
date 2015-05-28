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
from ipp_work import df_weighted_average_grouped

def df_survey_simulation(reductions):
    year = 2009
    TaxBenefitSystem = openfisca_france_data.init_country()
    tax_benefit_system = TaxBenefitSystem()
    input_data_frame = get_input_data_frame(year)


    survey_scenario_reference = SurveyScenario().init_from_data_frame(
        input_data_frame = input_data_frame,
        used_as_input_variables = ['sal', 'cho', 'rst', 'age_en_mois', 'smic55'],
        year = year,
        tax_benefit_system = tax_benefit_system
        )

    simulation = survey_scenario_reference.new_simulation()

    from openfisca_core import periods
    period = periods.period('year', 2007)
    period = period.start.offset('first-of', 'month').period('year')
    bareme = simulation.legislation_at(period.start).ir.bareme

    data_frame_by_entity_key_plural = dict(
        foyers = pandas.DataFrame(
            dict([(name, simulation.calculate_add(name)) for name in [
                'rfr',
                'irpp',
                'rbg',
                'iaidrdi',
                'rng',
                'ip_net',
                'reductions',
                'decile_rfr',
                'weight_foyers',
                ] + reductions
                ])
            ),
        )
    return data_frame_by_entity_key_plural


if __name__ == '__main__':
    import logging
    import time
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    start = time.time()
    reductions_2009 = ['adhcga',
                      'cappme',
                      'cotsyn',
                      'creaen',
                      'daepad',
                      'deffor',
                      'dfppce',
                      'doment',
                      'domlog',
                      'domsoc',
                      'donapd',
                      'ecodev',
                      'ecpess',
                      'intagr',
                      'invfor',
                      'invlst',
                      'locmeu',
                      'mohist',
                      'prcomp',
                      'repsoc',
                      'resimm',
                      'rsceha',
                      'saldom',
                      'scelli',
                      'sofica',
                      'sofipe',
                      'spfcpi'
                       ]

    data_frame_by_entity_key_plural = df_survey_simulation(reductions = reductions_2009)

    df = data_frame_by_entity_key_plural['foyers']

#
    Wconcat = df_weighted_average_grouped(
        dataframe = df,
        groupe = 'decile_rfr',
#        varlist = ['irpp', 'ip_net','rfr'] + reductions_2009
        varlist = ['ip_net'] + reductions_2009
        )
    df_to_plot = Wconcat
    for reduction in reductions_2009:
        df_to_plot[reduction] = df_to_plot[reduction] /df_to_plot['ip_net']
    del df_to_plot['ip_net']
    for col in df_to_plot.columns:
        if df_to_plot[:1][col].item() == 0:
            del df_to_plot[col]

    # Labelling
    import os
    path_file_input = os.path.join('/Users/malkaguillot/Documents/PhD/reductions_deductions', 'list_deductions_in.xlsx')
    labels = pandas.read_excel(path_file_input, sheetname = 'list')
    del labels['label']
    labels = labels[labels.index.isin(df_to_plot.columns)]
    label_dict = labels['short_names'].to_dict()
    label_dict.keys()
    for col in df_to_plot.columns:
        df_to_plot.rename(columns = {col : label_dict[col]}, inplace = True)
    # Plot du graphe avec matplotlib
    plt.figure()
    df_to_plot.plot(kind = 'bar', stacked = True)
    plt.axhline(0, color = 'k')

