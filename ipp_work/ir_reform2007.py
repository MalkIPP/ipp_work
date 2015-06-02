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


def make_simulation_df(year):
    simulation = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = [
            dict(
                count = 5,
                name = 'salaire_imposable',
                max = 11818 * 5,
                min = 0,
                ),
            ],
        period = year,
        parent1 = dict(agem = 40 * 12 + 6),
        ).new_simulation()  # Remove debug = True, because logging is too slow.
    var_to_be_simulated = ['irpp', 'salaire_imposable']
    return pandas.DataFrame(
        dict([
            (name, simulation.calculate(name)) for name in var_to_be_simulated
            ]))


if __name__ == '__main__':
    import logging
    import sys

    logging.basicConfig(level = logging.ERROR, stream = sys.stdout)
    df_2007 = make_simulation_df(year = 2007)
    df_2006 = make_simulation_df(year = 2006)
