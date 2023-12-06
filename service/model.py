import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import json


def get_dataframes():
    print('Parsing data...')
    df = pd.read_csv('./data/world-happiness-report.csv')

    df = df[['Country name',
             'year',
             'Log GDP per capita',
             'Social support',
             'Freedom to make life choices',
             'Healthy life expectancy at birth']]
    df = df.dropna(how='any', axis=0)

    df['Log GDP per capita'] = df['Log GDP per capita'].apply(lambda x: x * 1000)
    df['Log GDP per capita'] = df['Log GDP per capita'].astype(int)

    df['Social support'] = df['Social support'].apply(lambda x: x * 100)
    df['Social support'] = df['Social support'].astype(int)

    df['Freedom to make life choices'] = df['Freedom to make life choices'].apply(lambda x: x * 100)
    df['Freedom to make life choices'] = df['Freedom to make life choices'].astype(int)

    dfs = []
    for country in df['Country name'].unique():
        country_df = df[df['Country name'] == country].drop(columns=['Country name'])
        dfs.append((country, country_df))

    df.drop(columns=['Country name'], inplace=True)

    dfs.insert(0, ('All', df))

    return dfs


def train_model(df, country):
    y = df['Healthy life expectancy at birth']
    X = df.drop('Healthy life expectancy at birth', axis=1)

    print(f'Training data for country {country}...')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.8, random_state=0)
    reg = LinearRegression().fit(X_train, y_train)
    y_pred = reg.predict(X_test)

    RMSE = pow(mean_squared_error(y_pred, y_test), 0.5)
    R2 = r2_score(y_pred, y_test)

    return reg, y_pred, RMSE, R2


def get_results():
    results = []

    for country, df in get_dataframes():
        reg, y_pred, RMSE, R = train_model(df, country)
        year, gdp, social_support, freedom = reg.coef_

        results.append({
            'country': country,
            'intercept': reg.intercept_,
            'coef': {
                'year': year,
                'gdp': gdp,
                'social_support': social_support,
                'freedom': freedom
            },
            'rmse': RMSE,
            'r2': R
        })

    return results


def write_results(results):
    print('Writing results...')
    with open('results.json', 'w') as fp:
        json.dump(results, fp, separators=(',', ':'))


if __name__ == '__main__':
    write_results(get_results())
    print('Done!')
