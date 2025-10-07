import re

import pandas as pd
from pathlib import Path

from configs.config import load_config

def extract_numbers_only(text):
    """
    Extract only numbers from a string
    Examples:
    - "abc123def456" -> "123456"
    - "Price: $1,234.56" -> "123456"
    - "No numbers here" -> ""
    - "Model 2023 Honda Civic" -> "2023"
    """
    if pd.isna(text) or text == "":
        return ""
    
    # Convert to string and extract all digits
    text = str(text)
    numbers_only = re.sub(r'[^\d]', '', text)
    
    return numbers_only

def clean_id(id):
    id = str(id)
    return extract_numbers_only(id)

def clean_mileage(mileage):
    mileage = str(mileage)
    return extract_numbers_only(mileage)

def split_address(address):
    address = str(address)
    districts = ["Ba Đình", "Cầu Giấy", "Đống Đa", "Hai Bà Trưng", "Hoàn Kiếm", "Thanh Xuân", "Hoàng Mai", "Long Biên", "Hà Đông", "Tây Hồ", "Nam Từ Liêm", "Bắc Từ Liêm"]
    for district in districts:
        if district in address:
            return district
    return address

def transform_data(df):
    df['id'] = df['id'].apply(clean_id)
    df['kilometers'] = df['kilometers'].apply(clean_mileage)
    df['district'] = df['andress'].apply(split_address)
    return df

def run():
    config = load_config()
    data_raw = pd.read_csv(config["data"]["raw"]["overview"])

    data_transformed = transform_data(data_raw)

    data_transformed.to_csv(config["data"]["warehouse"], index=False)
    print(f"Transformed data saved to {config["data"]["warehouse"]}")

if __name__ == "__main__":
    run()