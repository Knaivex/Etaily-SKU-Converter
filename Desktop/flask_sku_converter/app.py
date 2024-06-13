from flask import Flask, request, render_template
import pandas as pd

app = Flask(__name__)

masterfile = pd.read_csv('masterfile.csv')
sku_to_name = pd.Series(masterfile.product_name.values, index=masterfile.sku_code).to_dict()
sku_to_id = pd.Series(masterfile.product_id.values, index=masterfile.sku_code).to_dict()

@app.route('/', methods=['GET', 'POST'])
def index():
    sku_list = ""
    conversion_type = "name"
    result = ""

    if request.method == 'POST':
        sku_list = request.form.get('sku_list', '').strip()
        conversion_type = request.form.get('conversion_type', 'name')
        if sku_list:
            sku_list = sku_list.split('\n')[:3000]  # Limit to 3000 SKUs
            if conversion_type == 'name':
                result = [sku_to_name.get(sku.strip(), 'Unknown SKU') for sku in sku_list if sku.strip()]
            elif conversion_type == 'id':
                result = [str(sku_to_id.get(sku.strip(), 'Unknown SKU')) for sku in sku_list if sku.strip()]
            else:
                result = 'Invalid conversion type. Use "name" or "id".'
            result = "\n".join(result)  # Join the result using new lines

    return render_template('index.html', sku_list=sku_list, conversion_type=conversion_type, result=result)

if __name__ == '__main__':
    app.run(debug=True)