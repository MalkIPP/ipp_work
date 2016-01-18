# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 15:23:28 2016

@author: benjello
"""

import datetime
import pandas

from openfisca_core import periods
from openfisca_core.rates import average_rate, marginal_rate

from openfisca_france.tests import base


name = 'salaire_imposable'
count = 2000
max = 200000
min = 0

result = pandas.DataFrame()
for year in [2008, 2014]:
    simulation = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = [
            dict(
                count = count,
                max = max,
                min = min,
                name = name,
                ),
            ],
        parent1 = dict(
            birth = datetime.date(year - 40, 1, 1),
            ),
        menage = dict(statut_occupation = 4),
        period = periods.period('year', year)
        ).new_simulation(debug = True, reference = True)

    df = pandas.DataFrame(dict(
        salaire_imposable = simulation.calculate('salaire_imposable'),
        irpp = simulation.calculate('irpp')))

    target = df['salaire_imposable'].values + df['irpp'].values
    varying = df['salaire_imposable'].values
    df2 = pandas.DataFrame({
        'marginal_rate': marginal_rate(target, varying),
        'average_rate': average_rate(target, varying)[1:],
        })


    result[year] = df2.marginal_rate
