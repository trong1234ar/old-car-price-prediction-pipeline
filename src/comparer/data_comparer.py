
import json
import os

class DataComparer:
    def __init__(self):
        self.summary = {}
    
    def compare(self, old, new, id_col):
        old_ids = set(old[id_col])
        new_ids = set(new[id_col])
        
        added_ids = new_ids - old_ids
        removed_ids = old_ids - new_ids
        
        self.summary["added_ids"] = added_ids
        self.summary["removed_ids"] = removed_ids

    def save(self, file_path):
        with open(file_path, "w") as f:
            json.dump(self.summary, f)