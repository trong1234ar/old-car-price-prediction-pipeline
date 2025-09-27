# import pandas as pd
# from pathlib import Path
# import re

# def convert_price(price_str):
#     """
#     Convert Vietnamese price format to integer (in millions VND)
#     Examples:
#     - "1 Tỷ 24 Triệu" -> 1024
#     - "928 Triệu" -> 928
#     - "2 Tỷ" -> 2000
#     - "500 Triệu" -> 500
#     """
#     if pd.isna(price_str) or price_str == "":
#         return 0
#     # Convert to string and normalize
#     price_str = str(price_str).strip()
#     # Initialize result
#     price = 0
#     # Extract billions (Tỷ)
#     billion_match = re.search(r'(\d+)\s*[Tt]ỷ', price_str)
#     if billion_match:
#         billions = int(billion_match.group(1))
#         price += billions * 1_000_000_000
#     # Extract millions (Triệu)
#     million_match = re.search(r'(\d+)\s*[Tt]riệu', price_str)
#     if million_match:
#         millions = int(million_match.group(1))
#         price += millions * 1_000_000
    
#     # If no Tỷ or Triệu found, try to extract just numbers
#     if price == 0:
#             raise ValueError(f"Cannot convert price: {price_str}")
#     return int(price)

# def extract_numbers_only(text):
#     """
#     Extract only numbers from a string
#     Examples:
#     - "abc123def456" -> "123456"
#     - "Price: $1,234.56" -> "123456"
#     - "No numbers here" -> ""
#     - "Model 2023 Honda Civic" -> "2023"
#     """
#     if pd.isna(text) or text == "":
#         return ""
    
#     # Convert to string and extract all digits
#     text = str(text)
#     numbers_only = re.sub(r'[^\d]', '', text)
    
#     return numbers_only


# def run():
#     config = {
#         "raw_dir": r"C:\Study\Personal\Project\old-car-price-prediction-pipeline",
#         "raw": {
#             "train": "data/raw/train.csv",
#             "test": "data/raw/test.csv"
#         },
#         "temp": {
#             "train": "data/temp/train.csv",
#             "test": "data/temp/test.csv"
#         }
#     }

#     # raw_train = pd.read_csv(config["raw_dir"] / config["raw"]["train"])
#     # raw_test = pd.read_csv(config["raw_dir"] / config["raw"]["test"])

#     temp_train = pd.read_csv(Path(config["raw_dir"]) / config["temp"]["train"])
#     temp_test = pd.read_csv(Path(config["raw_dir"]) / config["temp"]["test"])
#     temp = pd.concat([temp_train, temp_test])
#     temp.to_csv(Path(config["raw_dir"]) / "data/data warehouse/data.csv", index=False)
#     # processed_train.to_csv(config["raw_dir"] / config["processed"]["train"], index=False)
#     # processed_test.to_csv(config["raw_dir"] / config["processed"]["test"], index=False)

#     # print(f"[transform] Wrote {len(temp_train)} rows -> {config['raw_dir'] /  "data/data warehouse/data.csv"}")
#     # print(f"[transform] Wrote {len(temp_test)} rows -> {config['raw_dir'] /  "data/data warehouse/data.csv"}")

# if __name__ == "__main__":
#     run()