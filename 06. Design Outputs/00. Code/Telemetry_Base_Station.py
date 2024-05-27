import machine
import time
import math
import json

# Define UART settings for GPS and Zigbee
GPS_UART = machine.UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))  # UART1 for GPS
ZIGBEE_UART = machine.UART(2, baudrate=9600, tx=Pin(6), rx=Pin(7))  # UART2 for Zigbee

# Define base station GPS coordinates and initial signal strengths (mock data)
base_stations = {
    'station1': {'coords': (35.6895, 139.6917), 'received_signal_strength': None, 'time_received': None},
    'station2': {'coords': (34.0522, 118.2437), 'received_signal_strength': None, 'time_received': None},
    'station3': {'coords': (40.7128, 74.0060), 'received_signal_strength': None, 'time_received': None},
}

# Constants for free-space path loss calculation
transmitted_signal_strength = -30  # dBm, example value
frequency = 2.4e9  # Hz, example frequency for calculation

# Function to read GPS data
def read_gps_data():
    return GPS_UART.readline().decode('utf-8').strip()

# Function to calculate free space path loss to estimate the distance
def calculate_distance(received_signal_strength, transmitted_signal_strength, frequency):
    c = 3 * 10**8  # Speed of light
    fspl_db = transmitted_signal_strength - received_signal_strength
    wavelength = c / frequency
    distance = 10 ** ((fspl_db - 20 * math.log10(wavelength) - 20 * math.log10(4 * math.pi / c)) / 20)
    return distance

# Function to log data
def log_data(data):
    with open("log.txt", "a") as file:
        file.write(json.dumps(data) + "\n")

# Main loop
while True:
    # Read GPS data
    gps_data = read_gps_data()
    
    # Process GPS data
    if gps_data:
        print("GPS Data:", gps_data)
        
        # Forward GPS data to Zigbee module
        ZIGBEE_UART.write(gps_data.encode('utf-8'))
        print("GPS Data forwarded to Zigbee module")
    
    # Read data from Zigbee module
    zigbee_data = ZIGBEE_UART.readline().decode('utf-8').strip()
    if zigbee_data:
        print("Received from Zigbee:", zigbee_data)
        # Parse Zigbee data (assuming JSON format with keys: station, signal_strength, timestamp)
        data = json.loads(zigbee_data)
        station_id = 'station' + str(data['station'])
        if station_id in base_stations:
            base_stations[station_id]['received_signal_strength'] = data['signal_strength']
            base_stations[station_id]['time_received'] = data['timestamp']
            
            # Calculate distance from Tx for each base station
            distance = calculate_distance(data['signal_strength'], transmitted_signal_strength, frequency)
            print(f"Calculated distance for {station_id}: {distance} meters")
            
            # Log the calculated distances
            log_data({
                'station_id': station_id,
                'distance': distance,
                'timestamp': data['timestamp']
            })
    
    # Example use: perform location triangulation and height calculation here if data is complete
    
    time.sleep(1)  # Adjust sleep time as needed
