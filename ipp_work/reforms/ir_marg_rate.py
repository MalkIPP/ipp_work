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


from __future__ import division


import logging


from openfisca_core import formulas, reforms


from openfisca_france.model.prelevements_obligatoires.impot_revenu import ir


log = logging.getLogger(__name__)


class rni(formulas.SimpleFormulaColumn):
    reference = ir.rni
    label = u"Revenu net imposable"
    url = "http://impotsurlerevenu.org/definitions/115-revenu-net-imposable.php"

    def function(self, simulation, period):
        ''' Revenu net imposable ou déficit à reporter'''
        period = period.start.offset('first-of', 'month').period('year')
        rng = simulation.calculate('rng', period)
        abat_spe = simulation.calculate('abat_spe', period)
        print "passe par simulation"
        return period, rng - abat_spe + 10


def build_reform(tax_benefit_system):
    # reference_legislation_json = tax_benefit_system.legislation_json
    # reform_legislation_json = copy.deepcopy(reference_legislation_json)
    # reform_legislation_json['children'].update(reform_legislation_subtree)
    Reform = reforms.make_reform(
        # legislation_json = reform_legislation_json,
        name = u'Revenu imposable + 10',
        new_formulas = [rni],
        reference = tax_benefit_system,
        )
    return Reform()
