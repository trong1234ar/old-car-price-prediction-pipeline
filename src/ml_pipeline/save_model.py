# from __future__ import annotations
# import pickle
# from pathlib import Path
# import mlflow
# import mlflow.sklearn

# from ..scripts.utils import get_configs, get_mlflow_paths, get_data_paths


# def run():
#     cfg = get_configs()
#     tracking_uri, _, registered_model_name = get_mlflow_paths(cfg)
#     mlflow.set_tracking_uri(tracking_uri)

#     model_uri = f"models:/{registered_model_name}/latest"
#     model = mlflow.sklearn.load_model(model_uri)

#     out_path = get_data_paths()["local_model"]
#     out_path.parent.mkdir(parents=True, exist_ok=True)
#     with open(out_path, "wb") as f:
#         pickle.dump(model, f)
#     print(f"[save_model] Saved model -> {out_path}")


# if __name__ == "__main__":
#     run()
