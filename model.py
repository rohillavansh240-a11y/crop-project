import pandas as pd
from sklearn.linear_model import LinearRegression

def train_model(crop):
    data = pd.read_csv("crop_data.csv")

    # crop filter
    data = data[data['Crop'] == crop]

    X = data[['Year']]
    y_price = data['Price']
    y_production = data['Production']

    model_price = LinearRegression()
    model_production = LinearRegression()

    model_price.fit(X, y_price)
    model_production.fit(X, y_production)

    return model_price, model_production