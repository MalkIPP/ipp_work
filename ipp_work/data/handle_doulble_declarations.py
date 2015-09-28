# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 11:25:40 2015

@author: malkaguillot
"""
import pandas

from openfisca_france_data import default_config_files_directory as config_files_directory
from openfisca_france_data.input_data_builders.build_openfisca_survey_data.base \
    import year_specific_by_generic_data_frame_name
from openfisca_france_data.temporary import get_store
from openfisca_survey_manager.survey_collections import SurveyCollection

# En entrée : tables individus, foyer et sif de ERFS (testé sur 2009)
year = 2009
year_specific_by_generic = year_specific_by_generic_data_frame_name(year)

erfs_survey_collection = SurveyCollection.load(collection = 'erfs', config_files_directory = config_files_directory)
survey = erfs_survey_collection.get_survey('erfs_{}'.format(year))
foyer_all = survey.get_values(table = year_specific_by_generic["foyer"])
erfind = survey.get_values(table = year_specific_by_generic["erf_indivi"])

temporary_store = get_store(file_name = 'erfs')
sif = temporary_store['sif']

ind = erfind[['ident', 'noindiv', 'declar1', 'declar2', 'zsali', 'persfip', 'persfipd']]
small_sif = sif[['noindiv', 'declar', 'causeXYZ']]
foyer = foyer_all[['ident', 'noindiv', 'declar', 'sif', '_1aj', '_1bj', '_1cj', '_1dj', '_1aq', '_1bq', '_8by', '_8cy'
                   ]]
foyer = foyer.drop(['_1cj', '_1dj', '_1aq', '_1bq', '_8by', '_8cy'], axis=1)
foyer_sif = pandas.merge(foyer, small_sif, on = ['declar', 'noindiv'])


def df_concatenate_declarations(df, sitaution_finale):
    # Les déclarants ont un noindiv qui finit par 1 i.e. df['noindiv'] % 2 == 1
    # Les conjoints (qui sont éventuellement déclarants d'une seconde déclaration)
        # ont un noindiv qui finit par 2 i.e. df['noindiv'] % 2 == 0
    df.loc[df['noindiv'] % 2 == 1, '_1aj_fictif'] = df.loc[df['noindiv'] % 2 == 1, '_1aj']
    df.loc[(df['noindiv'] % 2 == 1) & (df['causeXYZ'] == ' '), '_1aj_fictif'] = df.loc[(df['noindiv'] % 2 == 1)
        & (df['causeXYZ'] == ' '), '_1aj']
    df.loc[(df['noindiv'] % 2 == 0) & (df['causeXYZ'] == ' '), '_1bj_fictif'] = df.loc[(df['noindiv'] % 2 == 0)
        & (df['causeXYZ'] == ' '), '_1aj']
    df.loc[(df['causeXYZ'] != '{}'.format(situation_finale)), '_1aj_fictif'] = df.loc[(
        df['causeXYZ'] != '{}'.format(situation_finale)), '_1aj']
    df.loc[(df['causeXYZ'] != '{}'.format(situation_finale)), '_1bj_fictif'] = df.loc[(
        df['causeXYZ'] != '{}'.format(situation_finale)), '_1bj']
    grouped_foy = df.groupby('ident')
    divorce_foy_sum = grouped_foy.sum()
    return divorce_foy_sum[['_1aj_fictif', '_1bj_fictif']]

# la cause du dédoublement ou du doublement de la déclaration est affectée à la déclaration double :
    # A la déclaration commune avant le divorce
    # A la déclaration commune après un mariage
    # A la déclaration commune avant un décès

# Exemples sur deux foyers pour chaque cause de double déclaration
# Dans les trois cas, le choix est fait d'agrégé tous les revenus en une déclaration

# Les gens qui divorcent étaient codéclarant de cause 'D' avant divorce
divorces_foy = pandas.concat([foyer_sif.loc[foyer.ident == 9024628], foyer_sif.loc[foyer.ident == 9000173]])
divorces_foy = divorces_foy.drop(['_1cj', '_1dj', '_1aq', '_1bq', '_8by', '_8cy'], axis=1)
cause = 'D'
situation_finale = ' '
divorces_concat = df_concatenate_declarations(divorces_foy, situation_finale)

# Les gens qui se marient deviennent codéclarant de cause 'M' après mariage
maries_foy = pandas.concat([foyer_sif.loc[foyer.ident == 9000028], foyer_sif.loc[foyer.ident == 9034034]])
maries_foy = maries_foy.drop(['_1cj', '_1dj', '_1aq', '_1bq', '_8by', '_8cy'], axis=1)
situation_initiale = ' '
situation_finale = 'M'
maries_concat = df_concatenate_declarations(maries_foy, situation_finale)

# Les couples dont un décède étaient codéclarant de cause 'Z' et le survivant devient simple déclarant
deces_foy = pandas.concat([foyer_sif.loc[foyer.ident == 9044076], foyer_sif.loc[foyer.ident == 9038793]])
deces_foy = deces_foy.drop(['_1cj', '_1dj', '_1aq', '_1bq', '_8by', '_8cy'], axis=1)
situation_initiale = 'Z'
situation_finale = ' '
maries_concat = df_concatenate_declarations(maries_foy, situation_finale)

# TODO: étendre ce principe aux différentes cases de la déclaration
# TODO: en l'état, la fonction ne fonctionne que pour un sous-ensemble de déclarations affectées par la même cause de
    #dédoublement
# TODO: revoir l'utilisation des "situations initiale et finacle", qui ne sont pas dans le même sens suivant la cause

simple_declarations = ind.loc[(ind.declar1 !='') & (ind.declar2 =='')]
double_declarations = ind.loc[(ind.declar1 !='') & (ind.declar2 !='')]
double_declarations.zsali.sum() /(simple_declarations.zsali.sum() + double_declarations.zsali.sum())
# En 2009, les salaires des doubles déclarant constituent 2.5% de la totalité des salaires déclarés