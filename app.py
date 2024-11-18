from flask import Flask, render_template_string
import requests
import pandas as pd

app = Flask(__name__)

@app.route('/')
def display_table():
    # Define the URL to fetch data
    site = "https://ibex.bg/%d0%b4%d0%b0%d0%bd%d0%bd%d0%b8-%d0%b7%d0%b0-%d0%bf%d0%b0%d0%b7%d0%b0%d1%80%d0%b0/%d0%bf%d0%b0%d0%b7%d0%b0%d1%80%d0%b5%d0%bd-%d1%81%d0%b5%d0%b3%d0%bc%d0%b5%d0%bd%d1%82-%d0%b4%d0%b5%d0%bd-%d0%bd%d0%b0%d0%bf%d1%80%d0%b5%d0%b4/day-ahead-prices-and-volumes-v2-0/"
    response = requests.get(site, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    if response.status_code == 200:
        # Extract tables from the HTML
        tables = pd.read_html(response.text)

        # Select the desired table (assuming it’s at index 3) and drop unnecessary columns
        df = tables[3].drop(columns=[4, 5, 6], errors='ignore')

        # Convert DataFrame to an HTML table with Bootstrap classes
        table_html = df.to_html(classes='table table-striped table-bordered', index=False)

        # HTML template for rendering
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Table Extraction</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.5.2/css/bootstrap.min.css">
            <style>
                body {{ margin: 20px; }}
                .table-wrapper {{ max-height: 500px; overflow-y: auto; }}
            </style>
        </head>
        <body>
            <h1>Extracted Market Data Table</h1>
            <div class="table-wrapper">
                {table_html}
            </div>
        </body>
        </html>
        """
        return render_template_string(html_template)
    else:
        return f"Failed to retrieve content. Status code: {response.status_code}", 500

if __name__ == "__main__":
    app.run(debug=True)
