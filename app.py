from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Initialize dictionaries to avoid NameError
sku_to_name = {}
sku_to_id_shopee = {}
sku_to_id_lazada = {}
sku_to_id_tiktok = {}
sku_to_lazada_shop_sku = {}
name_to_sku = {}
id_to_sku = {}
lazada_shop_sku_to_sku = {}
brands = []

try:
    # Load the CSV file
    masterfile = pd.read_csv('masterfile.csv', encoding='ISO-8859-1', dtype=str, on_bad_lines='warn')
    print(masterfile.head())  # Print the first few rows of the CSV file for debugging
    print(masterfile.columns)  # Print the column names for debugging

    # Replace NaN values with 'No data' and convert all columns to strings
    masterfile = masterfile.fillna('No data').astype(str)

    # Check if required columns exist
    required_columns = ['brand_sku', 'item_name', 'product_id_shopee', 'product_id_lazada', 'product_id_tiktok', 'lazada_shopsku', 'brand']
    missing_columns = [col for col in required_columns if col not in masterfile.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in the DataFrame: {', '.join(missing_columns)}")

    # Create mappings from SKU to various fields
    sku_to_name = pd.Series(masterfile.item_name.values, index=masterfile.brand_sku).to_dict()
    sku_to_id_shopee = pd.Series(masterfile.product_id_shopee.values, index=masterfile.brand_sku).to_dict()
    sku_to_id_lazada = pd.Series(masterfile.product_id_lazada.values, index=masterfile.brand_sku).to_dict()
    sku_to_id_tiktok = pd.Series(masterfile.product_id_tiktok.values, index=masterfile.brand_sku).to_dict()
    sku_to_lazada_shop_sku = pd.Series(masterfile.lazada_shopsku.values, index=masterfile.brand_sku).to_dict()

    name_to_sku = pd.Series(masterfile.brand_sku.values, index=masterfile.item_name).to_dict()
    id_to_sku = {**pd.Series(masterfile.brand_sku.values, index=masterfile.product_id_shopee).to_dict(),
                 **pd.Series(masterfile.brand_sku.values, index=masterfile.product_id_lazada).to_dict(),
                 **pd.Series(masterfile.brand_sku.values, index=masterfile.product_id_tiktok).to_dict()}
    lazada_shop_sku_to_sku = pd.Series(masterfile.brand_sku.values, index=masterfile.lazada_shopsku).to_dict()

    # Extract unique brands from Column A
    brands = masterfile['brand'].unique().tolist()
    
    print(sku_to_name)  # Print the dictionary for debugging
    print(name_to_sku)  # Print the reverse dictionary for debugging
except pd.errors.ParserError as e:
    print("Error parsing CSV file:", e)
except UnicodeDecodeError as e:
    print("Encoding error:", e)
except ValueError as e:
    print("Value error:", e)
except Exception as e:
    print("Unexpected error:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    sku_list = ""
    conversion_type = "name"
    marketplace = "Select a market place"
    selected_brand = ""
    result = ""
    comma_result = ""

    if request.method == 'POST':
        sku_list = request.form.get('sku_list', '').strip()
        conversion_type = request.form.get('conversion_type', 'name')
        marketplace = request.form.get('marketplace', 'shopee')
        selected_brand = request.form.get('brand', '')

        if sku_list and selected_brand:
            # Filter SKUs based on selected brand
            filtered_masterfile = masterfile[masterfile['brand'] == selected_brand]
            sku_to_name_filtered = pd.Series(filtered_masterfile.item_name.values, index=filtered_masterfile.brand_sku).to_dict()
            sku_to_id_shopee_filtered = pd.Series(filtered_masterfile.product_id_shopee.values, index=filtered_masterfile.brand_sku).to_dict()
            sku_to_id_lazada_filtered = pd.Series(filtered_masterfile.product_id_lazada.values, index=filtered_masterfile.brand_sku).to_dict()
            sku_to_id_tiktok_filtered = pd.Series(filtered_masterfile.product_id_tiktok.values, index=filtered_masterfile.brand_sku).to_dict()
            sku_to_lazada_shop_sku_filtered = pd.Series(filtered_masterfile.lazada_shopsku.values, index=filtered_masterfile.brand_sku).to_dict()

            name_to_sku_filtered = pd.Series(filtered_masterfile.brand_sku.values, index=filtered_masterfile.item_name).to_dict()
            id_to_sku_filtered = {**pd.Series(filtered_masterfile.brand_sku.values, index=filtered_masterfile.product_id_shopee).to_dict(),
                                 **pd.Series(filtered_masterfile.brand_sku.values, index=filtered_masterfile.product_id_lazada).to_dict(),
                                 **pd.Series(filtered_masterfile.brand_sku.values, index=filtered_masterfile.product_id_tiktok).to_dict()}
            lazada_shop_sku_to_sku_filtered = pd.Series(filtered_masterfile.brand_sku.values, index=filtered_masterfile.lazada_shopsku).to_dict()

            # Normalize line endings to '\n'
            sku_list = sku_list.replace('\r\n', '\n').replace('\r', '\n')
            sku_list_lines = sku_list.split('\n')

            result = []
            for item in sku_list_lines:
                item = item.strip()
                if item:
                    if item in sku_to_name_filtered:
                        sku_code = item
                    elif item in name_to_sku_filtered:
                        sku_code = name_to_sku_filtered[item]
                    elif item in id_to_sku_filtered:
                        sku_code = id_to_sku_filtered[item]
                    elif item in lazada_shop_sku_to_sku_filtered:
                        sku_code = lazada_shop_sku_to_sku_filtered[item]
                    else:
                        sku_code = None
                    
                    if sku_code:
                        if conversion_type == 'name':
                            result.append(sku_to_name_filtered.get(sku_code, 'No data'))
                        elif conversion_type == 'id':
                            if marketplace == 'shopee':
                                result.append(sku_to_id_shopee_filtered.get(sku_code, 'No data'))
                            elif marketplace == 'lazada':
                                if marketplace == 'lazada':  # Ensure 'lazada' marketplace logic is applied
                                    result.append(sku_to_id_lazada_filtered.get(sku_code, 'No data'))
                            elif marketplace == 'tiktok':
                                result.append(sku_to_id_tiktok_filtered.get(sku_code, 'No data'))
                        elif conversion_type == 'shop_sku':
                            if marketplace == 'lazada':  # Ensure 'lazada' marketplace logic is applied
                                result.append(sku_to_lazada_shop_sku_filtered.get(sku_code, 'No data'))
                        elif conversion_type == 'sku_code':
                            result.append(sku_code)
                        else:
                            result.append('Invalid conversion type. Use "name", "id", "shop_sku", or "sku_code".')
                    else:
                        result.append('No data')

            # Join the result using new lines
            result = "\n".join(result)
            # Convert result to comma-separated format
            comma_result = ", ".join(result.splitlines())

    return render_template('index.html', sku_list=sku_list, conversion_type=conversion_type, marketplace=marketplace, selected_brand=selected_brand, result=result, comma_result=comma_result, brands=brands)

if __name__ == '__main__':
    app.run(debug=True)
