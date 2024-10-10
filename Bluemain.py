import asyncio
import struct
import pandas
from bleak import BleakClient
from bleak import BleakScanner
from consolemenu import *
from consolemenu.items import *

SENSOR_DATA = "2BEEF31A-B10D-271C-C9EA-35D865C1F48A"
SINGLE = "6D3A6149-9AFA-4445-8CF9-84F5FB8C333A"
DOUBLE = "3C857A26-8CAD-4D02-84CD-680AEC8885F3"
TRIPLE = "C23B61C3-D5D9-4AA7-B0Bf-1B73334D2C51"
ALL = "D3F72B47-A54A-45AE-B56A-FE9E76ADF269"
SF = "9FB3C336-BB50-4BA4-A2F0-1B84203ACB3D"

sensors = { "Accelerometer" : [3,'Ax','Ay','Az'], "Gyroscope" : [3, 'Gx','Gy','Gz'], "Magnetometer" : [3,'Mx','My','Mz'], "Barometer" : [1, "Bar"]}
DoF = 0
columns = []
characteristicsToSub = {SINGLE : "One sensor (Accelerometer, Gyroscope, Magnetometer...)", DOUBLE : "Two Sensors(Accelorometer + Gyroscope, Accelorometer + Magnetometer...)", TRIPLE : "Three Sensors (Accelerometer + Gysroscope + Magnetometer, Accelerometer + Gysroscope + Barometer...)", ALL : "Four Sensors"}
menucharacteristics = []
Choices = ["Start Session", "Chose Sampling Frequency", "Show Data", "Store"]
sessiondata = []

#Handle notification from the connected device
def notification_handler(handle, byte):
  formatNotification = "<" + "f" * DoF + "L"
  data = struct.unpack(formatNotification, byte)
  sessiondata.append(data)  
   
#Scanning for bluetooth devices
async def discover():
    async with BleakScanner() as scanner:
        device = await scanner.discover()
        return device
   
def disconnection_handler(_:BleakClient):
  print("Device disconnected")

#Send the new Sampling Frequency
async def write_Frequency(sf, client:BleakClient):
  sfbytes = int(sf).to_bytes(byteorder="little")
  await client.write_gatt_char(SF, sfbytes, True)
      
#Subscribe to 
async def subscribe(client:BleakClient):
  global DoF, columns
  columns.clear()
  DoF = 0
  subscription = SelectionMenu.get_selection(menucharacteristics, "Choose a characteristic to subscribe to:")
  if subscription < len(menucharacteristics):
    match menucharacteristics[subscription]:
      case "One sensor (Accelerometer, Gyroscope, Magnetometer...)":
        sensor = SelectionMenu.get_selection(sensors.keys(), "Select your sensor:")
        DoF= sensors[list(sensors.keys())[sensor]][0]
        columns.extend(sensors[list(sensors.keys())[sensor]][1:])
        await client.start_notify(SINGLE, notification_handler)
        input("Press Enter to disconnect...")
        await client.stop_notify(SINGLE)
      case "Two Sensors(Accelorometer + Gyroscope, Accelorometer + Magnetometer...)":
        sensors2 = sensors
        i = 0
        while (i <= 1):
          sensor = SelectionMenu.get_selection(sensors2.keys(), "Select your sensor:",show_exit_option=False)
          DoF += sensors2[list(sensors2.keys())[sensor]][0]
          columns.extend(sensors[list(sensors.keys())[sensor]][1:])
          sensors2.pop(list(sensors2.keys())[sensor])
          i += 1
        await client.start_notify(DOUBLE, notification_handler)
        input("Press Enter to disconnect...")
        await client.stop_notify(DOUBLE)
      case "Three Sensors (Accelerometer + Gysroscope + Magnetometer, Accelerometer + Gysroscope + Barometer...)":
        sensors2 = sensors
        i = 0
        while (i <= 2):
          sensor = SelectionMenu.get_selection(sensors2.keys(), "Select your sensor:",show_exit_option=False)
          DoF += sensors2[list(sensors2.keys())[sensor]][0]
          columns.extend(sensors2[list(sensors2.keys())[sensor]][1:])
          sensors2.pop(list(sensors2.keys())[sensor])
          i += 1
        await client.start_notify(TRIPLE, notification_handler)
        input("Press Enter to disconnect...")
        await client.stop_notify(TRIPLE)
      case "Four Sensors":
        for s in sensors.keys() :
          columns.extend(sensors[s][1:])
          DoF += sensors[s][0]
        await client.start_notify(ALL, notification_handler)
        input("Press Enter to disconnect...")
        await client.stop_notify(ALL)

