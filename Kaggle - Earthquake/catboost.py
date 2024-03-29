import pandas as pd
import numpy as np
from catboost import CatBoostRegressor, Pool
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.svm import NuSVR, NuSVR
from sklearn.kernel_ridge import KernelRidge
import matplotlib.pyplot as plt

train = pd.read_csv('LANL-Earthquake-Prediction/train.csv', nrows = 6000000, dtype={'acoustic_data' : np.int16, 'time_to_failure' : np.float64})

print(train.head(10))

# Visualize 1% of sample data
train_ad_sample_df = train['acoustic_data'].values[::100]
train_ttf_sample_df = train['time_to_failure'].values[::100]

# Plot function
def plot_acc_ttf_data(train_ad_sample_df, train_ttf_sample_df, title = "Acoustic data/time to failure: 1% sample data"):
    fig, ax1 = plt.subplots(figsize = (12, 8))
    plt.title(title)
    plt.plot(train_ad_sample_df, color = 'r')
    ax1.set_ylabel('acoustic_data', color = 'r')
    plt.legend(['acoustic_data'], loc = (0.01, 0.95))
    ax2 = ax1.twinx()
    plt.plot(train_ttf_sample_df, color = 'b')
    ax2.set_ylabel('time_to_failure', color = 'b')
    plt.legend(['time_to_failure'], loc = (0.01, 0.9))
    plt.grid(True)
    plt.show()

# Features
def gen_features(X):
    strain = []
    strain.append(X.mean())
    strain.append(X.std())
    strain.append(X.min())
    strain.append(X.max())
    strain.append(X.kurtosis())
    strain.append(X.skew())
    strain.append(np.quantile(X,0.01))
    strain.append(np.quantile(X,0.05))
    strain.append(np.quantile(X,0.95))
    strain.append(np.quantile(X,0.99))
    strain.append(np.abs(X).max())
    strain.append(np.abs(X).mean())
    strain.append(np.abs(X).std())
    return pd.Series(strain)

# plot_acc_ttf_data(train_ad_sample_df, train_ttf_sample_df)
# del train_ad_sample_df
# del train_ttf_sample_df

# Features implementation
train = pd.read_csv('LANL-Earthquake-Prediction/train.csv', iterator = True, chunksize = 150_000, dtype = {'acoustic_data': np.int16, 'time_to_failure': np.float64})

X_train = pd.DataFrame()
y_train = pd.Series()
for df in train:
    ch = gen_features(df['acoustic_data'])
    X_train = X_train.append(ch, ignore_index = True)
    y_train = y_train.append(pd.Series(df['time_to_failure'].values[-1]))
    print(df)
# print(X_train.describe())


# Catboost (model 1)
train_pool = Pool(X_train, y_train)
m = CatBoostRegressor(iterations = 10000, loss_function = 'MAE', boosting_type = 'Ordered')
m.fit(X_train, y_train, silent = True)
print(m.best_score_)


# Grid search (model 2)
# from sklearn.preprocessing import StandardScaler
# from sklearn.model_selection import GridSearchCV
# from sklearn.svm import NuSVR, SVR
#
# scaler = StandardScaler()
# scaler.fit(X_train)
# X_train_scaled = scaler.transform(X_train)
#
# parameters = [{'gamma': [0.001, 0.005, 0.01, 0.02, 0.05, 0.1],
#                'C': [0.1, 0.2, 0.25, 0.5, 1, 1.5, 2]}]
#                #'nu': [0.75, 0.8, 0.85, 0.9, 0.95, 0.97]}]
#
# reg1 = GridSearchCV(SVR(kernel='rbf', tol=0.01), parameters, cv=5, scoring='neg_mean_absolute_error')
# reg1.fit(X_train_scaled, y_train.values.flatten())
# y_pred1 = reg1.predict(X_train_scaled)
#
# print("Best CV score: {:.4f}".format(reg1.best_score_))
# print(reg1.best_params_)
