from __future__ import annotations
import os
from typing import List
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

def load_data(config):
    train = pd.read_csv(config["data_raw"]["train"])
    test = pd.read_csv(config["data_raw"]["test"])
    return train, test

def fill_missing_values(df):
    pass

def feature_engineering(df):
    df['maker'] = df['href'].astype('string').str.rsplit('/', n=1).str[-1].str.split('-').str[1].str.lower().fillna('')
    df['release'] = df['href'].astype('string').str.rsplit('/', n=1).str[-1].str.split('-').str[-2].str.lower().fillna('')
    df['release'] = df['release'].astype(int)
    df.drop(columns=['href', 'id'], inplace=True)
    return df

def encode_features(X_train: pd.DataFrame, X_test: pd.DataFrame):
    # Identify categorical columns
    categorical_cols = X_train.select_dtypes(include=["object", "category"]).columns.tolist()

    # If no categorical columns, return as-is
    if not categorical_cols:
        return X_train.copy(), X_test.copy()

    # In sklearn 1.5.x, use sparse_output to get dense arrays directly
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)

    # Fit on train, transform both
    X_train_encoded_array = encoder.fit_transform(X_train[categorical_cols])
    X_test_encoded_array = encoder.transform(X_test[categorical_cols])

    # Get encoded feature names
    encoded_col_names = encoder.get_feature_names_out(categorical_cols)

    # Convert to DataFrames with aligned index
    X_train_encoded = pd.DataFrame(X_train_encoded_array, columns=encoded_col_names, index=X_train.index)
    X_test_encoded = pd.DataFrame(X_test_encoded_array, columns=encoded_col_names, index=X_test.index)

    # Keep non-categorical columns and concat without resetting indices
    X_train_num = X_train.drop(columns=categorical_cols)
    X_test_num = X_test.drop(columns=categorical_cols)

    X_train_final = pd.concat([X_train_num, X_train_encoded], axis=1)
    X_test_final = pd.concat([X_test_num, X_test_encoded], axis=1)

    return X_train_final, X_test_final

def scale_features(X_train, X_test):
    scaler = StandardScaler()
    num_features = X_train.select_dtypes(include=['number']).columns
    scaler.fit(X_train[num_features])
    X_train[num_features] = scaler.transform(X_train[num_features])
    X_test[num_features] = scaler.transform(X_test[num_features])
    return X_train, X_test

def run(config=None):
    config = {
        "data_raw": {
            "train": "data/raw/train.csv",
            "test": "data/raw/test.csv"
        },
        "data_preprocessed": {
            "train": "data/preprocessed/train.csv",
            "test": "data/preprocessed/test.csv"
        }
    }
    train, test = load_data(config)
    X_train, y_train = train.drop(columns=["price"]), train["price"]
    X_test, y_test = test.drop(columns=["price"]), test["price"]

    X_train, X_test = feature_engineering(X_train), feature_engineering(X_test)
    X_train, X_test = scale_features(X_train, X_test)
    X_train, X_test = encode_features(X_train, X_test)

    train = pd.concat([X_train, y_train], axis=1)
    test = pd.concat([X_test, y_test], axis=1)

    os.makedirs(os.path.dirname(config["data_preprocessed"]["train"]), exist_ok=True)
    os.makedirs(os.path.dirname(config["data_preprocessed"]["test"]), exist_ok=True)
    train.to_csv(config["data_preprocessed"]["train"], index=False)
    test.to_csv(config["data_preprocessed"]["test"], index=False)
    
    print(f"[preprocess] Wrote {len(train)} rows -> {config['data_preprocessed']['train']}")
    print(f"[preprocess] Wrote {len(test)} rows -> {config['data_preprocessed']['test']}")
    
    return train, test

if __name__ == "__main__":
    run()