async def deviceMenu(device, client:BleakClient):
  selection = SelectionMenu.get_selection(Choices, title=device)
  while (selection != 0 and selection != len(Choices)):
    clear_terminal()
    if (selection == 1):
      old_sf_data =  await client.read_gatt_char(SF)
      old_sf = struct.unpack("<I", old_sf_data)
      sf = input("Input new Sampling Frequency (current: " + str(old_sf[0]) + "): ")
      if sf != '':
        if int(sf) > 0:
          await write_Frequency(sf, client)
    if (selection == 2):
      global sessiondata
      if sessiondata:
        df = pandas.DataFrame(sessiondata, columns= columns + ['Timestap'])
        print(df)
        input("Enter to continue")
      else:
        input("No data recorded")
    if (selection == 3):
      if sessiondata:
        df = pandas.DataFrame(sessiondata, columns= columns + ['Timestap'])
        name = input("Enter a name (default: out.csv): ")
        if (name == ""):
          df.to_csv("out.csv")
        else :
          df.to_csv(name + ".csv")
      else:
        input("No data recorded")
    selection = SelectionMenu.get_selection(Choices, title=device)
  clear_terminal()
  return selection

#Get services and check if the device complies to the standard    
async def get_device_services(address):
  complies = False
  async with BleakClient(address) as client:
    if (not client.is_connected):
      raise "client not connected"

    for char in client.services[SENSOR_DATA].characteristics:
      if (char.uuid.upper() == SINGLE):
        size = await client.read_gatt_char(char.uuid)
        if(len(size) == 8 or len(size) == 16):
          complies = True
          menucharacteristics.append(characteristicsToSub[SINGLE])
      if (char.uuid.upper() == DOUBLE):
        size = await client.read_gatt_char(char.uuid)
        if(len(size) == 20 or len(size) == 28):
          complies = True
          menucharacteristics.append(characteristicsToSub[DOUBLE])
      if (char.uuid.upper() == TRIPLE):
        size = await client.read_gatt_char(char.uuid)
        if(len(size) == 32 or len(size) == 40):
          complies = True   
          menucharacteristics.append(characteristicsToSub[TRIPLE]) 
      if (char.uuid.upper() == ALL):
        size = await client.read_gatt_char(char.uuid)
        if(len(size) == 44):
          complies = True
          menucharacteristics.append(characteristicsToSub[ALL])
    return complies

async def main():
    devices = await discover()
    selection = SelectionMenu.get_selection(devices, "Choose a device to connect to")
    if selection < len(devices):
      address = devices.__getitem__(selection).address
      device = devices.__getitem__(selection).name
      clear_terminal()
      check = await get_device_services(address)
      if (check):
        client = BleakClient(address, disconnected_callback= disconnection_handler)
        await client.connect()
        if (not client.is_connected):
          raise "client not connected"
        selection = await deviceMenu(device, client)
        while (selection != len(Choices)):
          if (selection == 0):
            global sessiondata
            sessiondata.clear()
            await subscribe(client)
            selection = await deviceMenu(device, client)
        await client.disconnect()
      else:
        raise Exception("Deviece does not complies to the standard")

if __name__ == "__main__":
    asyncio.run(main())