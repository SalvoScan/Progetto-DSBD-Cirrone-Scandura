#import matplotlib.pyplot as plt
from ADFtest import *
import ADFtest as adf
from statsmodels.tsa.seasonal import seasonal_decompose

def calcola_metadati(metric_df):
    # Valori della serie temporale
    metric_values = metric_df["value"]

    # Applichiamo adf_test (Augmented Dickey-Fuller) sulla serie
    # per controllare la stazionarietà della serie
    # if p-value <= 0.05 => Stationary
    # if p-value > 0.05 => Not-Stationary
    p_value= adf.adf_test(metric_values, "Results")
 
    # Calcolo dei valori relativi alla stagionalità della serie
    result = seasonal_decompose(metric_values, model='additive', period=3)  
    trend = result.trend
    seasonal = result.seasonal 
    # result.seasonal.plot()
    # print(seasonal)

    # Calcolo dell'autocorrelazione
    lag = range(0, len(metric_values)-1)
    corr = list()
    for l in lag:
        c = metric_values.autocorr(l)
        corr.append(c)

    return p_value, seasonal, corr
