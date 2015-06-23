# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 17:47:15 2015

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
import numpy
import os
import matplotlib.pyplot as plt

from ipp_work.utils import df_weighted_average_grouped, survey_simulate
from ipp_work.example.quantiles_of_revimp import make_weighted_deciles_of_variable
from openfisca_france_data.input_data_builders import get_input_data_frame

path = '/Users/malkaguillot/Documents/PhD/reductions_deductions'

if __name__ == '__main__':
    import logging
    import time
    log = logging.getLogger(__name__)
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    start = time.time()
    year = 2009

    def group_by(dataframe, groupe, var):
        grouped = dataframe.groupby([groupe])
        var_grouped = grouped.apply(lambda x: (x[var]).sum())
        return var_grouped

    reductions_2009 = ['cotsyn']
    foy_variables = ['rfr', 'irpp', 'rbg', 'iaidrdi', 'rng', 'ip_net', 'reductions', 'decile_rfr', 'weight_foyers',
                     'f7gq']
    ind_variables = ['f7ac', 'quifoy', 'idfoy', 'weight_individus']
    used_as_input_variables = ['salaire_imposable', 'cho', 'rst', 'age_en_mois', 'smic55']
    data_frame_by_entity_key_plural, simulation = survey_simulate(used_as_input_variables = used_as_input_variables,
        year = year, foy_variables = foy_variables + reductions_2009, ind_variables = ind_variables)

    df = data_frame_by_entity_key_plural['foyers']
    dfi = data_frame_by_entity_key_plural['individus']
    grouped_dfi_by_idfoy = dfi.groupby(['idfoy'])

    number_of_quantile = 10
    make_weighted_deciles_of_variable(df, 'rfr', 'weight_foyers', number_of_quantile)

    dfi_f7ac_nonnul = dfi[dfi.f7ac != 0]

#    f7ac_summed_by_foy = grouped['f7ac'].agg([np.sum, np.mean, np.std, ])
    f7ac_summed_by_foy = pandas.DataFrame()
    f7ac_summed_by_foy['f7ac'] = grouped_dfi_by_idfoy['f7ac'].agg([numpy.sum])
    f7ac_summed_by_foy['idfoy'] = grouped_dfi_by_idfoy['idfoy'].agg([numpy.min])
    f7ac_summed_by_foy.set_index(f7ac_summed_by_foy.idfoy, inplace = True)

    merged = df.merge(f7ac_summed_by_foy, right_index = True, left_index = True)
    cotsyn_foy = merged[['f7ac', 'cotsyn', 'idfoy', 'weight_foyers', 'rfr', 'decile_of_rfr']]
    cotsyn_foy['cotsyn_decl_w'] = (cotsyn_foy['cotsyn'] > 0) * cotsyn_foy.weight_foyers
    cotsyn_foy['f7ac_decl_w'] = (cotsyn_foy['f7ac'] > 0) * cotsyn_foy.weight_foyers
    cotsyn_foy_decl = cotsyn_foy[cotsyn_foy.f7ac != 0]

    to_merge = cotsyn_foy[['rfr', 'idfoy', 'decile_of_rfr', 'cotsyn']]
    cotsyn_ind = dfi.merge(to_merge, on = 'idfoy')
    cotsyn_ind['f7ac_decl_w'] = (cotsyn_ind['f7ac'] > 0) * cotsyn_ind.weight_individus
    cotsyn_ind['f7ac_decl'] = (cotsyn_ind['f7ac'] > 0)
    cotsyn_ind_decl = cotsyn_ind[cotsyn_ind.f7ac != 0]

    del df, dfi, dfi_f7ac_nonnul, f7ac_summed_by_foy, merged, to_merge

    (cotsyn_ind.f7ac > 0).sum()  # 3017 individus de la base
    (cotsyn_foy > 0).sum()  # 2801 foyers tq f7ac > 0 mais 2796 tq cotsyn > 0

    nb_ind = ((cotsyn_ind.f7ac > 0) * cotsyn_ind['weight_individus']).sum()  # 1 591 370 individus
    total_ind = (cotsyn_ind.f7ac * cotsyn_ind.weight_individus).sum()  # 214 997 803 euros

    nb_foy = ((cotsyn_foy.f7ac > 0) * cotsyn_foy['weight_foyers']).sum()  # 1 486 072 foyers
    total_foy = (cotsyn_foy.f7ac * cotsyn_foy.weight_foyers).sum()  # 214 997 803 euros

    # Moyenne (pondérée) parmis la population des déclarants
    (cotsyn_ind_decl.f7ac * cotsyn_ind_decl.weight_individus).sum() / \
        cotsyn_ind_decl.weight_individus.sum()  # 135 euros

    (cotsyn_foy_decl.f7ac * cotsyn_foy_decl.weight_foyers).sum() / \
        cotsyn_foy_decl.weight_foyers.sum()  # 144 euros
    (cotsyn_foy_decl.cotsyn * cotsyn_foy_decl.weight_foyers).sum() / \
        cotsyn_foy_decl.weight_foyers.sum()  # 94  euros

    # Histogram
    sortie_graph = os.path.join(path, 'cotsyn-hist.png')
    cases = plt.hist(cotsyn_ind.f7ac, 50, range = (1, 500), color='green', alpha=0.8)
    reduction = plt.hist(cotsyn_foy.cotsyn, 50, range = (1, 500), color='blue', alpha=0.8)
    plt.legend((u"Montant de cotisation déclaré", u"Montant déduit à l\'IR"))
    plt.savefig(sortie_graph)

    # Aggrégation par décile
    grouped_cotsyn_foy_by_dec = cotsyn_foy.groupby(['decile_of_rfr'])
