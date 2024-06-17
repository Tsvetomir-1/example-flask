from flask import Flask
import requests
import re
import pandas as pd
from io import StringIO

app = Flask(__name__)

@app.route('/')
def hello_world():
    site = "https://ibex.bg/%d0%b4%d0%b0%d0%bd%d0%bd%d0%b8-%d0%b7%d0%b0-%d0%bf%d0%b0%d0%b7%d0%b0%d1%80%d0%b0/%d0%bf%d0%b0%d0%b7%d0%b0%d1%80%d0%b5%d0%bd-%d1%81%d0%b5%d0%b3%d0%bc%d0%b5%d0%bd%d1%82-%d0%b4%d0%b5%d0%bd-%d0%bd%d0%b0%d0%bf%d1%80%d0%b5%d0%b4/day-ahead-prices-and-volumes-v2-0/"
    request = requests.get(site, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    if request.status_code == 200:

        pattern = r"date_default_timezone_set:.*?<tbody>.*?</tbody>"

        match = re.search(pattern, request.text, re.DOTALL)

        if match:
            specific_line = match.group()
            dfs = pd.read_html(StringIO(request.text))
            df = dfs[3].drop([4, 5, 6])
            print(df)
        else:
            print("No matching line found.")
    else:
        print(f"Failed to retrieve the content. Status code: {request.status_code}")
    return df.to_string()


if __name__ == "__main__":
    app.run()
