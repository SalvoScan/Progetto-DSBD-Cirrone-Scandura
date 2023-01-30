from prometheus_api_client import MetricsList, MetricRangeDataFrame
from prometheus_api_client.utils import parse_datetime
import datetime as dt
from statsmodels.tsa.seasonal import seasonal_decompose
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from statsmodels.tools.eval_measures import rmse
import ADFtest as adf

import warnings
warnings.filterwarnings("ignore")

def calcola_predizioni(prom, k, v, time_prediction):
    start_time = parse_datetime("1h")
    end_time = parse_datetime("now")
    chunk_size = dt.timedelta(minutes=5)
    label_config = {'job': v}
    metric_data = prom.get_metric_range_data(metric_name=k , label_config=label_config, start_time=start_time,
        end_time=end_time, chunk_size=chunk_size)

    metric_object_list = MetricsList(metric_data)
    my_metric_object = metric_object_list[0]
    metric_df = MetricRangeDataFrame(metric_data)

    metric_values = metric_df["value"]
    metric_values = metric_values.resample(rule='1T').mean()
    period = int(len(metric_values)/2)

    result = seasonal_decompose(metric_values, model='additive', period=period)  
    trend = result.trend.dropna()


    # metric_values.plot()
    # trend.plot(figsize=(20,8))
    # plt.legend(loc="upper left")

    # qualche prova per vedere se il trend e' stazionario o meno 
    adf.adf_test(trend, "Trend")
    adf.adf_test(trend.diff().dropna(), "1 diff Trend")

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
     
    '''
    plt.figure(figsize=(24,10))
    add axes labels and a title
    plt.ylabel('Values', fontsize=14)
    plt.xlabel('Time', fontsize=14)
    plt.title('Values over time pred', fontsize=16)
    plt.plot(train,"-", label = 'train')
    plt.plot(test,"-", label = 'test')
    plt.plot(predictions,"--", label = 'pred')
    add legend
    plt.legend(title='Series')
    '''   

    # Calcoliamo errore quadratico medio per misurare l'accuratezza della previsione del modello(L'MSE è sempre >= 0)
    error = mean_squared_error(test, predictions)
    #print(error)

    # Calcoliamo il Root Mean Square Error (Di solito, un punteggio RMSE inferiore a 180 è considerato un buon punteggio per un algoritmo che funziona moderatamente o bene. 
    # Nel caso in cui il valore RMSE superi 180,  è necessario eseguire 
    # la selezione delle funzionalità e l'ottimizzazione dei parametri iper sui parametri del modello.)

    error = rmse(test, predictions)
    # print(error)

    # Proviamo a predirre sul trend 
    model = ARIMA(trend,order=iperparametri)
    results = model.fit()
    fcast = results.predict(start=len(trend),end = len(trend)+time_prediction,typ='levels')
    
    '''
    plt.figure(figsize=(24,10))
    add axes labels and a title
    plt.ylabel('Values', fontsize=14)
    plt.xlabel('Time', fontsize=14)
    plt.title('Values over time pred', fontsize=16)
    plt.plot(trend,"-", label = 'trend')
    plt.plot(fcast,"--", label = 'pred')

    add legend
    plt.legend(title='Series')

    print(fcast.mean())
    print(fcast.min())
    print(fcast.max())
    '''
   
    results_list= [ fcast.max(), fcast.min(),fcast.mean()]
    return results_list , fcast