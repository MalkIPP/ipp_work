# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 16:49:06 2015

@author: malkaguillot
"""
from ipp_work.ir_marg_rate import test_survey_simulation
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity


merged = test_survey_simulation(year = 2009, increment = 10, target = 'irpp', varying = 'rni')

data = merged['marginal_rate'][merged['marginal_rate']>1] # merged['marginal_rate']
maxi = np.max(data)
mini = np.min(data)
N = 1000
x_grid = np.linspace(mini, maxi, N)
X_src = data
bandwidth=0.5
kde_skl = KernelDensity(bandwidth=bandwidth)
kde_skl.fit(X_src[:, np.newaxis])
# score_samples() returns the log-likelihood of the samples
log_pdf = kde_skl.score_samples(x_grid[:, np.newaxis])
kde_sklearn = np.exp(log_pdf)
plt.plot(x_grid, kde_sklearn, color='blue', alpha=0.5, lw=3)


