# -*- coding: utf-8 -*-
"""
Created on Thu Jan 14 17:30:29 2016

@author: malkaguillot
"""

from __future__ import division


import datetime
import matplotlib.pyplot as plt
import pandas

from ipp_work.utils import from_simulation_to_data_frame_by_entity_key_plural as make_sim
from openfisca_core import periods
from openfisca_core.rates import average_rate, marginal_rate
from openfisca_france.tests import base


def parent(year, statmarit):
    return dict(
        birth = datetime.date(year - 40, 1, 1),
        statmarit = statmarit,
        )


def enfant(year):
    return dict(birth = datetime.date(year - 9, 1, 1))


def axe(name='salaire_imposable', count=2000, max=200000, min=0):
        return [
            dict(
                count = count,
                max = max,
                min = min,
                name = name,
                ),
            ]


def create_simulations(year, ind_variables, foy_variables):
    # couple
    simulation_couple = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = axe(),
        parent1 = parent(2010, 1),
        parent2 = parent(2010, 1),
        menage = dict(statut_occupation = 4),
        period = periods.period('year', year),
        ).new_simulation(debug = True, reference = True)

    # couple_enfant
    simulation_couple_enfant = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = axe(),
        parent1 = parent(2010, 1),
        parent2 = parent(2010, 1),
        enfants = [enfant(2010), enfant(2010)],
        menage = dict(statut_occupation = 4),
        period = periods.period('year', year),
        ).new_simulation(debug = True, reference = True)

    # celibataire
    simulation_celib = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = axe(),
        parent1 = parent(2010, 1),
        menage = dict(statut_occupation = 4),
        period = periods.period('year', year)
        ).new_simulation(debug = True, reference = True)

    # celibataire avec 1 enfant
    simulation_celib_enfant = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = axe(),
        parent1 = parent(2010, 1),
        enfants = [enfant(2010)],
        menage = dict(statut_occupation = 4),
        period = periods.period('year', year),
        ).new_simulation(debug = True, reference = True)

    d_couple = make_sim(simulation_couple, ind_variables=ind_variables, foy_variables = foy_variables)
    d_couple_enfant = make_sim(simulation_couple_enfant, ind_variables=ind_variables, foy_variables = foy_variables)
    d_celib = make_sim(simulation_celib, ind_variables=ind_variables, foy_variables=foy_variables)
    d_celib_enfant = make_sim(simulation_celib_enfant, ind_variables=ind_variables, foy_variables=foy_variables)

    df_by_type_menage = dict()
    df_by_type_menage['couple'] = d_couple
    df_by_type_menage['couple_enfant'] = d_couple_enfant
    df_by_type_menage['celib'] = d_celib
    df_by_type_menage['celib_enfant'] = d_celib_enfant
    return df_by_type_menage


def df_ind_by_foy_merged(df, varlist_ind_to_foy):
    ind = df['individus']
    foy = df['foyers']

    ind_by_foy = ind.groupby(['idfoy'])
    foy2 = pandas.DataFrame(
        dict([
            (var, ind_by_foy['{}'.format(var)].sum()) for var in varlist_ind_to_foy
            ])
        )
    return pandas.concat([foy, foy2], axis=1)


def df_with_tax_rate(df):
    target = df['salaire_imposable'].values + df['irpp'].values
    varying = df['salaire_imposable'].values
    df2=pandas.DataFrame({
        'marginal_rate': marginal_rate(target, varying),
        'average_rate': average_rate(target, varying)[1:],
        })

    return pandas.concat([df[1:], df2], axis = 1)


def wrap_up(year):
    ind_variables = ['salaire_imposable', 'idmen', 'quimen', 'idfoy',]
    foy_variables = ['irpp']
    df_by_type_menage = create_simulations(year, ind_variables, foy_variables)

    d_couple = df_by_type_menage['couple']
    d_couple_enfant = df_by_type_menage['couple_enfant']
    d_celib = df_by_type_menage['celib']
    d_celib_enfant = df_by_type_menage['celib_enfant']
    varlist_ind_to_foy = ['salaire_imposable']



year = 2010
wrap_up(year)
# celib #
foy = df_ind_by_foy_merged(d_celib, varlist_ind_to_foy)
foy_rate_2010 = df_with_tax_rate(foy)

year = 2005
wrap_up(year)
foy = df_ind_by_foy_merged(d_celib, varlist_ind_to_foy)
foy_rate_2005 = df_with_tax_rate(foy)

year = 2006
wrap_up(year)
foy = df_ind_by_foy_merged(d_celib, varlist_ind_to_foy)
foy_rate_2006 = df_with_tax_rate(foy)

year = 2007
wrap_up(year)
foy = df_ind_by_foy_merged(d_celib, varlist_ind_to_foy)
foy_rate_2007 = df_with_tax_rate(foy)

year = 2008
wrap_up(year)
foy = df_ind_by_foy_merged(d_celib, varlist_ind_to_foy)
foy_rate_2008 = df_with_tax_rate(foy)



## Graphe
year = 2005
foy_rate = foy_rate_2005
x = foy_rate.salaire_imposable
y = foy_rate.marginal_rate
plt.plot(x, y)
x = foy_rate.salaire_imposable
y = foy_rate.average_rate
plt.plot(x, y)
plt.title('celib {}'.format(year)) # subplot 211 title


year = 2010
foy_rate = foy_rate_2010
x = foy_rate.salaire_imposable
y = foy_rate.marginal_rate
plt.plot(x, y)
x = foy_rate.salaire_imposable
y = foy_rate.average_rate
plt.plot(x, y)
plt.title('celib {}'.format(year)) # subplot 211 title

