# -*- coding: utf-8 -*-
"""Gold-price-by-Team-sql.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QeQNA918HeTvOpRZ9_n3-HKt0Rq4IyWh

## Business Problem
Historically, gold had been used as a form of currency in various parts of the world including the USA. In present times, precious metals like gold are held with central banks of all countries to guarantee re-payment of foreign debts, and also to control inflation which results in reflecting the financial strength of the country. Recently, emerging world economies, such as China, Russia, and India have been big buyers of gold, whereas the USA, SoUSA, South Africa, and Australia are among the big seller of gold.

Fractional change in gold price may result in huge profit or loss for investors as well as government banks.
Forecasting rise and fall in the daily gold rates can help investors to decide when to buy (or sell) the commodity. But Gold prices are dependent on many factors such as prices of other precious metals, prices of crude oil, stock exchange performance, Bonds prices, currency exchange rates, etc.
"""

from google.colab import drive
drive.mount('/content/drive')

"""#### Business Objectives and Constraints
* To accurately predict the future adjusted closing price of Gold ETF (Exchang Traded Funds) across a given period of time in the future.
* The model should not take too long to return prediction (Latency concerns)
* To Maximize the Coefficient of determination (R2) as much as posible (the closer it is to 1 the better)
* To minimize the Root Mean Squared Error (RMSE) as much as posible (the closer it is to zero the better)

#### Type of Machine Learning Problem
It is a Regression problem as the target variable (adjusted closing price) is a **continuous** value.

####  Performance Metric

- R^2 score (Coefficient of determination)
- RMSE (root mean squared error)

### Data Overview
- Data Source: https://www.kaggle.com/datasets/sid321axn/gold-price-prediction-dataset <br><br>
- Data for this study is collected from November 18th 2011 to January 1st 2019 from various sources.<br><br>
- The dataset has 1718 rows in total and 80 columns in total. Data for attributes, such as Oil Price, Standard and Poor’s (S&P) 500 index, Dow Jones Index US Bond rates (10 years), Euro USD exchange rates, prices of precious metals Silver and Platinum and other metals such as Palladium and Rhodium, prices of US Dollar Index, Eldorado Gold Corporation and Gold Miners ETF were gathered.<br><br>
- The historical data of Gold ETF fetched from Yahoo finance has 7 columns, Date, Open, High, Low, Close, Adjusted Close, and Volume, the difference between Adjusted Close and Close is that the closing price of a stock is the price of that stock at the close of the trading day. Whereas the adjusted closing price takes into account factors such as dividends, stock splits, and new stock offerings to determine a value. So, Adjusted Close is the outcome variable which is the value you have to predict.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(context="notebook", palette="coolwarm", style = 'ticks' ,font_scale = 1.2, color_codes=True)

"""## Loading Data"""

data = pd.read_csv("/content/drive/MyDrive/SQL WORK/FINAL_USO.csv") #change the file path as applicable to you
data.head(2)

"""## Data Cleaning"""

data.columns

"""### Sanitary check"""

#sanitory check to observe the datatypes of the features
data.info()

"""#### Observation:
- No missing values
- The `Date` feature is of type `object`.
"""

#converting the datatype of "Date" feature from "object" to "datetime"
data.Date = pd.to_datetime(data.Date, format="%Y-%m-%d" )

#checking for any missing values
data.isnull().values.any()

"""It is observed that `Close` and `Adj Close` are duplicates of each other as shown below, hence the need to drop one (`Close`)"""

data[['Close', 'Adj Close']].head()

#checking to see if features "Close" and "Adj Close" are duplicates
(data.Close.values == data['Adj Close'].values).all()

#droping the "Close" feature, since it's a duplicate of "Adj Close"
data.drop('Close', axis=1, inplace=True)



"""## Exploratory Data Analysis"""

data.tail()

"""### Transforming the dataframe into a time series by turning the "Date" feature to index"""

#Transform dataframe into a time series by turning the "Date" feature into index
data.set_index('Date', inplace=True)

"""### Plot of Gold price over time
Lets plot just the target variable against time and check for seasonality and trend (how the prices of gold varies over time)
"""

