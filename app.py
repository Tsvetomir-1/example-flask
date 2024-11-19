from flask import Flask, Response
import requests
import pandas as pd
import pytz
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_prices():
    # Define the URL to fetch data
    site = "https://ibex.bg/%d0%b4%d0%b0%d0%bd%d0%b8-%d0%b7%d0%b0-%d0%bf%d0%b0%d0%b7%d0%b0%d1%80%d0%b0/%d0%bf%d0%b0%d0%b7%d0%b0%d1%80%d0%b5%d0%bd-%d1%81%d0%b5%d0%b3%d0%bc%d0%b5%d0%bd%d1%82-%d0%b4%d0%b5%d0%bd%d0%bd%d0%b0%d0%bf%d1%80%d0%b5%d0%b4/day-ahead-prices-and-volumes-v2-0/"
    response = requests.get(site, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    if response.status_code == 200:
        try:
            tables = pd.read_html(response.text)
            df = tables[3].copy()  # Select the table containing the relevant data
        except (ValueError, IndexError):
            return Response("Error: The expected table was not found on the webpage.", status=500)

        # Rename columns for consistency
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]

        # Ensure 'date' and 'time' columns exist and process them
        if 'date' in df.columns and 'time' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date
            df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce').dt.time
        else:
            return Response("Error: The 'date' or 'time' column was not found in the table.", status=500)

        # Get the current date and time in UTC+2
        local_tz = pytz.timezone('Europe/Sofia')  # Define the desired time zone (e.g., UTC+2)
        current_datetime_utc = datetime.now(pytz.utc)  # Current time in UTC
        current_datetime_local = current_datetime_utc.astimezone(local_tz)  # Convert to local time zone

        # Extract the current local date and hour
        current_date = current_datetime_local.date()
        current_hour = current_datetime_local.hour

        # Convert current date to the desired format DD/MM/YYYY
        formatted_date = current_datetime_local.strftime('%d/%m/%Y')

        # Filter rows that match the current date and current hour (using just the hour for flexibility)
        df_filtered = df[(df['date'] == current_date) & (df['time'].apply(lambda x: x.hour) == current_hour)]

        if not df_filtered.empty:
            data = df_filtered.to_dict(orient='records')[0]
            # Format the response as plain text
            return Response(
                f"Date:  {formatted_date}\n"  # Use the formatted date
                f"Time:  {current_datetime_local.strftime('%H:%M:%S')}\n"
                f"Price  (BGN): {data['price']}\n"
                f"Price  (EUR): {data['price_eur']}\n"
                f"Volume (MWh): {data['volume']}",
                mimetype="text/plain"
            )
        else:
            return Response("No data available for the current time.", status=404, mimetype="text/plain")

    else:
        return Response(f"Error: Failed to retrieve content. Status code: {response.status_code}", status=500, mimetype="text/plain")


if __name__ == "__main__":
    app.run(debug=True)
