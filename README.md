# BlueArm
The software is designed to receive  data from a BLE device equipped with an IMU, which integrates accelerometers, gyroscopes, magnetometers, and barometers, through a BLE 5.0 connection.

BLE Service are design as follow:

Sensors Data: UUID: "2BEEF31A-B10D-271C-C9EA-35D865C1F48A"

Characteristics:

- One Sensor (UUID: "6D3A6149-9AFA-4445-8CF9-84F5FB8C333A", READ, Notify)
- Two Sensors (UUID: "3C857A26-8CAD-4D02-84CD-680AEC8885F3", READ, Notify)
- Three Sensors (UUID: "C23B61C3-D5D9-4AA7-B0Bf-1B73334D2C51", READ, Notify)
- Four Sensors (UUID: "D3F72B47-A54A-45AE-B56A-FE9E76ADF269", READ, Notify)

Sampling Frequency Service UUID: “E4159B0B-951E-4CDB-88EF-4D90AB83EB2A”

Characteristics:

- Sampling Frequency (UUID: “9FB3C336-BB50-4BA4-A2F0-1B84203ACB3D”, READ, WRITE)

The data is packed in little-endian order with the sensor data followed by a Timestamp which is expected to be an unsigned long

On start up the user can select the device, which has to be properly advertised, to connect to. Then the software checks if the device is correctly set up and complies to the specification. If it complies to the specification the user can start exchanging data between them. At the end of the session the user can choose to store the data collected.

To establish a connection between the BLE device and the client device I choose to use Bleak.

To store the data received I decided to use Pandas which is a Python library for data manipulation and analysis. It provides flexible, and easy-to-use data structures like Series and DataFrames for handling datasets efficiently
# Installation
Required package: Bleak, Pandas, Consolemenu
