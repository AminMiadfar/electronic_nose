from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, get_flashed_messages
import time
import json
import yaml
import os
import boto3
from a import capture_temperature, read_gas_sensor_continuously

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# AWS S3 setup
S3_BUCKET_NAME = 'aminenose'
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)


# Initialize data
sensor_data = {}
calibration_data = {}

def load_clean_air_data():
    """Load clean air data from the YAML file."""
    with open('clean_air.yaml', 'r') as file:
        return yaml.safe_load(file)['clean_air']  # Access the clean_air key directly

def save_calibration_data(data):
    """Save calibration data to a JSON file."""
    with open('calibration_data.json', 'a') as f:
        json.dump(data, f)
        f.write('\n')

def load_calibration_data():
    """Load the latest calibration data."""
    if os.path.exists('calibration_data.json'):
        with open('calibration_data.json', 'r') as f:
            lines = f.readlines()
            return json.loads(lines[-1]) if lines else {}
    return {}

def upload_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket."""
    if object_name is None:
        object_name = file_name

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False
    return True

# Shutdown route
@app.route('/shutdown')
def shutdown():
    """Shutdown the Raspberry Pi."""
    os.system('sudo shutdown now')
    return "Shutting down...", 200

# Endpoint for the homepage (calibration page)
@app.route('/')
def calibration_page():
    """Render the calibration page."""
    clean_air_data = list(load_clean_air_data().values())  # Ensure this is a list
    calibration_averages = calibration_data.get('averages', [0] * len(clean_air_data))  # Use averages

    # Make sure you have the flashed messages available
    messages = get_flashed_messages(with_categories=True)
    
    return render_template('calibration.html', clean_air_data=clean_air_data, calibration_averages=calibration_averages, messages=messages)

# Calibration process
@app.route('/calibrate', methods=['POST'])
def calibrate():
    """Handle the calibration process."""
    global calibration_data
    start_time = time.time()
    duration = 10  # Duration for calibration
    gas_readings = []

    while time.time() - start_time < duration:
        gas_readings.append(next(read_gas_sensor_continuously()))
        time.sleep(1)  # Delay between readings

    # Check if any readings were captured
    if not gas_readings:
        flash("Calibration failed: No sensor readings captured. Please try again.", "error")
        return redirect(url_for('calibration_page'))

    # Calculate averages for calibration
    averages = [sum(reading) / len(reading) for reading in zip(*gas_readings)]

    calibration_data = {
        'gas_readings': gas_readings,
        'averages': averages,  # Save the averages
        'status': 'calibrated'
    }

    # Load clean air criteria
    clean_air_data = load_clean_air_data()

    # Check if the averages exceed clean air criteria
    is_clean = True
    for index, average in enumerate(averages):
        sensor_key = f'mq{index + 2}'  # Assuming your sensors are mq2, mq3, etc.
        if sensor_key in clean_air_data:
            if average > clean_air_data[sensor_key]:
                is_clean = False
                break  # Break if any average is too high

    # Flash message and redirect on failure
    if not is_clean:
        flash("Calibration failed: Sensor readings exceed clean air criteria. Please try again.", "error")

        # Save calibration data even if it failed
        save_calibration_data(calibration_data)

        return redirect(url_for('calibration_page'))

    # Save calibration data if the readings are within the acceptable range
    save_calibration_data(calibration_data)

    return redirect(url_for('input_page'))

# Input page (after calibration)
@app.route('/input')
def input_page():
    """Render the wine input page."""
    return render_template('input.html')

# Start capturing wine data
@app.route('/capture', methods=['POST'])
def capture():
    global sensor_data
    user_input = request.form.to_dict()

    # Store user inputs
    user_data = {
        'username': user_input['username'],
        'wine_type': user_input['wine_type'],
        'origin': user_input['origin'],
        'wine_name': user_input['wine_name'],
        'alcohol_percent': user_input['alcohol_percent'],
        'date_of_produce': user_input['date_of_produce'],
        'characteristics': {
            'light': user_input['light'],
            'bold': user_input['bold'],
            'smooth': user_input['smooth'],
            'dry': user_input['dry'],
            'soft': user_input['soft'],
            'acidic': user_input['acidic'],
            'tannic': user_input['tannic'],
            'sweet': user_input['sweet']
        }
    }

    # Capture sensor data for 10 seconds (5 captures)
    captures = []
    for _ in range(5):
        captures.append(next(read_gas_sensor_continuously()))
        time.sleep(1)

    # Calculate averages
    sensor_avg = [sum(x) / len(x) for x in zip(*captures)]

    # Capture temperature and humidity
    temperature, humidity = capture_temperature()  # This already returns humidity

    # Combine user data and sensor averages
    sensor_data = {
        'user_data': user_data,
        'sensor_avg': sensor_avg,
        'temperature': temperature,
        'humidity': humidity,  # Add humidity here
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save to JSON file
    json_file_path = 'sensor_data.json'
    with open(json_file_path, 'a') as f:
        json.dump(sensor_data, f)
        f.write('\n')

    # Upload the JSON file to S3
    if upload_to_s3(json_file_path, S3_BUCKET_NAME):
        flash("Sensor data uploaded to S3 successfully.", "success")
    else:
        flash("Failed to upload sensor data to S3.", "error")

    return redirect(url_for('result_page'))

# Result page
@app.route('/result')
def result_page():
    """Render the result page with sensor data."""
    calibration_averages = calibration_data.get('averages', [0] * 6)  # Adjust based on the number of sensors
    characteristics_data = sensor_data['user_data']['characteristics'] if 'user_data' in sensor_data else {}
    return render_template('result.html', sensor_data=sensor_data, 
                           calibration_averages=calibration_averages, 
                           characteristics_data=characteristics_data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
