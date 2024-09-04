#Packages(Libs) to install if needed
# !pip install gspread
# !pip install oauth2client
# !pip install requests
# !pip install pandas
# !pip install numpy
# !pip install json

import requests
import pandas as pd
from datetime import datetime

# API endpoint and headers
base_url = "https://api.givebutter.com/v1/transactions"  # Replace with the desired request endpoint url 
headers = {
    "accept": "application/json",
    "Authorization": "Bearer API KEY"  # Replace with your actual API key
}

#For use once date parameters can be added
params = {
        'start_date': '2024-07-01',
        'end_date': '2025-06-30'
    }

def fetch_all_data(base_url, headers):   #Fetch all data utlizes pagnation for specific URL can be used on other similar page structures
    all_data = []
    url = base_url  

    while url:
       
        response = requests.get(url, headers=headers, params = params)

        if response.status_code == 200:
            data_json = response.json()

            
            all_data.extend(data_json.get('data', []))

            
            url = data_json.get('links', {}).get('next')
        else:
            print(f"Request failed with status code {response.status_code}")
            break

    return all_data


all_transactions = fetch_all_data(base_url, headers)


donation_data = []
for transaction in all_transactions:
    timestamp_utc = transaction.get('transacted_at')
    if timestamp_utc:
        utc_dt = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00"))
        local_dt = utc_dt.astimezone()
        date_str = local_dt.strftime('%Y-%m-%d')
        time_str = local_dt.strftime('%H:%M:%S')
    else:
        date_str = None
        time_str = None

    donation_data.append({
        'donationAmount': transaction.get('amount'),
        'currencyType': transaction.get('currency'),
        'date': date_str,
        'time': time_str
    })


df1 = pd.DataFrame(donation_data)

# Display the sorted by date rang DataFrame
start_date = '2024-07-01'                                                       #When you wish to change the dates that are storting the data base utalize these two variables start_date/end_date and thats all you need to update it for different dates
end_date = '2025-06-30'
df_date_filter = df1.loc[(df1['date'] >= start_date) & (df1['date'] <= end_date)]

 
df_ts = df_date_filter
donateTotal = df_ts['donationAmount'].sum()
donateGoal = 300000
percentage = (donateTotal / donateGoal) * 100

#Translating pandas dataframe to excel sheet
from google.colab import auth
import gspread
from google.auth import default
from gspread_dataframe import set_with_dataframe

auth.authenticate_user()

creds, _ = default()

gc = gspread.authorize(creds)                                                   #This will have a prompt pop up giving google colab read/write privaleges to your google account that has the desired sheet attached


sh = gc.open("TestGiveButter")                                                  #Opens the slected spreadsheet, in this case the test sheet that i made, this sheet must be interactive in order for the google client to succesffuly write data to it
ws = sh.worksheet("Sheet1")
cell_to_update = 'A1'
ws.update_acell(cell_to_update, percentage)