#    f7ac_summed_by_foy = grouped['f7ac'].agg([np.sum, np.mean, np.std, ])
    foy_by_decile = pandas.DataFrame()
    foy_by_decile = grouped_cotsyn_foy_by_dec.agg([numpy.sum, numpy.mean])
#    decl_by_decile['decl_f7ac'] = grouped.agg({'decl_f7ac' : lambda x: x.sum()})
#    decl_by_decile['decl_cotsyn'] = grouped.agg({'decl_cotsyn' : lambda x: x.sum()})
    del foy_by_decile['idfoy'], foy_by_decile['weight_foyers']
    # Vérification:
    print foy_by_decile.sum()
    print ((cotsyn_foy.f7ac > 0) * cotsyn_foy['weight_foyers']).sum()

    grouped_cotsyn_ind_by_dec = cotsyn_ind.groupby(['decile_of_rfr'])
    ind_by_decile = pandas.DataFrame()
    ind_by_decile = grouped_cotsyn_ind_by_dec.agg([numpy.sum, numpy.mean])

    del grouped_cotsyn_foy_by_dec, grouped_cotsyn_ind_by_dec

    grouped_cotsyn_foy_by_dec_decl = cotsyn_foy_decl.groupby(['decile_of_rfr'])
    foy_by_decile_decl = pandas.DataFrame()
    foy_by_decile_decl = grouped_cotsyn_foy_by_dec_decl.agg([numpy.sum, numpy.mean])
    del foy_by_decile_decl['idfoy'], foy_by_decile_decl['weight_foyers'], grouped_cotsyn_foy_by_dec_decl

    print foy_by_decile_decl.sum()
#    foy_by_decile_decl['taux_eff', 'sum'] = foy_by_decile_decl['cotsyn', 'sum'] / foy_by_decile_decl['rfr', 'sum']
    foy_by_decile_decl['taux_eff', 'mean'] = foy_by_decile_decl['cotsyn', 'mean'] / foy_by_decile_decl['rfr', 'mean']

    df_to_plot = foy_by_decile_decl['taux_eff', 'mean']

    # Plot : nombre de déclarant par décile
    sortie_graph = os.path.join(path, 'cotsyn-declarants-{}.png'.format(number_of_quantile))
    plt.figure()
    foy_by_decile['cotsyn_decl_w', 'sum'].plot(kind = 'bar', stacked = True, label = u'Nombre de foyers déclarant')

    # Plot : montant moyen de la réduction, parmi les déclarants
    df_to_plot = foy_by_decile_decl['cotsyn', 'mean']
    sortie_graph = os.path.join(path, 'cotsyn-montant-{}.png'.format(number_of_quantile))
    plt.figure()
    df_to_plot.plot(kind = 'bar', stacked = True, label = u'Montant moyen de la réduction')
    plt.legend(loc = 2)
    plt.xlabel(u'Décile de revenu fiscal de référence')
    plt.ylabel(u'Euros 2009')
    plt.savefig(sortie_graph)

