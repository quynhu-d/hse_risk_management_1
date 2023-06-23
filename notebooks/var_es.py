import numpy as np
import pandas as pd
import seaborn as sns
sns.set_style('whitegrid')
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm
import pylab

from tqdm.auto import tqdm, trange

class VaR_ES:
    def __init__(self, ret, var_p=0.01, es_p=0.025):
        self.ret = ret
        self.var_p = var_p
        self.es_p = es_p

    def get_var_es(self):
        pass

    def plot_dist(self):
        pass

    def print_res(self):
        print(f'1-day VaR 99%: {self.var99_1d:.3f}')
        print(f'1-day ES 97.5%: {self.cvar975_1d:.3f}')
        print(f'10-day VaR 99%: {self.var99_10d:.3f}')
        print(f'10-day ES 97.5%: {self.cvar975_10d:.3f}')

class Parametric_VE(VaR_ES):
    def __init__(self, ret, var_p=0.01, es_p=0.025):
        super().__init__(ret, var_p, es_p)
        
    def get_var_es(self):
        self.tdf, self.tmean, self.tsigma = stats.t.fit(self.ret)
        self.support = np.linspace(self.ret.min(), self.ret.max(), 100)
        self.mean = self.ret.mean()
        self.sigma = self.ret.std()
        
        self.var99_1d = stats.norm.ppf(self.var_p, self.mean, self.sigma)
        self.cvar975_1d = self.ret[self.ret <= stats.norm.ppf(self.es_p, self.mean, self.sigma)].mean()
        self.var99_10d = self.var99_1d * (10 ** 0.5)
        self.cvar975_10d = self.cvar975_1d * (10 ** 0.5)

    def plot_dist(self):
        plt.figure(figsize=(6,4))
        self.ret.hist(bins=100, density=True, histtype='stepfilled', color='#104294')
        plt.plot(self.support, stats.t.pdf(self.support, loc=self.tmean, scale=self.tsigma, df=self.tdf), color='lightblue')
        plt.show()

class Historical_VE(VaR_ES):
    def __init__(self, ret, var_p=0.01, es_p=0.025):
        super().__init__(ret, var_p, es_p)
        
    def get_var_es(self):
        self.var99_1d = self.ret.quantile(self.var_p)
        self.cvar975_1d = self.ret[self.ret <= self.ret.quantile(self.es_p)].mean()
        self.var99_10d = self.var99_1d * (10 ** 0.5)
        self.cvar975_10d = self.cvar975_1d * (10 ** 0.5)

    def plot_dist(self):
        plt.figure(figsize=(6,4))
        self.ret.hist(bins=100, density=True, histtype='stepfilled', color='#104294')
        plt.axvline(x=self.ret.quantile(self.var_p), linewidth=1, color='lightblue')
        plt.axvline(x=self.ret.quantile(self.es_p), linewidth=1, color='lightblue')
        plt.show()

class Bootstrap_VE(VaR_ES):
    def __init__(self, ret, var_p=0.01, es_p=0.025, n_samples=10000):
        super().__init__(ret, var_p, es_p)
        self.n_samples = n_samples

    def _bootstrap_quantile(self, q, verbose):
        quantile_list = []        
        for i in trange(self.n_samples, leave=False) if verbose else range(self.n_samples):
            boot_df = self.ret.sample(len(self.ret), replace=True)
            quantile_list.append(boot_df.quantile(q))
        return quantile_list
        
    def get_var_es(self, verbose=True):
        quantile_list = self._bootstrap_quantile(self.var_p, verbose)
        self.var99_1d = np.mean(quantile_list)
        self.var99_10d = self.var99_1d * (10 ** 0.5)
        
        quantile_list = self._bootstrap_quantile(self.es_p, verbose)
        self.cvar975_1d = self.ret[self.ret <= np.mean(quantile_list)].mean()
        self.cvar975_10d = self.cvar975_1d * (10 ** 0.5)
    
    def plot_dist(self):
        pass