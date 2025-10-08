import json
import pandas as pd
brands_json_path="brands.json"
type_data_path="classified_bread_products.json"
brands_list=[]
try:
    with open(brands_json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        brands_list=data["brands"]
except Exception as e:
    print(e)

try:
    with open(type_data_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for record in data:
            for brand in brands_list:
                if brand in record["product_name"]:
                    record["brand"]=brand
                    break
        df=pd.DataFrame(data)
except Exception as e:
    print(e)

print(df.head())
