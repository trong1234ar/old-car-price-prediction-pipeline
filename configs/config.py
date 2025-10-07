import yaml
from datetime import datetime as dt
import os

def _create_directories_for_paths(config_dict):
    """Recursively create directories for all local file paths in the config dictionary"""
    for key, value in config_dict.items():
        if isinstance(value, dict):
            _create_directories_for_paths(value)
        elif isinstance(value, str):
            # Skip URLs and web paths
            if value.startswith(('http://', 'https://', 'ftp://')):
                continue
            
            # Skip paths that start with '/' (absolute Unix paths that might be web paths)
            if value.startswith('/') and len(value) > 1 and not value.startswith('//'):
                continue
                
            # Check if it looks like a local file path
            if ('.' in value or '/' in value or '\\' in value):
                # Get directory part
                dir_path = os.path.dirname(value)
                
                # Only create if:
                # 1. There's a directory part (not just a filename)
                # 2. It's not a URL or web path
                # 3. It contains typical file path patterns
                if (dir_path and 
                    not dir_path.startswith(('http://', 'https://', 'ftp://')) and
                    ('.' in dir_path or '/' in dir_path or '\\' in dir_path)):
                    os.makedirs(dir_path, exist_ok=True)

def load_config() -> dict:
    """Simple function to read YAML and return dictionary"""
    with open("./configs/config.yaml", 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        
        # Automatically create directories for all file paths in config
        _create_directories_for_paths(config)
        
        if not config['TODAY']:
            today = dt.now().date()
            config['TODAY'] = today
        return config
