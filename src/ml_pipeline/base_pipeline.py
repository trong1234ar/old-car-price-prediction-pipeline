from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypeVar, Generic

from pyspark.sql import DataFrame
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor, GBTRegressor, LinearRegression
try:
    from xgboost.spark import SparkXGBRegressor
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

ModelType = TypeVar('ModelType')

class BasePredictionPipeline(Generic[ModelType], ABC):

    def __init__(self, target_col, model_name, config):
        self.target_col = target_col
        self.config = config
        self.model_name = model_name
        self.model = self._build_model()

        self.fitted = False
        self.num_imputer = None
        self.cat_imputer = None
        self.encoder = None
        self.scaler = None
        self.categorical_cols = []
        self.numeric_cols = []
    
    def fit(self, train_data: DataFrame):
        self._infer_column_types(train_data)

        # Preprocess the training data
        processed_data = self._preprocess(train_data)
        
        # Build and train the model
        self.model = self.model.fit(processed_data)
        
        self.fitted = True
    
    def predict(self, data: DataFrame) -> DataFrame:
        self._infer_column_types(data)

        # if not self.fitted or self.model is None:
        #     raise RuntimeError("Model has not been trained yet. Call fit() first.")
            
        # Preprocess the input data
        processed_data = self._preprocess(data)
        
        # Make predictions
        return self.model.transform(processed_data)
    
    def _preprocess(self, data: DataFrame) -> DataFrame:
        print("[Start imputing]")
        data, self.num_imputer = self._fill_missing_data(data, self.num_imputer)
        print("[Start feature engineering]")
        data = self._feature_engineering(data)
        print("[Start scaling]")
        data, self.scaler = self._scale_features(data, self.scaler)
        print("[Start encoding]")
        data, self.encoder = self._encode_features(data, self.encoder)
        print("[Start assembling]")
        assembler = VectorAssembler(inputCols=['scaled_num_features_vec',
                                       'indexed_cat_features_vec'],
                            outputCol='final_feature_vector')
        data = assembler.transform(data)
        return data

    def _build_model(self):
        models = {
            "random_forest": RandomForestRegressor(
                featuresCol='final_feature_vector', 
                labelCol='price'
            ),
            "adaboost": GBTRegressor(  # Gradient Boosted Trees as an alternative to AdaBoost
                featuresCol='final_feature_vector',
                labelCol='price',
                maxIter=10,
                maxDepth=5
            ),
            "linear": LinearRegression(  # Using LinearSVR as an alternative to SVR
                featuresCol='final_feature_vector',
                labelCol='price',
                maxIter=100,
                regParam=0.1,  # Regularization parameter
                elasticNetParam=0.8  # Mix between L1 and L2 regularization
            ),
            "xgboost": SparkXGBRegressor(
                features_col='final_feature_vector',
                label_col='price',
                num_workers=1
            ),
        }
        return models[self.model_name]
    
    def _infer_column_types(self, data: DataFrame) -> None:
        # Get DataFrame schema
        dtypes = dict(data.dtypes)
        
        # Define numeric types
        numeric_types = ['int', 'long', 'float', 'double', 'decimal']
        categoric_types = ['string', 'boolean']
        
        # Categorize columns
        for col_name, col_type in dtypes.items():
            # Skip target column
            if col_name == self.target_col:
                continue
                
            # Check if column is numeric
            if any(t in col_type.lower() for t in numeric_types):
                self.numeric_cols.append(col_name)
            elif any(t in col_type.lower() for t in categoric_types):
                # For non-numeric columns, check cardinality
                if data.select(col_name).distinct().count() <= 30:
                    self.categorical_cols.append(col_name)
                else:
                    print(f"Warning: Column '{col_name}' has high cardinality. Consider preprocessing.")
        print(f"Detected numeric columns: {self.numeric_cols}")
        print(f"Detected categorical columns: {self.categorical_cols}")    
    
    @abstractmethod
    def _fill_missing_data(data: DataFrame, imputer):
        pass

    @abstractmethod
    def _feature_engineering(data: DataFrame):
        pass

    @abstractmethod
    def _encode_features(data: DataFrame, encoder):
        pass

    @abstractmethod
    def _scale_features(data: DataFrame, scaler):
        pass


    