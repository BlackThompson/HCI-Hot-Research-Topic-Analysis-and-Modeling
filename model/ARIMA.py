import datetime
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm

plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示乱码问题
plt.rcParams['axes.unicode_minus'] = False  # 解决符号无法显示问题

input_path = r'./input/2016-2023.xlsx'
output_path = r'./output/Devices.png'

df_words = pd.read_excel(input_path)
keywords_list = []
for word in df_words['Word']:
    keywords_list.append(word)
years_list = []
for year in range(2016, 2024):
    years_list.append(year)

X_time = years_list
# y_AI_true = [3, 4, 5, 23, 44, 60, 70, 117]
y_AI_true = [85, 62, 58, 45, 68, 32, 39, 25]
y_AI = [85, 62, 58, 45, 68, 32, 39, 25]

# 85 62	58	45	68	32	39	25
# 38	60	97	107	128	110	143	108
X_preyear = [2023, 2024, 2025, 2026]
AI_predict = [25]

Arima011 = sm.tsa.ARIMA(y_AI, order=(1, 2, 1)).fit()
AI_predict_2024 = Arima011.forecast(1)
y_AI.append(AI_predict_2024[0])
AI_predict.append(AI_predict_2024[0])

Arima011 = sm.tsa.ARIMA(y_AI, order=(1, 2, 1)).fit()
AI_predict_2025 = Arima011.forecast(1)
y_AI.append(AI_predict_2025[0])
AI_predict.append(AI_predict_2025[0])

Arima011 = sm.tsa.ARIMA(y_AI, order=(1, 2, 1)).fit()
AI_predict_2026 = Arima011.forecast(1)
y_AI.append(AI_predict_2026[0])
AI_predict.append(AI_predict_2026[0])

print('Arima_2024: ', AI_predict_2024)
print('Arima_2024: ', AI_predict_2025)
print('Arima_2024: ', AI_predict_2026)

plt.plot(X_time, y_AI_true, 'o-', label='Building Devices')
plt.plot(X_preyear, AI_predict, 'o-', label='Building Devices prediction')
plt.legend()
plt.title('ARIMA Prediction')
plt.savefig(output_path)
plt.show()
