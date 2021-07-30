#!/usr/bin/python3

# TODO: handle exceptions for each connection attempt to both BMC and GLPI
# TODO: handle missing components such as only 2 DIMMs of 12, etc.
# TODO: Ethernet interfaces /redfish/v1/Managers/bmc/EthernetInterfaces/
# TODO: OTK Logs import
# TODO: Delete existing associated items first for a computer
# TODO: Alternatively detach items from existing server and reattach new
# TODO: Remove existing firmware type if adding the same type but different version

import configparser
import requests
import json
import sys, getopt
import urllib
from urllib3.exceptions import InsecureRequestWarning
import logging
logging.basicConfig( level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings( category=InsecureRequestWarning)

class Item:

  global config
  URL = ''

  def __init__( self, Name = None, Type = None):
    self.Name = Name
    self.Type = Type
    self.URL = 'http://' + config["GLPI"]["host"] + '/apirest.php'
    self.comments = None
    logging.debug( 'Item class constructor')

  def searchGLPIbyName( self):
    response = requests.get( self.URL + 
      '/search/' + self.Type + '?criteria[0][field]=1&criteria[0][searchtype]=contains&criteria[0][value]=^' + 
      self.Name + '$&range=0-0&withindexes=1', headers = headers)
#      urllib.parse.quote( self.Name) + '&range=0-0&withindexes=1', headers = headers)
    if response.json()["totalcount"] > 0:
      ids = list( response.json()["data"])
      logging.info( "Found " + self.Type + " Id: " + ids[0])
      return int( ids[0])
    else:
      logging.debug( response.json())
    return -1

  def searchGLPIbySerial( self, Type, Serial):
    response = requests.get( self.URL + 
      '/search/' + Type + '?criteria[0][field]=10&criteria[0][searchtype]=equals&criteria[0][value]=' + 
      Serial + '&range=0-0&withindexes=1', headers = headers)
#      urllib.parse.quote( Serial) + '&range=0-0&withindexes=1', headers = headers)
    if response.json()["totalcount"] > 0:
      ids = list( response.json()["data"])
      logging.info( "Found " + self.Type + " Id: " + ids[0])
      return int( ids[0])
    else:
      logging.debug( response.json())
    return -1

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"name": "' + self.Name + '"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

  def setSerial( self):
    response = requests.put( self.URL + 
      '/' + self.Type + '/' + str( self.Id), data = '{"input": {"serial": "' + str( self.Serial) + '"}}', headers = headers)
    logging.debug( response.url)
    logging.debug( response.json())

  def setUUID( self):
    response = requests.put( self.URL + 
      '/' + self.Type + '/' + str( self.Id), data = '{"input": {"uuid": "' + str( self.UUID) + '"}}', headers = headers)
    logging.debug( response.url)
    logging.debug( response.json())

  def setItemsId( self):
    response = requests.put( self.URL + 
      '/' + self.Type + '/' + str( self.Id), data = '{"input": {"items_id": "' + str( self.Items_id) + '"}}', headers = headers)
    logging.debug( response.url)
    logging.debug( response.status_code)

class DropDown( Item):

  def __init__( self, Name = None, Type = None):
    super().__init__( Name, Type)
    logging.debug( 'DropDown class constructor')
    self.Name = Name
    self.Type = Type

    self.Id = super().searchGLPIbyName()
    if self.Id == -1:
      logging.debug( "Adding new DropDown record of type: " + self.Type)
      super().addGLPIItem()

class Manufacturer( DropDown):

  def __init__( self, Name = None):
    super().__init__( Name, 'Manufacturer')
    logging.debug( 'Manufacturer class constructor')

class ComputerType( DropDown):

  def __init__( self, Name = None):
    super().__init__( Name, 'ComputerType')
    logging.debug( 'ComputerType class constructor')

class ComputerModel( DropDown):

  def __init__( self, Name = None):
    super().__init__( Name, 'ComputerModel')
    logging.debug( 'ComputerModel class constructor')

  # Redefine addGLPIItem method to store Product number, Units, Depth, Power connections, etc

class DeviceMemoryType( DropDown):

  def __init__( self, Name = None):
    super().__init__( Name, 'DeviceMemoryType')
    logging.debug( 'DeviceMemoryType class constructor')

class DeviceFirmwareType( DropDown):

  def __init__( self, Name = None):
    super().__init__( Name, 'DeviceFirmwareType')
    logging.debug( 'DeviceFirmwareType class constructor')

class DropDownDevice( DropDown):

  def __init__( self, Name = None, Type = None):
    super().__init__( Name, Type)
    self.product_number = None
    logging.debug( 'DropDownDevice class constructor')

  # Redefine addGLPIItem method to store product_number

class DeviceMemoryModel( DropDownDevice):

  def __init__( self, Name = None):
    super().__init__( Name, 'DeviceMemoryModel')
    logging.debug( 'DeviceMemoryModel class constructor')

class DeviceFirmwareModel( DropDownDevice):

  def __init__( self, Name = None):
    super().__init__( Name, 'DeviceFirmwareModel')
    logging.debug( 'DeviceFirmwareModel class constructor')

class DeviceHardDriveModel( DropDownDevice):

  def __init__( self, Name = None):
    super().__init__( Name, 'DeviceHardDriveModel')
    logging.debug( 'DeviceHardDriveModel class constructor')

class DeviceProcessorModel( DropDownDevice):

  def __init__( self, Name = None):
    super().__init__( Name, 'DeviceProcessorModel')
    logging.debug( 'DeviceProcessorModel class constructor')

class DeviceProcessor( Item):

  def __init__( self, Name = None, Frequency = None, Cores = None, Threads = None, MF = None, Model = None):
    self.Manufacturer = Manufacturer( MF)
    self.Model = DeviceProcessorModel( Model)
    self.Frequency = Frequency
    self.Cores = Cores
    self.Threads = Threads
    super().__init__( Name, 'DeviceProcessor')
    logging.debug( 'DeviceProcessor class constructor')

    self.Id = super().searchGLPIbyName()
    if self.Id == -1:
      logging.debug( "Adding new DeviceProcessor item")
      self.addGLPIItem()

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"designation": "' + self.Name + '", "frequency_default": "' + 
      str( self.Frequency) + '", "frequence": "' + str( self.Frequency) + '", "nbcores_default": "' + str( self.Cores) + '", "nbthreads_default": "' + 
      str( self.Threads) + '", "manufacturers_id": "' + str( self.Manufacturer.Id) + '", "deviceprocessormodels_id": "' + 
      str( self.Model.Id) + '"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

class DeviceHardDrive( Item):

  def __init__( self, Name = None):
    self.Model = DeviceHardDriveModel( Name)
    self.Type = 'DeviceHardDrive'

    super().__init__( Name, self.Type)
    logging.debug( 'DeviceHardDrive class constructor')
    logging.debug( "HardDrive device: " + Name + " Model id: " + str( self.Model.Id))

    self.Id = super().searchGLPIbyName()
    if self.Id == -1:
      logging.debug( "Adding new DeviceHardDrive item")
      self.addGLPIItem()

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"designation": "' + self.Name + 
      '", "deviceharddrivemodels_id": "' + str( self.Model.Id) + '"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

class DeviceMemory( Item):

  def __init__( self, Name = None, Frequency = None, Size = None, MF = None, MT = None, Model = None):
    self.Manufacturer = Manufacturer( MF)
    self.Model = DeviceMemoryModel( Model)
    self.MT = DeviceMemoryType( MT)
    self.Frequency = Frequency
    self.Size = Size
    self.Type = 'DeviceMemory'

    super().__init__( Name, self.Type)
    logging.debug( 'DeviceMemory class constructor')
    logging.debug( "Memory device: " + Name + " Manufacturer Id: " + str( self.Manufacturer.Id) + 
      " Model id: " + str( self.Model.Id) + " Type id: " + str( self.MT.Id))

    self.Id = super().searchGLPIbyName()
    if self.Id == -1:
      logging.debug( "Adding new DeviceMemory item")
      self.addGLPIItem()

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"designation": "' + self.Name + '", "frequence": "' + 
      str( self.Frequency) + '", "size_default": "' + str( self.Size) + '", "devicememorytypes_id": "' + 
      str( self.MT.Id) + '", "manufacturers_id": "' + str( self.Manufacturer.Id) + '", "devicememorymodels_id": "' + 
      str( self.Model.Id) + '"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

class DeviceFirmware( Item):

  def __init__( self, Version = None, MF = None, FT = None, Model = None):
    self.Manufacturer = Manufacturer( MF)
    self.Model = DeviceFirmwareModel( Model)
    self.FT = DeviceFirmwareType( FT)
    self.Version = Version
    self.Type = 'DeviceFirmware'

    super().__init__( Version, self.Type)
    logging.debug( 'DeviceFirmware class constructor')
    logging.debug( "Firmware device: " + Version + " Manufacturer Id: " + str( self.Manufacturer.Id) + 
      " Model id: " + str( self.Model.Id) + " Type id: " + str( self.FT.Id))

    self.Id = super().searchGLPIbyName()
    if self.Id == -1:
      logging.debug( "Adding new DeviceFirmware item")
      self.addGLPIItem()

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"designation": "' + self.Name + '", "devicefirmwaretypes_id": "' + 
      str( self.FT.Id) + '", "manufacturers_id": "' + str( self.Manufacturer.Id) + '", "devicefirmwaremodels_id": "' +
      str( self.Model.Id) + '", "version": "' + self.Version + '"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

class Item_DeviceFirmware( Item):

  def __init__( self, Version, MF, FT, Model, Items_id):

    self.DF = DeviceFirmware( Version, MF, FT, Model)

    self.Items_id = Items_id
    self.Type = 'Item_DeviceFirmware'

    super().__init__( Version, self.Type)
    logging.debug( 'Item_DeviceFirmware class constructor')

    self.Id = self.searchGLPIbyCombo()
    if self.Id == -1:
      logging.info( "Adding new Item_DeviceFirmware item")
      self.addGLPIItem()

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"devicefirmwares_id": "' + str( self.DF.Id) + 
      '", "items_id": "' + str( self.Items_id) + 
      '", "itemtype": "Computer", "entities_id": "0"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

  def searchGLPIbyCombo( self):
    response = requests.get( self.URL + 
      '/search/' + self.Type + '?criteria[0][link]=AND&criteria[0][field]=4&criteria[0][searchtype]=equals&criteria[0][value]=' + 
      str( self.DF.Id) + '&criteria[1][link]=AND&criteria[1][field]=5&criteria[1][searchtype]=equals&criteria[1][value]=' +
      str( self.Items_id) + '&range=0-0&withindexes=1', headers = headers)
    if response.json()["totalcount"] > 0:
      ids = list( response.json()["data"])
      logging.info( "Found " + self.Type + " Id: " + ids[0])
      return int( ids[0])
    else:
      logging.debug( response.json())
    return -1

class Item_DeviceMemory( Item):

  def __init__( self, Name, Frequency, Size, MF, MT, Model, Serial, Items_id):

    self.DM = DeviceMemory( Name, Frequency, Size, MF, MT, Model)

    self.Serial = Serial
    self.Size = Size
    self.Items_id = Items_id
    self.Type = 'Item_DeviceMemory'

    super().__init__( Name, self.Type)
    logging.debug( 'Item_DeviceMemory class constructor')

    self.Id = super().searchGLPIbySerial( self.Type, Serial)
    if self.Id == -1:
      logging.info( "Adding new Item_DeviceMemory item")
      self.addGLPIItem()
    else:
      logging.info( "Relinking existing Item_DeviceMemory item")
      self.updateGLPIItem()

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"size": "' + str( self.Size) + '", "devicememories_id": "' + 
      str( self.DM.Id) + '", "items_id": "' + str( self.Items_id) + '", "serial": "' + self.Serial + 
      '", "itemtype": "Computer", "entities_id": "0"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

  def updateGLPIItem( self):
    response = requests.put( self.URL + 
      '/' + self.Type + '/' + str( self.Id), data = '{"input": {"size": "' + str( self.Size) + '", "devicememories_id": "' + 
      str( self.DM.Id) + '", "items_id": "' + str( self.Items_id) + '", "serial": "' + self.Serial + 
      '", "itemtype": "Computer", "entities_id": "0"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 200:
      logging.info( "Updated " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

class Item_DeviceHardDrive( Item):

  def __init__( self, Name, Serial, Items_id):

    self.DHD = DeviceHardDrive( Name)

    self.Serial = Serial
    self.Items_id = Items_id
    self.Type = 'Item_DeviceHardDrive'

    super().__init__( Name, self.Type)
    logging.debug( 'Item_DeviceHardDrive class constructor')

    self.Id = super().searchGLPIbySerial( self.Type, Serial)
    if self.Id == -1:
      logging.info( "Adding new Item_DeviceHardDrive item")
      self.addGLPIItem()
    else:
      logging.info( "Relinking existing Item_DeviceHardDrive item")
      self.updateGLPIItem()

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"deviceharddrives_id": "' + 
      str( self.DHD.Id) + '", "items_id": "' + str( self.Items_id) + '", "serial": "' + self.Serial + 
      '", "itemtype": "Computer", "entities_id": "0"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

  def updateGLPIItem( self):
    response = requests.put( self.URL + 
      '/' + self.Type + '/' + str( self.Id), data = '{"input": {"deviceharddrives_id": "' + 
      str( self.DHD.Id) + '", "items_id": "' + str( self.Items_id) + '", "serial": "' + self.Serial + 
      '", "itemtype": "Computer", "entities_id": "0"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 200:
      logging.info( "Updated " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

class Item_DeviceProcessor( Item):

  def __init__( self, Name, Frequency, Cores, Threads, MF, Model, Serial, Items_id):

    self.DP = DeviceProcessor( Name, Frequency, Cores, Threads, MF, Model)

    self.Serial = Serial
    self.Frequency = Frequency
    self.Cores = Cores
    self.Threads = Threads
    self.Items_id = Items_id
    self.Type = 'Item_DeviceProcessor'

    super().__init__( Name, self.Type)
    logging.debug( 'Item_DeviceProcessor class constructor')

    self.Id = super().searchGLPIbySerial( self.Type, Serial)
    if self.Id == -1:
      logging.info( "Adding new Item_DeviceProcessor item")
      self.addGLPIItem()
    else:
      logging.info( "Relinking existing Item_DeviceProcessor item")
      self.updateGLPIItem()

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"nbcores": "' + str( self.Cores) + '", "frequency": "' + 
      str( self.Frequency) + '", "nbthreads": "' + str( self.Threads) + '", "deviceprocessors_id": "' + 
      str( self.DP.Id) + '", "items_id": "' + str( self.Items_id) + '", "serial": "' + self.Serial + 
      '", "itemtype": "Computer", "entities_id": "0"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

  def updateGLPIItem( self):
    response = requests.put( self.URL + 
      '/' + self.Type + '/' + str( self.Id), data = '{"input": {"nbcores": "' + str( self.Cores) + '", "frequency": "' + 
      str( self.Frequency) + '", "nbthreads": "' + str( self.Threads) + '", "deviceprocessors_id": "' + 
      str( self.DP.Id) + '", "items_id": "' + str( self.Items_id) + '", "serial": "' + self.Serial + 
      '", "itemtype": "Computer", "entities_id": "0"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      logging.info( "Updated " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

class Computer( Item):

  def __init__( self, Name = None, MF = None, CT = None, Model = None):
    self.Manufacturer = Manufacturer( MF)
    self.CT = ComputerType( CT)
    self.Model = ComputerModel( Model)
    super().__init__( Name, 'Computer')
    logging.debug( 'Computer class constructor')

    self.Id = super().searchGLPIbyName()
    if self.Id == -1:
      logging.debug( "Adding new Computer item")
      self.addGLPIItem()

  def addGLPIItem( self):
    response = requests.post( self.URL + 
      '/' + self.Type + '/', data = '{"input": {"name": "' + self.Name + '", "computermodels_id": "' + 
      str( self.Model.Id) + '", "manufacturers_id": "' + str( self.Manufacturer.Id) + '", "computertypes_id": "' + 
      str( self.CT.Id) + '"}}', headers = headers)
    logging.debug( response.url)
    if response.status_code == 201:
      self.Id = response.json()["id"]
      logging.info( "Inserted " + self.Type + " Id: " + str( self.Id))
      return self.Id
    else:
      logging.debug( response.json())
    return -1

class TiogaPassServer( Computer):

  def __init__( self, Name, MF, CT, Model, Serial, UUID):
    self.Serial = Serial
    self.UUID = UUID
    super().__init__( Name, MF, CT, Model)
    logging.debug( 'TiogaPassServer class constructor')

    logging.info( "Setting serial number: " + self.Serial)
    super().setSerial()

    logging.info( "Setting UUID: " + self.UUID)
    super().setUUID()

  def setFirmware( self, FW, Name, MF, FT, Model, Version):
    firmware = Item_DeviceFirmware( Version, MF, FT, Model, self.Id) 

  def setDimm( self, Slot, Name, Frequency, Size, MF, MT, Model, Serial):
    memory = Item_DeviceMemory( Name, Frequency, Size, MF, MT, Model, Serial, self.Id) 

  def setCPU( self, Socket, Name, Frequency, Cores, Threads, MF, Model, Serial):
    Item_DeviceProcessor( Name, Frequency, Cores, Threads, MF, Model, Serial, self.Id) 

  def setDrive( self, Bay, Name, Serial):
    Item_DeviceHardDrive( Name, Serial, self.Id) 

def main( argv):

  # Read command line arguments
  ip =''
  if len(sys.argv) < 2:
    print( 'glpi.py -i <BMC_IP>')
    sys.exit(2)
  try:
    opts, args = getopt.getopt(argv,"hi:",["ip="])
  except getopt.GetoptError:
    print( 'glpi.py -i <BMC_IP>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
       print( 'glpi.py -i <BMC_IP>')
       sys.exit()
    elif opt in ("-i", "--ip"):
       ip = arg
  logging.info( 'Working with the following address: ' + ip)

  # Read the config file
  global config
  config = configparser.ConfigParser()
  config.read('glpi.ini')
  logging.info( 'Read config: glpi.ini')

  # Init GLPI session
  try:
    response = requests.get( 'http://' + config["GLPI"]["host"] + 
      '/apirest.php/initSession?get_full_session=true', auth=( config["GLPI"]["user"], config["GLPI"]["pass"]))
  except requests.exceptions.ReadTimeout:
    sys.exit('Oops. Read timeout occured')
  except requests.exceptions.ConnectTimeout:
    sys.exit('Oops. Connection timeout occured!')

  resp_json = response.json()
  logging.debug( 'Session token: ' + resp_json["session_token"])

  global headers
  headers = {'Session-Token': resp_json["session_token"]}
 
  logging.info( 'Working with the Chassis endpoint')

  # Get Chassis endpoint
  chassis = requests.get( 'https://' + ip + '/redfish/v1/Chassis/TiogaPass_Baseboard', 
    auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
  chassis_json = chassis.json()

  chassis_json["Manufacturer"] = "GAGAR.IN"			# Broken > sign encoding in GLPI search
  # chassis_json["PartNumber"] should be saved in a ComputerModel

  # Get System endpoint
  system = requests.get( 'https://' + ip + '/redfish/v1/Systems/system', 
    auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
  system_json = system.json()

  t = TiogaPassServer( chassis_json["SerialNumber"], chassis_json["Manufacturer"], chassis_json["ChassisType"], 
    chassis_json["Model"], chassis_json["SerialNumber"], system_json["UUID"])

  # Get BMC endpoint
  bmc = requests.get( 'https://' + ip + '/redfish/v1/Managers/bmc',
    auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
  bmc_json = bmc.json()

  t.setFirmware( 'BMC', bmc_json["Description"], 'Phoenix Technologies', 'BMC', bmc_json["Id"], bmc_json["FirmwareVersion"])

  # Get uefi endpoint
  uefi = requests.get( 'https://' + ip + '/redfish/v1/UpdateService/FirmwareInventory/bios_active', 
    auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
  uefi_json = uefi.json()

  t.setFirmware( 'UEFI', uefi_json["Description"], 'Phoenix Technologies', 'UEFI', uefi_json["Id"], uefi_json["Version"])

  # Get ME endpoint
  me = requests.get( 'https://' + ip + '/redfish/v1/UpdateService/FirmwareInventory/me', 
    auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
  me_json = me.json()

  # ME endpoint may be missing
  if 'error' not in me_json:
    t.setFirmware( 'ME', me_json["Description"], 'Intel(R) Corporation', 'ME', me_json["Id"], me_json["Version"])

  logging.info( 'Working with the CPU endpoint')

  # Get CPU endpoint
  cpu = requests.get( 'https://' + ip + '/redfish/v1/Systems/system/Processors', 
    auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
  cpu_json = cpu.json()

  logging.info( 'Iterating over CPUs endpoints')

  CPUs = cpu_json["Members"]
  for cpu in CPUs:

    # Get particular cpu endpoint
    c = requests.get( 'https://' + ip + cpu["@odata.id"],
      auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
    c_json = c.json()
   
    if 'ProtectedIdentificationNumber' not in c_json:
      logging.warning( 'Processor PIN missing for ' + cpu["@odata.id"])
      continue

    t.setCPU( cpu, c_json["Version"], c_json["MaxSpeedMHz"], c_json["TotalCores"], 
      c_json["TotalThreads"], c_json["Manufacturer"], c_json["Model"], c_json["ProtectedIdentificationNumber"])

  logging.info( 'Working with the Memory endpoint')

  # Get Memory endpoint
  memory = requests.get( 'https://' + ip + '/redfish/v1/Systems/system/Memory', 
    auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
  memory_json = memory.json()

  logging.info( 'Iterating over Dimm endpoints')

  Dimms = memory_json["Members"]
  for dimm in Dimms:

    # Get particular dimm endpoint
    d = requests.get( 'https://' + ip + dimm["@odata.id"],
      auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
    d_json = d.json()

    if ('SerialNumber' not in d_json) or (d_json["SerialNumber"] == ''):
      logging.warning( 'SerialNumber missing or empty for ' + dimm["@odata.id"])
      continue

    t.setDimm( dimm, d_json["PartNumber"].strip(), d_json["OperatingSpeedMhz"], d_json["CapacityMiB"], 
      d_json["Manufacturer"], d_json["MemoryDeviceType"] + ' - ' + d_json["MemoryType"], 
      d_json["PartNumber"].strip(), d_json["SerialNumber"])

  logging.info( 'Working with the Storage endpoint')

  # Get Storage endpoint
  storage = requests.get( 'https://' + ip + '/redfish/v1/Systems/system/Storage/1', 
    auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
  storage_json = storage.json()

  logging.info( 'Iterating over Drive endpoints')

  Drives = storage_json["Drives"]
  for drive in Drives:

    # Get particular drive endpoint
    d = requests.get( 'https://' + ip + drive["@odata.id"], 
      auth=( config["BMC"]["user"], config["BMC"]["pass"]), verify=False)
    d_json = d.json()

    if ('SerialNumber' not in d_json) or (d_json["SerialNumber"] == ''):
      logging.warning( 'SerialNumber missing or empty for ' + drive["@odata.id"])
      continue

    t.setDrive( d_json["Name"], d_json["Model"].strip(), d_json["SerialNumber"])

  # Kill session
  response = requests.get( 'http://' + config["GLPI"]["host"] + '/apirest.php/killSession', headers=headers)

if __name__ == '__main__':
  main( sys.argv[1:])
