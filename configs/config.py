import yaml
from datetime import datetime as dt
import os

def load_config() -> dict:
    """Simple function to read YAML and return dictionary"""
    with open("./configs/config.yaml", 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        # Create directories for file paths (not the files themselves)
        os.makedirs(os.path.dirname(config["data"]["raw"]["overview"]), exist_ok=True)
        os.makedirs(os.path.dirname(config["data"]["raw"]["detail"]), exist_ok=True)
        os.makedirs(os.path.dirname(config["data"]["warehouse"]), exist_ok=True)
        os.makedirs(os.path.dirname(config["comparer"]["summary"]), exist_ok=True)
        if not config['TODAY']:
            today = dt.now().date()
            config['TODAY'] = today
        return config