#data['Adj Close'].plot()
plt.figure(figsize=(10,5))
plt.plot(data['Adj Close'])
plt.xlabel('Year')
plt.ylabel('Price [USD]')
plt.title('Gold Prices')
plt.grid()
plt.show()

"""### Observation
Here we can clearly see that gold prices are very high in the time period of 2012 to 2013. And since then, there has been a general decline in the price till 2016, then a little rise between 2016 and late 2018 with some fluctuations in between.

### Zooming in to the last 3 years of data
Lets have a closer look at the trend for the last 3 years
"""

last_3_years = data['Adj Close'].loc[data.index>='2016-01-01']
plt.figure(figsize=(10,5))
plt.plot(last_3_years)
plt.xlabel('Year')
plt.xticks(rotation=45)
plt.ylabel('Price [USD]')
plt.title('Gold Prices')
plt.grid()
plt.show()

"""### Zooming in closer to the last 2 years of data
Lets have a closer look at the trend for the last 2 years, we may be able to see things more clearly
"""

last_2_years = data['Adj Close'].loc[data.index>='2017-01-01']
plt.figure(figsize=(10,5))
plt.plot(last_2_years)
plt.xlabel('Year')
plt.xticks(rotation=45)
plt.ylabel('Price [USD]')
plt.title('Gold Prices')
plt.grid()
plt.show()

"""### Observation
As we zoom closer, we observed that there exist some level of seasonality in the Gold Prices and some seasonality are higher than others, hence the need to transform the seasonality into a stationary data by subtracting the previous seasonality from the current seasonality.

### Zooming in even closer to just last one year of data
"""

last_1_years = data['Adj Close'].loc[data.index>='2018-01-01']
plt.figure(figsize=(10,5))
plt.plot(last_1_years)
plt.xlabel('Year')
plt.xticks(rotation=45)
plt.ylabel('Price [USD]')
plt.title('Gold Prices')
plt.grid()
plt.show()

"""### Observation
Looking at the graph above, it can be seen that the first quarter (Jan to Apr) of 2018 recorded the highest and steady price of Gold for the year, after which there was a steady decline up till mid August, then increases a little and remain almost steady till around mid September before it then started recording a almost steady increace till the end of the year (2018). But on a high level note, 2018 recorded a general decreasing trend in Gold Price.

## AutoCorrelation:
Autocorrelation is the correlation of a point in the series with a point with lag (previous point) taken as one day of the same series. If a series show a positive autocorrelation then we say the series is **momentum** (trend following) and if the series shows a negative autocorrelation then we say the series is **mean reversing**. (Mean reversion is a financial term for the assumption that an asset's price will tend to converge to the average price over time, read more about **Mean reversion** [here](https://en.wikipedia.org/wiki/Mean_reversion_(finance)))

In python we can use pandas autocorr() function to calculate autocorrelation of a series.
"""

#calculating the Autocorrelation of the "Adj Close" using the python's inbuild "autocorr()" function
print(data['Adj Close'].autocorr())

"""### Observation
Here the autocorrelation value is positive and high (**0.997438**), hence we can conclude that the series is a trend following series.

## Percentage Change
Lets use the pct_change() function available in pandas to see how the prices of Gold changes over a time lag in days.
This is useful in comparing the percentage of change in a time series of elements.
This function by default calculates the percentage change from the immediately previous row. It output first row as NaN so we have to apply dropna(). Here we test percent change in gold price to check that series is a random walk or not.
"""

from statsmodels.tsa.stattools import adfuller
time_period = 20
results = adfuller(data['Adj Close'].pct_change(periods=time_period).dropna())
print(f'The % change of any current price from the last {time_period} days is: {round(results[1], 6)*100}%')

"""### Observation on the percentage change
The percentage change of any current price with that of 20 days ago is: 0.002%, which is a strong indication that the price of Gold at any given time $\tau$ is not a random walk but a function of trend. Hence we may want to experiment by trying to predict the Gold price using just the trend information (with the help of **Autoregressive models**), then compare the result with the prediction that takes into account other features.

## Correlation of features to the target ("Adj Close")
"""

