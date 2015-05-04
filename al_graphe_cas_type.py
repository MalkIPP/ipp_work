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


from openfisca_france.tests import base
import pandas


def aide_au_logement_by_loyer_celib(year, sal):
    simulation = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = [
            dict(
                count = 1000,
                name = 'loyer',
                max = 500,
                min = 0,
                ),
            ],
        period = '2013-01',
        menage = dict(depcom = '69381', statut_occupation= 4),
        parent1 = dict(agem = 40 * 12 + 6, sal = {"2011": sal, "2012": sal, "2013": sal}),
        ).new_simulation()  # Remove debug = True, because logging is too slow.
    var_to_be_simulated = ['aide_logement', 'loyer']
    return pandas.DataFrame(
        dict([
            (name, simulation.calculate(name, "{}-01".format(year))) for name in var_to_be_simulated
            ]))


def aide_au_logement_by_loyer_parent_isole(year, sal):
    simulation = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = [
            dict(
                count = 100,
                name = 'loyer',
                max = 500,
                min = 0,
                ),
            ],
        period = '2013-01',
        menage = dict(depcom = '69381', statut_occupation= 4),
        enfants = [
            dict(),
            dict(birth = year - 5)
            ],
        parent1 = dict(agem = 40 * 12 + 6, sal = {"2011": sal, "2012": sal, "2013": sal}),
        ).new_simulation()  # Remove debug = True, because logging is too slow.
    var_to_be_simulated = ['aide_logement', 'loyer']
    return pandas.DataFrame(
        dict([
            (name, simulation.calculate(name, "{}-01".format(year))) for name in var_to_be_simulated
            ]))


def aide_au_logement_by_ressource(year, depcom):
    simulation = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = [
            dict(
                count = 15000,
                name = 'br_pf_i',
                max = 15000,
                min = 0,
                ),
            ],
        period = '2013-01',
        menage = dict(loyer = 500, depcom = depcom, statut_occupation= 4),
        parent1 = dict(agem = 40 * 12 + 6),
        ).new_simulation()  # Remove debug = True, because logging is too slow.
    var_to_be_simulated = ['aide_logement', 'loyer', 'br_pf_i']
    return pandas.DataFrame(
        dict([
            (name, simulation.calculate(name, "{}-01".format(year))) for name in var_to_be_simulated
            ]))

if __name__ == '__main__':
    import logging
    import sys
    import os

    logging.basicConfig(level = logging.ERROR, stream = sys.stdout)

# Graphe 4: allocation logement locatif mensuel selon loyer (zone 2)
    df_celib_sal_0 = aide_au_logement_by_loyer_celib(year = 2013, sal = 0)
    df_celib_sal_10000 = aide_au_logement_by_loyer_celib(year = 2013, sal = 10000)
    df_isole_sal_0 = aide_au_logement_by_loyer_parent_isole(year = 2013, sal = 0)
    df_isole_sal_10000 = aide_au_logement_by_loyer_parent_isole(year = 2013, sal = 10000)

# Graphe 5: allocation logement locatif mensuel pour un individu isolé
#           au plafond de sa zone selon sa base ressource
    df_celib_by_ressource_zone1 = aide_au_logement_by_ressource(year = 2013, depcom = '75114')
    df_celib_by_ressource_zone2 = aide_au_logement_by_ressource(year = 2013, depcom = '69381')
    df_celib_by_ressource_zone3 = aide_au_logement_by_ressource(year = 2013, depcom = '87191')

    df_celib_by_ressource_zone1 = df_celib_by_ressource_zone1.rename(columns={'aide_logement': 'aide_logement_zone1'})
    df_celib_by_ressource_zone2 = df_celib_by_ressource_zone2.rename(columns={'aide_logement': 'aide_logement_zone2'})
    df_celib_by_ressource_zone3 = df_celib_by_ressource_zone3.rename(columns={'aide_logement': 'aide_logement_zone3'})
    del df_celib_by_ressource_zone2['loyer'], df_celib_by_ressource_zone2['br_pf_i']
    del df_celib_by_ressource_zone3['loyer'], df_celib_by_ressource_zone3['br_pf_i']
    df_by_zone = pandas.concat([df_celib_by_ressource_zone1, df_celib_by_ressource_zone2, df_celib_by_ressource_zone3], axis = 1)

# Exportation vers excel
    path = os.path.join('/Users/malkaguillot/Documents/IPP/statapp/', 'data_cas_type.xlsx')
    writer = pandas.ExcelWriter(path)
    df_celib_sal_0.to_excel(writer, sheet_name = 'df_celib_sal_{}'.format(0))
    df_celib_sal_10000.to_excel(writer, sheet_name = 'df_celib_sal_{}'.format(10000))
    df_isole_sal_0.to_excel(writer, sheet_name = 'df_isole_sal_{}'.format(0))
    df_isole_sal_10000.to_excel(writer, sheet_name = 'df_isole_sal_{}'.format(10000))
    df_by_zone.to_excel(writer, sheet_name = 'df_by_zone')
    writer.save()
