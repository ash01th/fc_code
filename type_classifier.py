import json
import os
import google.generativeai as genai

# --- Configuration ---
# It's best practice to set your API key as an environment variable.
# On your system, you would run: export GOOGLE_API_KEY="YOUR_API_KEY"
try:
    # Replace "YOUR_GOOGLE_AI_API_KEY" with your actual key if not using environment variables.
    # IMPORTANT: Do not share code publicly with your API key hardcoded.
    
    # Using a placeholder for security. Replace with your actual key or environment variable.
    # genai.configure(api_key="YOUR_GOOGLE_AI_API_KEY") 
    genai.configure(api_key="AIzaSyBByzleYpR-poWl5gnyHyRxOyg74FOCjx0")

except (KeyError, TypeError):
    print("API Key not found. Please set the GOOGLE_API_KEY environment variable.")
    exit()

def extract_product_names(file_path):
    """
    Reads a JSON file containing a list of product dictionaries
    and extracts all values from the 'product_name' key.
    This function is reused from your original script.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Use list comprehension to extract product names and store in a list
            product_names = [product['product_name'] for product in data]
            return product_names
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: The file at {file_path} is not a valid JSON file.")
        return []
    except KeyError:
        print(f"Error: A dictionary in {file_path} is missing the 'product_name' key.")
        return []
    except TypeError:
        print(f"Error: The JSON file at {file_path} does not contain a list of objects as expected.")
        return []

def classify_products(product_list: list[str]) -> dict:
    """
    Uses the Gemini LLM to classify a list of product names into predefined categories.
    """
    # Using a standard and effective model for this task.
    # Updated to a more recent model, but you can change it back if needed.
    model = genai.GenerativeModel('gemini-2.5-pro') 

    formatted_product_list = "\n".join(f"- {name}" for name in product_list)

    # This prompt is specifically designed for classification.
    # It defines the categories and the exact JSON structure required for the output.
    prompt = f"""
    You are an expert product classification assistant. Your task is to classify each product title from the list below into one of four categories.

    **Categories:**
    - "regular bread": Standard white, wheat, or basic sandwich bread.
    - "healthy bread": Includes multi-grain, whole wheat, rye, sourdough, low-carb, or keto bread.
    - "special bread": Artisanal bread, brioche, challah, focaccia, gluten-free, or bread with special ingredients like cheese, olives, or fruit.
    - "misc": Use this for items that are not bread or if the type is completely unclear (e.g., bread crumbs, croutons).

    **Output Rules (Strictly Follow):**
    1.  Return ONLY a valid JSON object. No other text, comments, or markdown.
    2.  The JSON object must have a single top-level key named "products".
    3.  The value for "products" must be a list of JSON objects.
    4.  Each object in the list must have exactly two keys:
        - "product_name": The original, unmodified product name from the input.
        - "type": The classification string (e.g., "healthy bread").
    5.  The order of products in the output list MUST match the order in the input list.

    **Product Titles to Classify:**
    {formatted_product_list}
    """

    try:
        # Calling the LLM API
        response = model.generate_content(prompt)
        
        # Clean and Parse the JSON Output
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        # Convert the JSON string into a Python dictionary
        result_json = json.loads(cleaned_response)
        
        return result_json

    except Exception as e:
        print(f"An error occurred during LLM classification: {e}")
        # Return an empty dict to signal failure
        return {}

# --- Main Execution ---
if __name__ == "__main__":
    # A list to store all classified product dictionaries from all files
    all_classified_products = []
    input_directory = "cleaned_data"
    output_file = "classified_bread_products.json"

    # Check if the input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Input directory '{input_directory}' not found.")
        print("Please create it and place your JSON files inside.")
        exit()

    # Loop through each file in the specified directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            json_file_path = os.path.join(input_directory, filename)
            print(f"\n--- Processing file: {filename} ---")
            
            # --- NEW: Extract platform name from the filename ---
            # This splits the filename by '_' and takes the first part.
            # Example: "amazon_bread.json" -> "amazon"
            platform_name = filename.split('_')[0]
            print(f"Detected platform: {platform_name}")

            names_list = extract_product_names(json_file_path)
            
            if names_list:
                print(f"Successfully extracted {len(names_list)} product names.")
                
                # Get the classification from the LLM
                classified_data = classify_products(names_list)
                
                if classified_data and 'products' in classified_data and isinstance(classified_data['products'], list):
                    print(f"Successfully classified {len(classified_data['products'])} products.")
                    
                    # --- MODIFIED: Add platform to each product record ---
                    # Loop through each product dict in the returned list
                    for product in classified_data['products']:
                        # Add the new 'platform' key-value pair
                        product['platform'] = platform_name

                    # Add the now-modified list of classified products to our master list
                    all_classified_products.extend(classified_data['products'])
                else:
                    print(f"Failed to classify products for {filename}.")
    
    # After processing all files, save the combined results to a new JSON file
    if all_classified_products:
        print(f"\n--- All files processed. Saving {len(all_classified_products)} items to output file. ---")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_classified_products, f, indent=4)
            print(f"Successfully saved all classified products to '{output_file}'")
        except Exception as e:
            print(f"Error saving to file: {e}")
    else:
        print("\nNo products were classified. The output file was not created.")