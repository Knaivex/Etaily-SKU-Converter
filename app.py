from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

# Initialize dictionaries to avoid NameError
sku_to_name = {}
sku_to_id_shopee = {}
sku_to_id_lazada = {}
sku_to_id_tiktok = {}
sku_to_shop_sku = {}
name_to_sku = {}
id_to_sku = {}
shop_sku_to_sku = {}

try:
    masterfile = pd.read_csv('masterfile.csv', encoding='utf-8')
    print(masterfile.head())  # Print the first few rows of the CSV for debugging

    # Convert all values to strings and handle NaNs
    masterfile['product_name'] = masterfile['product_name'].astype(str).fillna('Unknown SKU')
    masterfile['product_id_shopee'] = masterfile['product_id_shopee'].astype(str).fillna('Unknown SKU')
    masterfile['product_id_lazada'] = masterfile['product_id_lazada'].astype(str).fillna('Unknown SKU')
    masterfile['product_id_tiktok'] = masterfile['product_id_tiktok'].astype(str).fillna('Unknown SKU')
    masterfile['shop_sku'] = masterfile['shop_sku'].astype(str).fillna('Unknown SKU')

    sku_to_name = pd.Series(masterfile.product_name.values, index=masterfile.sku_code).to_dict()
    sku_to_id_shopee = pd.Series(masterfile.product_id_shopee.values, index=masterfile.sku_code).to_dict()
    sku_to_id_lazada = pd.Series(masterfile.product_id_lazada.values, index=masterfile.sku_code).to_dict()
    sku_to_id_tiktok = pd.Series(masterfile.product_id_tiktok.values, index=masterfile.sku_code).to_dict()
    sku_to_shop_sku = pd.Series(masterfile.shop_sku.values, index=masterfile.sku_code).to_dict()

    name_to_sku = pd.Series(masterfile.sku_code.values, index=masterfile.product_name).to_dict()
    id_to_sku = {**pd.Series(masterfile.sku_code.values, index=masterfile.product_id_shopee).to_dict(),
                 **pd.Series(masterfile.sku_code.values, index=masterfile.product_id_lazada).to_dict(),
                 **pd.Series(masterfile.sku_code.values, index=masterfile.product_id_tiktok).to_dict()}
    shop_sku_to_sku = pd.Series(masterfile.sku_code.values, index=masterfile.shop_sku).to_dict()

    print(sku_to_name)  # Print the dictionary for debugging
    print(name_to_sku)  # Print the reverse dictionary for debugging
except pd.errors.ParserError as e:
    print("Error parsing CSV file:", e)
except UnicodeDecodeError as e:
    print("Encoding error:", e)
except Exception as e:
    print("Unexpected error:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    sku_list = ""
    conversion_type = "name"
    marketplace = "shopee"
    result = ""
    comma_result = ""

    if request.method == 'POST':
        sku_list = request.form.get('sku_list', '').strip()
        conversion_type = request.form.get('conversion_type', 'name')
        marketplace = request.form.get('marketplace', 'shopee')
        
        if sku_list:
            # Normalize line endings to '\n'
            sku_list = sku_list.replace('\r\n', '\n').replace('\r', '\n')
            sku_list_lines = sku_list.split('\n')

            result = []
            for item in sku_list_lines:
                item = item.strip()
                if item:
                    if item in sku_to_name:
                        sku_code = item
                    elif item in name_to_sku:
                        sku_code = name_to_sku[item]
                    elif item in id_to_sku:
                        sku_code = id_to_sku[item]
                    elif item in shop_sku_to_sku:
                        sku_code = shop_sku_to_sku[item]
                    else:
                        sku_code = None
                    
                    if sku_code:
                        if conversion_type == 'name':
                            result.append(sku_to_name.get(sku_code, 'Unknown SKU'))
                        elif conversion_type == 'id':
                            if marketplace == 'shopee':
                                result.append(sku_to_id_shopee.get(sku_code, 'Unknown SKU'))
                            elif marketplace == 'lazada':
                                result.append(sku_to_id_lazada.get(sku_code, 'Unknown SKU'))
                            elif marketplace == 'tiktok':
                                result.append(sku_to_id_tiktok.get(sku_code, 'Unknown SKU'))
                        elif conversion_type == 'shop_sku':
                            result.append(sku_to_shop_sku.get(sku_code, 'Unknown SKU'))
                        elif conversion_type == 'sku_code':
                            result.append(sku_code)
                        else:
                            result.append('Invalid conversion type. Use "name", "id", "shop_sku", or "sku_code".')
                    else:
                        result.append('Unknown SKU')

            # Join the result using new lines
            result = "\n".join(result)
            # Convert result to comma-separated format
            comma_result = ", ".join(result.splitlines())

    return render_template('index.html', sku_list=sku_list, conversion_type=conversion_type, marketplace=marketplace, result=result, comma_result=comma_result)

if __name__ == '__main__':
    app.run(debug=True)