#########################
#   Analyse par CSP
    input_data_frame = get_input_data_frame(year)
    input_data_frame.cstoti.fillna(0, inplace = True)
    input_data_frame['cstotr'] = input_data_frame.cstotr.astype('category')
    input_data_frame['cstoti'] = input_data_frame.cstoti.astype('category')
    input_data_frame['cstoti'].describe()
    input_data_frame['cstoti'].value_counts()
    input_data_frame['cstotr'].value_counts()
    input_data_frame2 = pandas.DataFrame(input_data_frame[['cstoti', 'cstotr']])
    dfi2 = pandas.DataFrame(cotsyn_ind[['f7ac', 'f7ac_decl_w', 'f7ac_decl', 'weight_individus',  u'decile_of_rfr', 'rfr', 'cotsyn']])
    cotsyn_ind_csp = input_data_frame2.merge(dfi2, left_index = True, right_index = True)
#    name_cat = ['Non renseigné', 'Agriculteurs exploitants', 'Artisans, commerçants, et chefs d\'entreprise',
#    'Cadres et professions intellectuelles sup.', 'Professions intermédiaires', 'Employés', 'Ouvriers', 'Retraités',
#    'Autres personnes sans activité professionnelle']
#    cotsyn_ind_csp.cstotr.cat.rename_categories(name_cat, inplace = True)
#
    cotsyn_ind_csp_decl = cotsyn_ind_csp.loc[cotsyn_ind_csp.f7ac > 0]
    cotsyn_ind_csp['un'] = 1
    grouped = cotsyn_ind_csp.groupby(cotsyn_ind_csp['cstotr'])
    cotsyn_ind_by_csp = pandas.DataFrame()
    cotsyn_ind_by_csp = grouped.agg([numpy.sum, numpy.mean])
    cotsyn_ind_by_csp['pct_decl', 'rate'] = cotsyn_ind_by_csp['f7ac_decl_w', 'sum'] / cotsyn_ind_by_csp['weight_individus', 'sum']
    del grouped
    grouped_decl = cotsyn_ind_csp_decl.groupby(cotsyn_ind_csp_decl['cstotr'])
    cotsyn_ind_csp_by_csp_decl = pandas.DataFrame()
    cotsyn_ind_csp_by_csp_decl = grouped_decl.agg([numpy.sum, numpy.mean])
    del cotsyn_ind_csp_by_csp_decl['weight_individus'], grouped_decl

    my_xticks = [u'Non renseigné', u'Agriculteurs exploitants', u'Artisans, commerçants,\n et chefs d\'entreprise',
        u'Cadres et professions\n intellectuelles sup.', u'Professions intermédiaires', u'Employés', u'Ouvriers', u'Retraités',
        u'Autres personnes sans\n activité professionnelle']
    x = numpy.array([0, 1, 2, 3, 4, 5, 6, 7, 8])

    from matplotlib import rcParams
    rcParams.update({'figure.autolayout': True})
    sortie_graph = os.path.join(path, 'pcs-montant.png')
    plt.figure()
    plt.barh(cotsyn_ind_by_csp.index, cotsyn_ind_csp_by_csp_decl['cotsyn', 'mean'], align='center', alpha=0.8)
    plt.yticks(x, my_xticks)
    plt.xlabel('Montant moyen parmis les cotisants')
    plt.ylabel(u'Catégorie socio-professionnelle')
    plt.savefig(sortie_graph)
    plt.show()

    sortie_graph = os.path.join(path, 'pcs-beneficiaires.png')
    plt.figure()
    plt.barh(cotsyn_ind_by_csp.index, cotsyn_ind_by_csp['pct_decl', 'rate'], align='center', alpha=0.4)
    plt.yticks(x, my_xticks)
    plt.xlabel('Pourcentage')
    plt.ylabel(u'Catégorie socio-professionnelle')
    plt.savefig(sortie_graph)
    plt.show()
