import serial
import json
import struct

from abc import ABCMeta, abstractmethod

# configure the serial connections (the parameters differs on the device you are connecting to)


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



class Serializer(metaclass=ABCMeta):
    @abstractmethod
    def loads(self, data):
        pass

    @abstractmethod
    def dumps(self, data):
        pass


class JsonSerializer(Serializer):
    def loads(self, data):
        return json.loads(data.decode('utf-8'))

    def dumps(self, data):
        return json.dumps(data).encode('utf-8')


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



class Sensorflow(object):
    def __init__(self, source, serializer):
        self.source = source
        self.serializer = serializer

    def ping(self):
        run = True
        val = 0
        message = None
        while run:
            val += 1
            self.source.send(struct.pack("B", val))
            response = self.source.receive()
            if len(response):
                run = False
                message = response[1:len(response)-1].decode('ascii')
                val = response[0]

        return val, message

    def send(self, data):
        self.source.send(self.serializer.dumps(data))

    def receive(self):
        return self.serializer.loads(self.source.receive())

    def send_receive(self, data):
        self.send(data)
        return self.receive()

    def close(self):
        self.source.close()

    # Commands here

    def status(self):
        return self.send_receive({"command": "status"})

    def sensor_read(self):
        return self.send_receive({"command": "read"})

    def configure(self, configs):
        if not isinstance(configs, list):
            configs = [configs]

        data = bytes()
        for config in configs:
            data += config.build_config()

        self.send({"command": "writeConfig", "totalSensors": len(configs), "dataSize": len(data)})
        self.source.send(data)
        return self.receive()


# Sensor configurations
class DS18B20Sensor(object):
    sensor_type = "DS18B20"

    def __init__(self, address):
        if len(address) != 8:
            raise Exception("DS18B20 address should have a length of 8, not {size}".format(size=len(address)))
        self.address = address

    def build_config(self):
        sensor_type_packed = struct.pack("{size}s".format(size=len(self.sensor_type)), bytes(self.sensor_type, 'ascii'))
        address_packed = struct.pack("8B", *self.address)
        # print(address)
        data = sensor_type_packed + struct.pack("BB", 0, len(self.address)) + address_packed
        return data