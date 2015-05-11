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

import datetime
from openfisca_france.reforms import inversion_revenus
from openfisca_france.model.base import CAT
from openfisca_france.tests.base import assert_near, tax_benefit_system


def test_cho(year = 2011):
    simulation = tax_benefit_system.new_scenario().init_single_entity(
        axes = [dict(count = 11, max = 24000, min = 0, name = 'chobrut')],
        period = year,
        parent1 = dict(
            birth = datetime.date(year - 40, 1, 1),
            ),
        ).new_simulation(debug = True)
    brut = simulation.get_holder('chobrut').array
    imposable = simulation.calculate('cho')

    inversion_reform = inversion_revenus.build_reform(tax_benefit_system)

    inverse_simulation = inversion_reform.new_scenario().init_single_entity(
        axes = [dict(count = 11, max = 24000, min = 0, name = 'chobrut')],
        period = year,
        parent1 = dict(
            birth = datetime.date(year - 40, 1, 1),
            ),
        ).new_simulation(debug = True)

    inverse_simulation.get_holder('chobrut').delete_arrays()
    inverse_simulation.get_or_new_holder('choi').array = imposable.copy()
    new_brut = inverse_simulation.calculate('chobrut')
    assert_near(new_brut, brut, error_margin = 1)


def check_sal(type_sal, year = 2014):
    simulation = tax_benefit_system.new_scenario().init_single_entity(
        axes = [dict(count = 11, max = 24000, min = 0, name = 'salbrut')],
        period = year,
        parent1 = dict(
            birth = datetime.date(year - 40, 1, 1),
            type_sal = type_sal,
            ),
        ).new_simulation(debug = False)
    brut = simulation.get_holder('salbrut').array
    imposable = simulation.calculate('sal')

    inverse_simulation = simulation.clone(debug = True)
    inverse_simulation.get_holder('salbrut').delete_arrays()
    inverse_simulation.get_or_new_holder('sali').array = imposable.copy()
    new_brut = inverse_simulation.calculate('salbrut')

    assert_near(new_brut, brut, error_margin = 1)

def make_simulation_df(year):
    simulation = base.tax_benefit_system.new_scenario().init_single_entity(
        axes = [
            dict(
                count = 5,
                name = 'sal',
                max = 11818 * 5,
                min = 0,
                ),
            ],
        period = year,
        parent1 = dict(agem = 40 * 12 + 6),
        ).new_simulation()  # Remove debug = True, because logging is too slow.
    var_to_be_simulated = ['irpp', 'sal']
    return pandas.DataFrame(
        dict([
            (name, simulation.calculate(name)) for name in var_to_be_simulated
            ]))


if __name__ == '__main__':
    import logging
    import sys

    logging.basicConfig(level = logging.ERROR, stream = sys.stdout)
    test_cho()
    df_2007 = make_simulation_df(year = 2007)
    df_2006 = make_simulation_df(year = 2006)