#checking for correlation between features and target variable
corr_data = data.corr()#.abs()['Adj Close'].sort_values(ascending=False)
corr_data

"""### Visualizing the correlation of features to the target"""

def plot_corr_scores(corr_data, target):
    """
    Displays the horizontal bar plot showing how features are correlated with the target variable
    corr_data: The DataFrame containing the correlation scores between all the features
    target: The dependent variable whoes value you aim to predict
    """
    scores = corr_data.abs()[target].drop(target)
    scores = scores.sort_values(ascending=True)
    width = np.arange(len(scores))
    ticks = list(scores.index)
    plt.barh(width, scores)
    plt.yticks(width, ticks)
    plt.title("Correlation of features to Target")
    plt.grid()
    
plt.figure(dpi=80, figsize=(10,18))
plot_corr_scores(corr_data, 'Adj Close')

corr_data



"""## Making a dataframe of highly correlated features"""

#selecting features that are highly correlated with the target variable "Adj Close"
high_corr_features = list(corr_data[corr_data >= 0.3].index)
high_corr_features.insert(0, 'Date')

high_corr_df = data.reset_index()[high_corr_features]
high_corr_df.set_index('Date', inplace=True)
high_corr_df.head(2)

"""## Splitting the data into Train and Test sets
Since it is a time series data, it will be splited on the time axis in order to avoid data leakage.
"""

features_data = high_corr_df.drop('Adj Close', axis=1)
target = high_corr_df['Adj Close']



from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(features_data, target, test_size=.3, shuffle=False)



"""### Splitting the Train data further for training and cross validation """

X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=.2, shuffle=False)

"""## Data Normalization

USING MINMAXSCALER
"""

type(y_train)

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
norm_xtrain = scaler.fit_transform(X_train)
norm_xval = scaler.fit_transform(X_val)
norm_xtest = scaler.fit_transform(X_test)

norm_ytrain = scaler.fit_transform(y_train.values.reshape(-1,1))
norm_yval = scaler.fit_transform(y_val.values.reshape(-1,1))
norm_ytest = scaler.fit_transform(y_test.values.reshape(-1,1))



"""USING STANDARDSCALAR"""

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
stand_xtrain = scaler.fit_transform(X_train)
stand_xval = scaler.fit_transform(X_val)
stand_xtest = scaler.fit_transform(X_test)

stand_ytrain = scaler.fit_transform(y_train.values.reshape(-1,1))
stand_yval = scaler.fit_transform(y_val.values.reshape(-1,1))
stand_ytest = scaler.fit_transform(y_test.values.reshape(-1,1))



"""## Feature Engineering"""





"""## Modelling

USING HISTORIC DATA
"""

train_label = list(y_train)
type(train_label)

val_label = list(y_val)
type(val_label)

test_label = list(y_test)
type(test_label)

from numpy import array
 
# split a univariate sequence into samples
def split_sequence(sequence, n_steps):
	X, y = list(), list()
	for i in range(len(sequence)):
		# find the end of this pattern
		end_ix = i + n_steps
		# check if we are beyond the sequence
		if end_ix > len(sequence)-1:
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)
 

# choose a number of time steps
n_steps = 7
# split into samples
Xtrain1, ytrain1 = split_sequence(train_label, n_steps)
# summarize the data
print(Xtrain1.shape, ytrain1.shape)

Xtrain1[0], ytrain1[0]

# choose a number of time steps
n_steps = 7
# split into samples
Xval1, yval1 = split_sequence(val_label, n_steps)
# summarize the data
print(Xval1.shape, yval1.shape)

# choose a number of time steps
n_steps = 7
# split into samples
Xtest1, ytest1 = split_sequence(test_label, n_steps)
# summarize the data
print(Xtest1.shape, ytest1.shape)

from sklearn.tree import DecisionTreeRegressor
dt = DecisionTreeRegressor(random_state=0)
model1 = dt.fit(Xtrain1, ytrain1)

from sklearn.metrics import mean_squared_error, r2_score
def validate_result(model,val_x, val_y):
    predicted = model.predict(val_x)
    RSME_score = np.sqrt(mean_squared_error(val_y, predicted))
    print('RMSE: ', RSME_score)
    
    R2_score = r2_score(val_y, predicted)
    print('R2 score: ', R2_score)

