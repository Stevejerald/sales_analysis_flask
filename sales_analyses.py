from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

# Initialize sales_data to None
sales_data = None

# Home route to upload CSV file
@app.route("/", methods=["GET", "POST"])
def index():
    global sales_data
    if request.method == "POST":
        # Check if a file is uploaded
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        
        file = request.files["file"]

        # If user does not select file
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        # Load the CSV file
        try:
            sales_data = pd.read_csv(file)
            flash("Data loaded successfully!")
            return redirect(url_for("analysis"))
        except Exception as e:
            flash(f"Failed to load data: {str(e)}")
            return redirect(request.url)
    
    return render_template("sales_analyse.html")

# Route to display sales trends
@app.route("/analysis")
def analysis():
    global sales_data
    # Check if the data is loaded
    if sales_data is None:
        flash("Please load the data first!")
        return redirect(url_for("index"))
    
    # Process the data for analysis
    try:
        # Convert InvoiceDate to datetime with dayfirst=True
        sales_data['InvoiceDate'] = pd.to_datetime(sales_data['InvoiceDate'], dayfirst=True)
        
        # Calculate revenue
        sales_data['Revenue'] = sales_data['Quantity'] * sales_data['UnitPrice']
        
        # Group by day to get daily sales trends
        daily_sales = sales_data.groupby(sales_data['InvoiceDate'].dt.date)['Revenue'].sum()

        # Plot the sales trends and save the figure
        plt.figure(figsize=(10, 6))
        daily_sales.plot()
        plt.title('Daily Sales Analysis')
        plt.xlabel('Date')
        plt.ylabel('Revenue')
        plt.xticks(rotation=45)
        chart_path = os.path.join("static", "chart.png")
        plt.savefig(chart_path)
        plt.close()  # Close the plot to free memory
    except Exception as e:
        flash(f"Error processing data: {str(e)}")
        return redirect(url_for("index"))

    return render_template("sales_analysis.html", chart_url=url_for("static", filename="chart.png"))

if __name__ == "__main__":
    app.run(debug=True)
