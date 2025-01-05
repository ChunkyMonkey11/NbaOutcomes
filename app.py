from flask import Flask, render_template
import pandas as pd
import os
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    cwd = os.getcwd()
    print(f"right here, {cwd}")
    # Path to the uploaded CSV file
    csv_file_path = "predict_total/Predictions_Home_Road_adjusted.csv"
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    predictions = df.to_dict(orient="records")
    # Convert the DataFrame to a list of dictionaries
    return render_template("home.html", predictions=predictions)

@app.route("/about")
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
    

