# Interactive Sales Analytics Dashboard

A Python dashboard built with Plotly Dash for exploring sales and customer
feedback. It uses a synthetic sample dataset by default; if you add your own
`cleaned_customer_sales_data.csv` beside `app.py`, the dashboard uses that file
instead.

## Run locally

Use Python 3.9 or newer. From this folder, install the dependencies and start
the app:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:8050](http://127.0.0.1:8050) in a browser.

## Dashboard controls and charts

- Filter by purchase date, city, and gender; use **Reset filters** to restore
  the full view.
- Review total purchase value, sales records, average purchase, and average
  feedback.
- Explore monthly purchase value, purchase value by city, sales-record mix by
  gender, and feedback-score distribution.
- Charts support hover details and Plotly interactions.

Purchase values are shown in INR. The dashboard counts dataset rows as sales
records; it does not assume each row represents a distinct customer or order.
The bundled sample contains synthetic data only.

## Using your own data

The local file `cleaned_customer_sales_data.csv` takes precedence over the demo
dataset. It must include `Customer_ID`, `Gender`, `City`, `Last_Purchase_Date`,
`Purchase_Amount`, and `Feedback_Score` columns. Keep private or personal
customer data out of public commits; this filename is excluded by `.gitignore`.
