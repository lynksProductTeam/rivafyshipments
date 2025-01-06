import streamlit as st
import requests
import pandas as pd
import io
from datetime import datetime, timedelta

# Streamlit app
st.title("Invoices and Shipments List from Lynks")

# Password Authentication
st.sidebar.header("Login")
password = st.sidebar.text_input("Enter Password", type="password")
if password != "RivaInvoice@GX24":  # Replace 'your_password' with your actual password
    st.sidebar.warning("Please enter a valid password to proceed.")
    st.stop()

# Main Application
st.header("Fetch the data")

today = datetime.today()
yesterday = today - timedelta(days=1)

# Input fields
date = st.date_input("Select Date", value=yesterday)
option = st.selectbox("Select Operation", ["Invoices", "Shipments"])
submit = st.button("Submit")
# print("New Search Start")

if submit:
    try:
        # API call 1: Authenticate
        client_id = '4cq23g85641nhdacn0cdvvig50'  # Replace with actual secret management
        client_secret = 'guqmunen3j92f1abg3vamst8ulhm4tji1ltl107n46m8psrs5ie'
        
        auth_url = f"https://api.buyogo.com/api/oauth2/token/60?client_id=QyO226WrkXLc9zlCkcYWMMAj8QZGfIq5&client_secret=dXeU8FNiYp1orXJ1J58eQ1gClCm6fqwBhHBsiDJ3eDVn2VVYJmAcZNVSyb4BskwV"
        auth_response = requests.get(auth_url)
        print(auth_response)
        if auth_response.status_code != 200:
            st.error("Authentication failed. Please check your credentials.")
            st.stop()
        
        access_token = auth_response.json().get("access_token")
        if not access_token:
            st.error("Unable to retrieve access token.")
            st.stop()

        # API call 2: Fetch data
        operation_type = "INVOICE_UPDATE" if option == "Invoices" else "SHIPMENT_CREATION"
        formatted_date = date.strftime("%Y-%m-%dT00:00:00Z")
        data_url = f"https://api.buyogo.com/integrators-operations?operationType={operation_type}&date={formatted_date}&size=100&page=0"
        print(data_url)
        
        headers = {"Authorization": f"Bearer {access_token}"}

        # Initial request
        data_response = requests.get(data_url, headers=headers)
        data_response.raise_for_status()
        data = []

        while True:
            # Parse current response
            response_json = data_response.json()
            content = response_json.get("content", [])
            data.extend(content)
            # print(content)

            # Check if it's the last page
            if response_json.get("last", True):
                break

            # Get the next page URL and fetch it
            current_page = response_json.get("pageNo")
            print(current_page)
            next_pageNo = current_page+1
            print(next_pageNo)
            next_page_url = f"https://api.buyogo.com/integrators-operations?operationType={operation_type}&date={formatted_date}&size=100&page={next_pageNo}"
            print(next_page_url)
            if not next_page_url:
                break
            
            data_response = requests.get(next_page_url, headers=headers)

            data_response.raise_for_status()
            # print(data_response)
    # Convert aggregated data to a DataFrame
        if data:
            df = pd.DataFrame(data, columns=[
                "incomingFileName",
                "mailSubject",
                "processState"
                ])

            # Display table in Streamlit
            st.table(df)

            # Create an in-memory buffer to store the Excel file
            buffer = io.BytesIO()

            # Use pandas ExcelWriter to write DataFrame to Excel
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)

            # Rewind the buffer
            buffer.seek(0)

            # Provide download button for the Excel file
            st.download_button(
                label="Download data as Excel",
                data=buffer,
                file_name='output.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        else:
            st.warning("No data available for the selected criteria.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
