from prometheus_api_client import MetricsList, MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
import datetime as dt
from statsmodels.tsa.seasonal import seasonal_decompose
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA

import warnings
warnings.filterwarnings("ignore")

def calcola_predizioni(prom, k, v, time_prediction):

    start_time = parse_datetime("1h")
    end_time = parse_datetime("now")
    chunk_size = dt.timedelta(minutes=5)
    
    label_config = {'job':v}
    metric_data = prom.get_metric_range_data(metric_name=k, label_config=label_config, start_time=start_time,
        end_time=end_time, chunk_size=chunk_size)

    metric_object_list = MetricsList(metric_data)
    my_metric_object = metric_object_list[0]
    metric_df = MetricRangeDataFrame(metric_data)

    metric_values = metric_df["value"]
    # metric_values.plot()
    # plot_acf(metric_values,title='acf',lags=50)

    metric_values = metric_values.resample(rule='1T').mean()

    period = int(len(metric_values)/2)

    result = seasonal_decompose(metric_values, model='additive', period=period)  
    trend = result.trend.dropna()

    # metric_values.plot(figsize=(20, 8))
    # trend.plot(figsize=(20, 8))

    # dal trend ricaviamo gli iperparametri 
    iperparametri = auto_arima(trend)
    iperparametri = iperparametri.get_params().get("order")
    # print(iperparametri)

    n_train = int(len(trend)*2/3)

    train = trend.iloc[:n_train]
    test = trend.iloc[n_train:]

    model = ARIMA(train, order=iperparametri)
    results = model.fit()
    # print(results.summary())

    start=len(train)
    end=len(train)+len(test)-1

    predictions = results.predict(start=start, end=end, dynamic=False, typ='levels')

    #define size
    #plt.figure(figsize=(24,10))
    #add axes labels and a title
    #plt.ylabel('Values', fontsize=14)
    #plt.xlabel('Time', fontsize=14)
    #plt.title('Values over time pred', fontsize=16)
    #plt.plot(train,"-", label = 'train')
    #plt.plot(test,"-", label = 'test')
    #plt.plot(predictions,"--", label = 'pred')
    #add legend
    #plt.legend(title='Series')

    #error = rmse(test, predictions)
    #print(error)

    model = ARIMA(trend, order=iperparametri)
    results = model.fit()
    fcast = results.predict(start=len(trend),end = len(trend)+time_prediction,typ='levels')

    #plt.figure(figsize=(24,10))
    #add axes labels and a title
    #plt.ylabel('Values', fontsize=14)
    #plt.xlabel('Time', fontsize=14)
    #plt.title('Values over time pred', fontsize=16)
    #plt.plot(trend,"-", label = 'trend')
    #plt.plot(fcast,"--", label = 'pred')
    #add legend
    #plt.legend(title='Series')

    #print(fcast.max())
    #print(fcast.mean())
    #print(fcast.min())

    #plt.show()

    results_list = [fcast.max(), fcast.min(), fcast.mean()]
    return results_list, fcast