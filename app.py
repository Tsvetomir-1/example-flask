from flask import Flask, jsonify
import requests
import pandas as pd
from datetime import datetime

app = Flask(__name__)


# Route for the home page with a helpful message
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the IBEX Market Data API. Use the /prices endpoint to get today's data."
    })


# Route to fetch and return today's market prices for the current hour
@app.route('/prices', methods=['GET'])
def get_prices():
    # Define the URL to fetch data
    site = "https://ibex.bg/%d0%b4%d0%b0%d0%bd%d0%b8-%d0%b7%d0%b0-%d0%bf%d0%b0%d0%b7%d0%b0%d1%80%d0%b0/%d0%bf%d0%b0%d0%b7%d0%b0%d1%80%d0%b5%d0%bd-%d1%81%d0%b5%d0%b3%d0%bc%d0%b5%d0%bd%d1%82-%d0%b4%d0%b5%d0%bd-%d0%bd%d0%b0%d0%bf%d1%80%d0%b5%d0%b4/day-ahead-prices-and-volumes-v2-0/"
    response = requests.get(site, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    if response.status_code == 200:
        # Extract tables from the HTML
        try:
            tables = pd.read_html(response.text)
            df = tables[3].copy()  # Select the table containing the relevant data
        except (ValueError, IndexError):
            return jsonify({"error": "The expected table was not found on the webpage."}), 500

        # Rename columns for consistency
        df.columns = [col.lower().replace(" ", "_") for col in df.columns]

        # Ensure 'date' and 'time' columns exist and process them
        if 'date' in df.columns and 'time' in df.columns:
            # Convert 'date' to datetime.date
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.date  # Convert to datetime.date

            # Convert 'time' to datetime.time
            df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S',
                                        errors='coerce').dt.time  # Convert to datetime.time
        else:
            return jsonify({"error": "The 'date' or 'time' column was not found in the table."}), 500

        # Get the current date and time
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        current_hour = current_datetime.hour
        current_minute = current_datetime.minute

        # Format the current time to match the table's time format (e.g., "00:24:00")
        current_time = current_datetime.strftime("%H:%M:%S")

        # Print the current time and all available times to debug
        print(f"Current time: {current_time}")
        print(f"Available times: {df['time'].unique()}")

        # Filter rows that match the current date and current hour (using just the hour for flexibility)
        df_filtered = df[(df['date'] == current_date) & (df['time'].apply(lambda x: x.hour) == current_hour)]

        # Print the filtered data for debugging
        print(f"Filtered data: {df_filtered}")

        if not df_filtered.empty:
            # Convert the filtered data to a dictionary and return it
            data = df_filtered.to_dict(orient='records')
            return jsonify({
                "date": str(current_date),
                "time": current_time,
                "price": data[0]['price'],
                "price_eur": data[0]['price_eur'],
                "volume": data[0]['volume']
            })
        else:
            return jsonify({"message": "No data available for the current time."}), 404

    else:
        # Return an error message if the request failed
        return jsonify({"error": f"Failed to retrieve content. Status code: {response.status_code}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
