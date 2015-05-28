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

import copy
from datetime import date

import logging

from numpy import maximum as max_, minimum as min_
from openfisca_core import columns, formulas, reforms, periods

from .. import entities
from ..model import base
from ..model.prelevements_obligatoires.impot_revenu import ir


log = logging.getLogger(__name__)


# TODO: les baisses de charges n'ont pas été codées car annulées (toute ou en partie ?)
# par le Conseil constitutionnel


# Reform formulas

class ir_brut(formulas.SimpleFormulaColumn):
    label = u"ir_brut"
    reference = ir.ir_brut

    def function(self, simulation, period):
        '''
        Impot sur le revenu avant non imposabilité et plafonnement du quotient
        'foy'
        '''
        period = period.start.offset('first-of', 'month').period('year')
        nbptr = simulation.calculate('nbptr', period)
        taux_effectif = simulation.calculate('taux_effectif', period)
        rni = simulation.calculate('rni', period)
        bareme = simulation.legislation_at(period.start).ir.bareme

        return period, (taux_effectif == 0) * nbptr * bareme.calc(rni / nbptr) + taux_effectif * rni


def build_reform(tax_benefit_system):
    reference_legislation_json = tax_benefit_system.legislation_json
    reform_legislation_json = copy.deepcopy(reference_legislation_json)
    reform_year = 2007
    reform_period = periods.period('year', reform_year)

    def update_threshold_bracket(bracket, amount):
        return reforms.update_legislation(
            legislation_json = reform_legislation_json,
            path = ('children', 'ir', 'children', 'bareme', 'brackets', bracket, 'threshold'),
            period = reform_period,
            value = amount,
            )

    def update_rate_bracket(bracket, rate):
        return reforms.update_legislation(
            legislation_json = reform_legislation_json,
            path = ('children', 'ir', 'children', 'bareme', 'brackets', bracket, 'rate'),
            period = reform_period,
            value = rate,
            )

    reform_legislation_json = update_rate_bracket(bracket = 0, rate = 0)
    reform_legislation_json = update_rate_bracket(bracket = 1, rate = .0683)
    reform_legislation_json = update_rate_bracket(bracket = 2, rate = .1914)
    reform_legislation_json = update_rate_bracket(bracket = 3, rate = .2826)
    reform_legislation_json = update_rate_bracket(bracket = 4, rate = .3738)
    reform_legislation_json = update_rate_bracket(bracket = 5, rate = .4262)
    reform_legislation_json = update_rate_bracket(bracket = 6, rate = .4809)

    inflation = 1
    reform_legislation_json = update_threshold_bracket(bracket = 0, amount = 0)
    reform_legislation_json = update_threshold_bracket(bracket = 1, amount = 4412 * inflation)
    reform_legislation_json = update_threshold_bracket(bracket = 2, amount = 8677 * inflation)
    reform_legislation_json = update_threshold_bracket(bracket = 3, amount = 15274 * inflation)
    reform_legislation_json = update_threshold_bracket(bracket = 4, amount = 24731 * inflation)
    reform_legislation_json = update_threshold_bracket(bracket = 5, amount = 40241 * inflation)
    reform_legislation_json = update_threshold_bracket(bracket = 6, amount = 49624 * inflation)

    reform_legislation_json = reforms.update_legislation(
        legislation_json = reform_legislation_json,
        path = ('children', 'ir', 'children', 'tspr', 'children', 'sabatsalpen'),
        period = reform_period,
        value = 0,
        )

    Reform = reforms.make_reform(
        legislation_json = reform_legislation_json,
        name = u'ir_2006',
        new_formulas = (),
        reference = tax_benefit_system,
        )
    return Reform()
