from typing import Any, Dict, Optional, Union

from numpy.testing._private.utils import print_assert_equal
from pyspark.sql import DataFrame, functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    StringIndexer, OneHotEncoder, VectorAssembler,
    StandardScaler, Imputer, MinMaxScaler, MaxAbsScaler
)
from pyspark.sql.types import FloatType
import mlflow

from src.ml_pipeline.base_pipeline import BasePredictionPipeline


class CarPricePredictionPipeline(BasePredictionPipeline):
    """
    A complete pipeline for car price prediction with configurable components.
    """
    
    def __init__(
        self,
        target_col: str,
        model_name: str,
        config: Optional[Dict[str, Any]],
        numeric_imputer_strategy: str = "mean",
        categoric_imputer_strategy: str = "mode",
        encoder_type: str = "label",
        scaler_type: str = "standard",
    ):
        super().__init__(target_col, model_name, config)
        self.numeric_imputer_strategy = numeric_imputer_strategy
        self.categoric_imputer_strategy = categoric_imputer_strategy
        self.encoder_type = encoder_type
        self.scaler_type = scaler_type
        
    
    def _fill_missing_data(self, data: DataFrame, num_imputer) -> tuple[DataFrame, Any]:
        """Handle missing values in the data."""
        if num_imputer is not None:
            data_imputed = num_imputer.transform(data)
            return data_imputed, num_imputer
        else:
            i_num = Imputer(strategy=self.numeric_imputer_strategy, inputCols=self.numeric_cols, outputCols=self.numeric_cols)
            num_imputer = i_num.fit(data)
            # Fill all categorical columns with 'Unknown'
            cat_fill_dict = {col: 'Unknown' for col in self.categorical_cols}
            data = data.fillna(cat_fill_dict)
            data_imputed = num_imputer.transform(data)
            return data_imputed, num_imputer
    
    def _feature_engineering(self, data: DataFrame) -> DataFrame:
        """Perform feature engineering."""
        # data = data.withColumn("seat_per_km", data["seats"] / (data["kilometers"] + 1)) \
        #             .withColumn("door_per_km", data["doors"] / (data["kilometers"] + 1)) \
        #             .withColumn("seat_x_door", data["seats"] * data["doors"])
        # data = data.drop("address", "id", "href")
        # Or explicitly specify numerical columns if you know them
        numerical_cols = ['kilometers', 'year']

        for exp in range(2, 4):
            for col in numerical_cols:
                data = data.withColumn(f'{col}_exp_{exp}', F.pow(F.col(col), F.lit(exp)))
                if not self.fitted:
                    self.numeric_cols.append(f'{col}_exp_{exp}')
        print(f"[feature_engineering] Current numeric columns: {self.numeric_cols}")
        return data
    
    def _scale_features(self, data: DataFrame, scaler_pip=None) -> tuple[DataFrame, Any]:
        """Scale numerical features."""
        if scaler_pip is not None:
            return scaler_pip.transform(data), scaler_pip
        else:            
            assembler = VectorAssembler(
                inputCols=self.numeric_cols,
                outputCol="num_features_vec"
            )

            if self.scaler_type == "standard":
                scaler = StandardScaler(
                    inputCol="num_features_vec",
                    outputCol="scaled_num_features_vec",
                    withStd=True,
                    withMean=True
                )
            elif self.scaler_type == "minmax":
                scaler = MinMaxScaler(
                    inputCol="num_features_vec",
                    outputCol="scaled_num_features_vec"
                )
            elif self.scaler_type == "maxabs":
                scaler = MaxAbsScaler(
                    inputCol="num_features_vec",
                    outputCol="scaled_num_features_vec"
                )
            else:
                raise ValueError(f"Unknown scaler type: {self.scaler_type}, should be in ['standard', 'minmax', 'maxabs']")

            scaler_pip = Pipeline(stages=[assembler, scaler])
            scaler_pip = scaler_pip.fit(data)

            return scaler_pip.transform(data), scaler_pip

    def _encode_features(self, data: DataFrame, encoder_pip=None) -> tuple[DataFrame, Any]:
        """Encode categorical features."""
        if encoder_pip is not None:
            return encoder_pip.transform(data), encoder_pip
        elif encoder_pip is None:
            indexer = StringIndexer(
                    inputCols=self.categorical_cols,
                    outputCols=[f"indexed_{col}" for col in self.categorical_cols],
                    handleInvalid="keep"
                )
            assembler = VectorAssembler(
                inputCols=[f"indexed_{col}" for col in self.categorical_cols],
                outputCol="indexed_cat_features_vec"
            )
            if self.encoder_type == "one_hot":
                encoders = [
                    OneHotEncoder(
                        inputCols="cat_features_vec",
                        outputCols="cat_features_vec"
                    )
                ]
                stages = [indexer, encoders, assembler]
            elif self.encoder_type == "label": 
                stages = [indexer, assembler]
            else:
                raise ValueError(f"Unknown encoder type: {self.encoder_type}, should be in ['one_hot', 'label']")
            
            encoder_pip = Pipeline(stages=stages)
            encoder_pip = encoder_pip.fit(data)

            return encoder_pip.transform(data), encoder_pip