from sklearn.metrics import mean_squared_error, r2_score
def test_result(model,test_x, test_y):
    predicted = model.predict(test_x)
    RSME_score = np.sqrt(mean_squared_error(test_y, predicted))
    print('RMSE: ', RSME_score)
    
    R2_score = r2_score(test_y, predicted)
    print('R2 score: ', R2_score)

validate_result(model1,Xval1, yval1)

test_result(model1,Xtest1, ytest1)

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LassoCV
from sklearn.linear_model import RidgeCV
from sklearn import linear_model
from sklearn.linear_model import SGDRegressor

clf = [ LinearRegression(), DecisionTreeRegressor(random_state=0), RandomForestRegressor(random_state=0),
       LassoCV(),  RidgeCV(), linear_model.BayesianRidge(),GradientBoostingRegressor(),
       SGDRegressor()]
models = [ 'LR', 'DTR', 'RFR', 'LC', 'RC', 'LMB', 'GBR', 'SGDR', ]

for clf, model in zip(clf,models):
  clf.fit ( Xtrain1, ytrain1)
  print ( f'performance of {model} on val:')
  validate_result(clf,Xval1, yval1)
  print("\n")
  print ( f'performance of {model} on test:')
  test_result(clf,Xtest1, ytest1)
  print("\n")

"""#USING ALL FEATURES"""

X = data.drop('Adj Close', axis=1)
y = data['Adj Close']
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=.3, shuffle=False)
X_tr, X_va, y_tr, y_va = train_test_split(X_tr, y_tr, test_size=.2, shuffle=False)

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 1))
norm_xtr = scaler.fit_transform(X_tr)
norm_xva = scaler.fit_transform(X_va)
norm_xte = scaler.fit_transform(X_te)

norm_ytr = scaler.fit_transform(y_tr.values.reshape(-1,1))
norm_yva = scaler.fit_transform(y_va.values.reshape(-1,1))
norm_yte = scaler.fit_transform(y_te.values.reshape(-1,1))

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
stand_xtr = scaler.fit_transform(X_tr)
stand_xva = scaler.fit_transform(X_va)
stand_xte = scaler.fit_transform(X_te)

stand_ytr = scaler.fit_transform(y_tr.values.reshape(-1,1))
stand_yva = scaler.fit_transform(y_va.values.reshape(-1,1))
stand_yte = scaler.fit_transform(y_te.values.reshape(-1,1))

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LassoCV
from sklearn.linear_model import RidgeCV
from sklearn import linear_model
from sklearn.linear_model import SGDRegressor

clf = [ LinearRegression(), DecisionTreeRegressor(random_state=0), RandomForestRegressor(random_state=0),
       LassoCV(),  RidgeCV(), linear_model.BayesianRidge(),GradientBoostingRegressor(),
       SGDRegressor()]
models = [ 'LR', 'DTR', 'RFR', 'LC', 'RC', 'LMB', 'GBR', 'SGDR', ]

for clf, model in zip(clf,models):
  clf.fit ( X_tr, y_tr )
  print ( f'performance of {model} on val:')
  validate_result(clf,X_va, y_va)
  print("\n")
  print ( f'performance of {model} on test:')
  test_result(clf,X_te, y_te)
  print("\n")

clf = [ LinearRegression(), DecisionTreeRegressor(random_state=0), RandomForestRegressor(random_state=0),
       LassoCV(),  RidgeCV(), linear_model.BayesianRidge(),GradientBoostingRegressor(),
       SGDRegressor()]
models = [ 'LR', 'DTR', 'RFR', 'LC', 'RC', 'LMB', 'GBR', 'SGDR', ]

for clf, model in zip(clf,models):
  clf.fit ( norm_xtr, norm_ytr)
  print ( f'performance of {model} on val:')
  validate_result(clf,norm_xva, norm_yva)
  print("\n")
  print ( f'performance of {model} on test:')
  test_result(clf,norm_xte, norm_yte)
  print("\n")

