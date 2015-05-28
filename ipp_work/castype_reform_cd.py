# -*- coding: utf-8 -*-
"""
Created on Tue May  5 14:35:00 2015

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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE,  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program,  If not, see <http://www.gnu.org/licenses/>.


import datetime
from openfisca_france.reforms import reform_cd

from openfisca_france.tests import base


def castype(year):
    assert year is not None
    reform = reform_cd.build_reform(base.tax_benefit_system)
    scenario = reform.new_scenario().init_single_entity(
        axes = [
            dict(
                count = 10,
                max = 13795 * (1 + .1) * (1 + .03),
                min = 13795 * (1 + .1) * (1 - .03),
                name = 'sal',
                ),
            ],
        period = year,
        parent1 = dict(birth = datetime.date(year - 40, 1, 1)),
        )

    reference_simulation = scenario.new_simulation(debug = True, reference = True)
    return reference_simulation.calculate('irpp')


if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(level = logging.ERROR, stream = sys.stdout)
    year = 2009
    castype(year)
