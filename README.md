Sensorflow Python
=================

This library allows you to communicate with a sensorflow device by using python.
Sensorflow python has been built for python 3 but with little changes will work
 on python 2 too.
 
Using Sensorflow
================
Before use sensorflow-python, you should have a sensorflow device ([for example an arduino](https://github.com/maxpowel/sensorflow-arduino)). 
The default configuration uses a serial port and JSON but you can use your custom source (serial port, ethernet... where the data come from) and
a custom serializer (JSON, YAML, XML, protocol buffers...).

Source
------
The data source. If you connect to your device through serial port the source is the serial port. That simple

If you want to create your own source, your should create a class that implements the SensorflowSource class.

```python
class SensorflowSource(metaclass=ABCMeta):
    def __iter__(self):
        return self

    def __next__(self):
        while True:
            yield self.receive()

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def close(self):
        pass
```

Once your class extends this, sensorflow knows how to fetch and push data.
In the case of serial port source, it is a simple as:

```python
class SerialSource(SensorflowSource):
    def __init__(self):
        self.serial = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=115200,
            timeout=2
        )

    def receive(self):
        return self.serial.readline()

    def send(self, data):
        self.serial.write(data)

    def close(self):
        self.serial.close()
```

That's all about sources.

Serializer
----------
By default, JSON is used but if you want your own you only have to extends the Serializer class

```python
class Serializer(metaclass=ABCMeta):
    @abstractmethod
    def loads(self, data):
        pass

    @abstractmethod
    def dumps(self, data):
        pass
```

and for json it is very simple too

```python
class JsonSerializer(Serializer):
    def loads(self, data):
        return json.loads(data.decode('utf-8'))

    def dumps(self, data):
        return json.dumps(data).encode('utf-8')
```

Sensorflow
----------
Once you have your source and serializer its time to use the library.
In this case, I will use the serial port source and JSON.
```python
import sensorflow

source = sensorflow.SerialSource()
serializer = sensorflow.JsonSerializer()
sf = sensorflow.Sensorflow(source=source, serializer=serializer)
```


Available commands
==================
The client implements the following commands:

* def ping(self): Ping your device, to check if it is listening and ready.
* def close(self): Close the connection with your device by the friendly way
* def status(self): Get data about the device like the available memory
* def sensor_read(self): Read all sensor data
* def configure(self, configs): Configure the sensors of your device. Check the section "configuration" for details

Sensorflow is in development process so more command will come soon.


Configuration
=============
A sensorflow device can handle a big variety of sensors but it will use only the ones that you configure. In the case
of arduino, this configuration is stored in the eeprom.

Every sensor has it owns parameters or options so this is reason for that every sensor requires a custom configuration process.
Luckily for us, sensoflow simplify this a lot, lets see.
 
Imagine that you want to configure a DS18B20 sensor. To use this sensor you only need the sensor address so to configure it you need
to provide this address. An example address is: 0x28 0xFF 0x10 0x93 0x6F 0x14 0x4 0x11

```python
# Connect to the device
source = sensorflow.SerialSource()
serializer = sensorflow.JsonSerializer()
sf = sensorflow.Sensorflow(source=source, serializer=serializer)

# Create the configuration for the sensor
config = sensorflow.DS18B20Sensor([0x28, 0xFF, 0x10, 0x93, 0x6F, 0x14, 0x4, 0x11])
# Send the configuration to the device
sf.configure(config)
# Device response showing if error found and how many bytes were received 
{'error': False, 'data': {'status': 'ok', 'read': 17}}
```

If you want to configure multiple devices, just send and array
```python
sensor_one = sensorflow.DS18B20Sensor([0x28, 0xFF, 0x10, 0x93, 0x6F, 0x14, 0x4, 0x11])
sensor_two = sensorflow.DS18B20Sensor([0x28, 0xFF, 0x10, 0x93, 0x6F, 0x14, 0x4, 0x12])
sensor_three = sensorflow.DS18B20Sensor([0x28, 0xFF, 0x10, 0x93, 0x6F, 0x14, 0x4, 0x13])

sf.configure([sensor_one, sensor_two, sensor_three])
```
Please notice that the configuration process will overwrite the existing configuration so all
sensors should be configured at the same time.

Console
=======
You can use an interactive console as an administration tool. Check the console.py file.
Here you have a screenshot

![alt text](https://raw.githubusercontent.com/maxpowel/sensorflow-python/master/console.png "Example of use")