clf = [ LinearRegression(), DecisionTreeRegressor(random_state=0), RandomForestRegressor(random_state=0),
       LassoCV(),  RidgeCV(), linear_model.BayesianRidge(),GradientBoostingRegressor(),
       SGDRegressor()]
models = [ 'LR', 'DTR', 'RFR', 'LC', 'RC', 'LMB', 'GBR', 'SGDR', ]

for clf, model in zip(clf,models):
  clf.fit ( stand_xtrain, stand_ytrain)
  print ( f'performance of {model} on val:')
  validate_result(clf,stand_xva, stand_yva)
  print("\n")
  print ( f'performance of {model} on test:')
  test_result(clf,stand_xte, stand_yte)
  print("\n")

"""#USING HIGHLY CORRELATED FEATURES

MODELLING WITHOUT NORMALIZATION OR STANDARDIZATION
"""

from sklearn.tree import DecisionTreeRegressor
dt = DecisionTreeRegressor(random_state=0)
model2 = dt.fit(X_train, y_train)

validate_result(model2,X_val, y_val)

test_result(model2,X_test, y_test)

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LassoCV
from sklearn.linear_model import RidgeCV
from sklearn import linear_model
from sklearn.linear_model import SGDRegressor

clf = [ LinearRegression(), DecisionTreeRegressor(random_state=0), RandomForestRegressor(random_state=0),
       LassoCV(),  RidgeCV(), linear_model.BayesianRidge(),GradientBoostingRegressor(),
       SGDRegressor()]
models = [ 'LR', 'DTR', 'RFR', 'LC', 'RC', 'LMB', 'GBR', 'SGDR', ]

for clf, model in zip(clf,models):
  clf.fit ( X_train, y_train )
  print ( f'performance of {model} on val:')
  validate_result(clf,X_val, y_val)
  print("\n")
  print ( f'performance of {model} on test:')
  test_result(clf,X_test, y_test)
  print("\n")

"""##From above it can be seen that Random Forest Regressor  had the best RMSE of 0.31825 and R squared result of 0.99535

MODELLING WITH NORMALIZED DATA
"""

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LassoCV
from sklearn.linear_model import RidgeCV
from sklearn import linear_model
from sklearn.linear_model import SGDRegressor

clf = [ LinearRegression(), DecisionTreeRegressor(random_state=0), RandomForestRegressor(random_state=0),
       LassoCV(),  RidgeCV(), linear_model.BayesianRidge(),GradientBoostingRegressor(),
       SGDRegressor()]
models = [ 'LR', 'DTR', 'RFR', 'LC', 'RC', 'LMB', 'GBR', 'SGDR', ]

for clf, model in zip(clf,models):
  clf.fit ( norm_xtrain, norm_ytrain)
  print ( f'performance of {model} on val:')
  validate_result(clf,norm_xval, norm_yval)
  print("\n")
  print ( f'performance of {model} on test:')
  test_result(clf,norm_xtest, norm_ytest)
  print("\n")

"""##From above it can be seen that Linear model bayesianRidge had the best RMSE of 0.01232 and R square result of 0.99156

MODELLING WITH NORMALIZED DATA
"""

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LassoCV
from sklearn.linear_model import RidgeCV
from sklearn import linear_model
from sklearn.linear_model import SGDRegressor

clf = [ LinearRegression(), DecisionTreeRegressor(random_state=0), RandomForestRegressor(random_state=0),
       LassoCV(),  RidgeCV(), linear_model.BayesianRidge(),GradientBoostingRegressor(),
       SGDRegressor()]
models = [ 'LR', 'DTR', 'RFR', 'LC', 'RC', 'LMB', 'GBR', 'SGDR', ]

for clf, model in zip(clf,models):
  clf.fit ( stand_xtrain, stand_ytrain)
  print ( f'performance of {model} on val:')
  validate_result(clf,stand_xval, stand_yval)
  print("\n")
  print ( f'performance of {model} on test:')
  test_result(clf,stand_xtest, stand_ytest)
  print("\n")

"""##From above it can be seen that Linear model bayesianRidge had the best RMSE of 0.03872 and R square result of 0.99850

## Model Evaluation
"""





"""## Comparison (Tabular form)"""



