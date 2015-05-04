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


def make_simulation_df(year, sal):
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
        parent1 = dict(agem = 40 * 12 + 6, sal = sal),
        ).new_simulation()  # Remove debug = True, because logging is too slow.
    var_to_be_simulated = ['aide_logement', 'loyer', 'zone_apl', 'sal']
    return pandas.DataFrame(
        dict([
            (name, simulation.calculate(name, "{}-01".format(year))) for name in var_to_be_simulated
            ]))

if __name__ == '__main__':
    import logging
    import sys

    logging.basicConfig(level = logging.ERROR, stream = sys.stdout)
    df_celib_sal_0 = make_simulation_df(year = 2013, sal = 0)
    df_celib_sal_10000 = make_simulation_df(year = 2013, sal = 10000)
