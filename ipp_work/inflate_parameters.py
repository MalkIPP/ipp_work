# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 16:40:38 2014

@author: malkaguillot
"""

def get_legislation_value(legislation_json, path, instant_str):
    start = legislation_json['start']
    stop = legislation_json['stop'],
    value = legislation_json.copy()

    for node in path.split("."):
        if node not in ["threshold", "value"]:
            value = value.get("children")
        value = value.get(node)
    return legislations.generate_dated_json_value(value["values"], start, stop, instant_str)
    
def inflate_legislation(reference_legislation_json, rates_inflate, period = None):
    inflated_legislation_json = copy.deepcopy(reference_legislation_json)
    for instant_str, rates in rates_inflate.iteritems():
        for rate, list_var_to_inflate in rates.iteritems():
            for var_to_inflate in list_var_to_inflate:
                print var_to_inflate
                old_value = get_legislation_value(reference_legislation_json, var_to_inflate, instant_str)
                print "old_value", old_value
                print "var_to_inflate", var_to_inflate
                inflated_legislation_json = reforms.update_legislation(
                    legislation_json = inflated_legislation_json,
                    path = var_to_inflate,
                    period = period,
                    value = (1 + rate)* old_value )
    return inflated_legislation_json

def show_monetary_parameters(dated_node_json, code = None, path = None):
    if path is None:
        path = []
    if code is not None:
        path = path + [code]
    node_type = dated_node_json['@type']
    node_unit = dated_node_json.get('unit', None)

    if node_type == u'Node':
#            if code is None:
            # Root node
#                assert instant is None, instant
#            else:
#                assert instant is not None
        for key, value in dated_node_json['children'].iteritems():
            show_monetary_parameters(value, code = key, path = path)
        return
#        assert instant is not None
    if node_unit == "currency":
        if node_type == u'Parameter':
            print '.'.join(path)
            return
        assert node_type == u'Scale'
        print '.'.join(path)
        if any('amount' in bracket for bracket in dated_node_json['brackets']):
            # AmountTaxScale
            for bracket_index, dated_bracket_json in enumerate(dated_node_json['brackets']):
                amount = dated_bracket_json.get('amount')
                assert not isinstance(amount, list)
                threshold = dated_bracket_json.get('threshold')
                assert not isinstance(threshold, list)
                prefix = '.'.join(path) + '.brackets[{}]'.format(bracket_index)
#                print "{}.threshold".format(prefix)
            return
        for bracket_index, dated_bracket_json in enumerate(dated_node_json['brackets']):
            base = dated_bracket_json.get('base', 1)
            assert not isinstance(base, list)
            rate = dated_bracket_json.get('rate')
            assert not isinstance(rate, list)
            threshold = dated_bracket_json.get('threshold')
            assert not isinstance(threshold, list)
            prefix = '.'.join(path) + '.brackets[{}]'.format(bracket_index)
        return


if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(level = logging.ERROR, stream = sys.stdout)
    simulation_year = 2014
    simulation_period = periods.period('year', simulation_year)
    reference_legislation_json = tax_benefit_system.legislation_json

    dated_reference_legislation_json=legislations.generate_dated_legislation_json(reference_legislation_json, instant=2014)
#    show_monetary_parameters(dated_node_json=dated_reference_legislation_json)
    path = "ir.abattements_speciaux.enf_montant"
    x = get_legislation_value(reference_legislation_json, path, '2013-01-01')
    dic_rates = {'2013-01-01': {
                    0.02:
                        ["ir.abattements_speciaux.enf_montant","ir.abattements_speciaux.inv_max1", "ir.abattements_speciaux.inv_max2"
                         ],
                    0.05:
                        ["ir.abattements_speciaux.enf_montant","ir.credits_impot.aidper.pac2"
                        ]
                    },
#                 '2014-01-01': {
#                    0.03:
#                        ["ir.abattements_speciaux.inv_max1", "ir.abattements_speciaux.inv_max2"
#                         ],
#                    0.06:
#                        ["ir.abattements_speciaux.enf_montant"
#                        ]
#                    }
                }
    inflate_legislation(reference_legislation_json, dic_rates)