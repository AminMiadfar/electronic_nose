from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, get_flashed_messages
import time
import json
import yaml
from a import capture_temperature, read_gas_sensor_continuously

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Initialize data
sensor_data = {}
calibration_data = {}

def load_clean_air_data():
    with open('clean_air.yaml', 'r') as file:
        return yaml.safe_load(file)['clean_air']  # Access the clean_air key directly

def save_calibration_data(data):
    with open('calibration_data.json', 'a') as f:
        json.dump(data, f)
        f.write('\n')

# Endpoint for the homepage (calibration page)
@app.route('/')
def calibration_page():
    clean_air_data = list(load_clean_air_data().values())  # Ensure this is a list
    calibration_averages = calibration_data.get('averages', [0] * len(clean_air_data))  # Use averages

    # Make sure you have the flashed messages available
    messages = get_flashed_messages(with_categories=True)
    
    return render_template('calibration.html', clean_air_data=clean_air_data, calibration_averages=calibration_averages, messages=messages)




# Calibration process
@app.route('/calibrate', methods=['POST'])
def calibrate():
    global calibration_data
    start_time = time.time()
    duration = 10  # Duration for calibration
    gas_readings = []

    while time.time() - start_time < duration:
        gas_readings.append(next(read_gas_sensor_continuously()))
        time.sleep(2)  # Delay between readings

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

    # Capture sensor data for 30 seconds (10 captures)
    captures = []
    for _ in range(10):
        captures.append(next(read_gas_sensor_continuously()))
        time.sleep(3)

    # Calculate averages
    sensor_avg = [sum(x) / len(x) for x in zip(*captures)]

    # Combine user data and sensor averages
    sensor_data = {
        'user_data': user_data,
        'sensor_avg': sensor_avg,
        'temperature': capture_temperature(),
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Save to JSON file
    with open('sensor_data.json', 'a') as f:
        json.dump(sensor_data, f)
        f.write('\n')

    return redirect(url_for('result_page'))

# Result page
@app.route('/result')
def result_page():
    return render_template('result.html', sensor_data=sensor_data)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
