import time

from sklearn.metrics import (
    mean_absolute_error, 
    mean_squared_error, 
    mean_absolute_percentage_error,
    r2_score, 
)
import numpy as np
import json

class ModelComparer:
    def __init__(self):
        self.summary = {}
    
    def compare(self, prod_model, staging_model, X_test, y_test):

        prod_preds, prod_time = self._get_predict(prod_model, X_test)
        staging_preds, staging_time = self._get_predict(staging_model, X_test)
        
        self.summary['metrics'] = self._compare_metric(prod_preds, staging_preds, y_test)
        self.summary['time_complexity'] = self._compare_time_complexity(prod_time, staging_time, 0.1)

        if self.summary['metrics'] and self.summary['time_complexity']:
            return True
        return False
        
    def _get_predict(self, model, X_test):
        start_time = time.time()
        pred = model.predict(X_test)
        end_time = time.time()
        return pred, end_time - start_time
    
    def _compare_metric(self, prod_preds, staging_preds, y_test):
        prod_metrics = {}
        prod_metrics["mse"] = float(mean_squared_error(y_test, prod_preds))
        prod_metrics["rmse"] = float(np.sqrt(mean_squared_error(y_test, prod_preds)))
        prod_metrics["mae"] = float(mean_absolute_error(y_test, prod_preds))
        prod_metrics["mape"] = float(mean_absolute_percentage_error(y_test, prod_preds))
        prod_metrics["r2"] = float(r2_score(y_test, prod_preds))

        staging_metrics = {}
        staging_metrics["mse"] = float(mean_squared_error(y_test, staging_preds))
        staging_metrics["rmse"] = float(np.sqrt(mean_squared_error(y_test, staging_preds)))
        staging_metrics["mae"] = float(mean_absolute_error(y_test, staging_preds))
        staging_metrics["mape"] = float(mean_absolute_percentage_error(y_test, staging_preds))
        staging_metrics["r2"] = float(r2_score(y_test, staging_preds))

        for metric in prod_metrics:
            if metric not in ["r2"]:
                if prod_metrics[metric] < staging_metrics[metric]:
                    return False
            else:
                if prod_metrics[metric] > staging_metrics[metric]:
                    return False
        return True

    def _compare_time_complexity(self, prod_time, staging_time, th):
        return True if prod_time > staging_time + staging_time * th else False

    def save(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.summary, f)