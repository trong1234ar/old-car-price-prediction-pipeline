from ast import List
import json
import os


class DataComparer:
    def __init__(self):
        self.summary = {}
    
    def compare(self, old, new):
        old = set(old)
        new = set(new)
        
        intersection = old & new  # Items in both old and new
        only_in_old = old - new   # Items only in old (removed)
        only_in_new = new - old   # Items only in new (added)
        
        self.summary["intersection"] = intersection
        self.summary["created"] = only_in_new
        self.summary["deleted"] = only_in_old

        return self.summary

    def save(self, file_path):
        
        for k, v in self.summary.items():
            self.summary[k] = list(v)
            
        with open(file_path, "w") as f:
            json.dump(self.summary, f)