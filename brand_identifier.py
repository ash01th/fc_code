import json
import os
import google.generativeai as genai

#initial config of ai model 
try:
    genai.configure(api_key="AIzaSyBByzleYpR-poWl5gnyHyRxOyg74FOCjx0")
except KeyError:
    print("API Key not found.")
    exit()

def extract_product_names(file_path):
    """
    Reads a JSON file containing a list of product dictionaries
    and extracts all values from the 'product_name' key.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            #use list comprehension to extract product names and store in list
            product_names = [product['product_name'] for product in data]
            return product_names
            
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file at {file_path} is not a valid JSON file.")
        return []
    except KeyError:
        print("Error: A dictionary in the JSON file is missing the 'product_name' key.")
        return []
    except TypeError:
        print("Error: The JSON file does not contain a list of objects as expected.")
        return []




def get_brands(product_list):
    """
    Use llm to get brand name from scraped data
    """
    
    model = genai.GenerativeModel('gemini-2.5-pro')

    
    formatted_product_list = "\n".join(f"- {name}" for name in product_list)

    #defining prompt
    prompt = f"""
    You are an expert data extraction assistant. Your task is to identify and extract the brand name from the following list of product titles.

    Follow these rules strictly:
    1.  Return ONLY a valid JSON object.
    2.  The JSON object must have a single key named "brands".
    3.  The value for the "brands" key must be a list of strings.
    4.  The order of brands in the list must correspond to the order of the product titles in the input.
    5.  If you cannot identify a brand for a product, use the string "N/A" for that item in the list.
    6.  Do not include any explanations, comments, or any text outside of the JSON object.

    Product Titles:
    {formatted_product_list}
    """

    try:
        #Calling LLM api
        response = model.generate_content(prompt)
        print("Raw response from the model:") 
        print(response.text)  #model repsonse
        #clean and Parse the json Output
        #the model sometimes wraps the json in markdown backticks (```json ... ```)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        #convert the json string into a python dictionary
        result_json = json.loads(cleaned_response)
        
        return result_json

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}
#final set containing all unique brands
brands_masterlist=set()

#reading all product names from cleaned data and extracting brand names
for file in os.listdir("cleaned_data"):
    json_file = 'cleaned_data/'+file
    names_list = extract_product_names(json_file)
    if names_list:
        print("Successfully extracted product names:")
        extracted_data = get_brands(names_list)
        if extracted_data and 'brands' in extracted_data:
            print("\n--- Successfully Extracted Brands ---")
            temp=json.dumps(extracted_data, indent=4)
            brands_dict = json.loads(temp)
            brands_masterlist.update(brands_dict["brands"])
        else:
             print("Failed to extract brand information.")
print(list(brands_masterlist))
brand_dict={"brands":list(brands_masterlist)}
try:
    with open("brands.json", 'w', encoding='utf-8') as f:
        json.dump(brand_dict, f, indent=4)
    print("Successfully saved the data to 'brands.json'")

except Exception as e:
    print(f"An error occurred while saving the file: {e}")

