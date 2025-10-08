import json
import os

def clean_prices(input_filepath):
    """
    Reads a JSON file and cleans 'price' field by removing rupee symbol and newline char , 
    in case of multiple numbers(disconunts) pick the first price on the screen
    and  convert the final number from string to a float.
    """
    try:
        with open("data/"+input_filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)

        #iterate through each dict in the file
        for item in data:
            price_str = item['price']
            
            #remove the rupee symbol ('\u20b9') and comma
            #replace newline characters ('\n') with a space to ensure numbers are separated
            no_symbols = price_str.replace('\u20b9', '').replace(',', '')
            cleaned_str = no_symbols.replace('\n', ' ')
            
            #split the string by whitespace to get a list of number strings.
            price_parts = cleaned_str.strip().split()
            
            #take the first number
            if price_parts:
                first_price_str = price_parts[0]
            #convert the first number string to a float and update the dictionary.
                item['price'] = float(first_price_str)
            else:
                item['price'] = None
        #create output directory if it doesn't exist
        output_dir ="cleaned_data"
        os.makedirs(output_dir, exist_ok=True)
        #if no errors save cleaned data to a new file
        with open("cleaned_data/"+input_filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            print("\nCleaned data has been saved to cleaned_data/"+input_filepath)   
        return data

    except FileNotFoundError:
        print(f"Error: File not found at {input_filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_filepath}. Check the file format.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    input_files =os.listdir('data') 
    print(input_files)
    for file in input_files:
        cleaned_data = clean_prices(file)