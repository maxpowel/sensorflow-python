import sensorflow
import cmd
# example of config: ds18b20 0x28 0xFF 0x10 0x93 0x6F 0x14 0x4 0x11
# example of config: dht 11 14
print("Initializing...")
source = sensorflow.SerialSource()
serializer = sensorflow.JsonSerializer()
sf = sensorflow.Sensorflow(source=source, serializer=serializer)

sf.ping()


def ds18b20(params):
    return sensorflow.DS18B20Sensor([int(i, 0) for i in params])


def dht(params):
    return sensorflow.DHTSensor(*[int(i) for i in params])

configs = {
    "ds18b20": ds18b20,
    "dht": dht
}


class SensorflowCommands(cmd.Cmd):

    def do_read(self, line):
        print(sf.sensor_read())

    def do_status(self, line):
        print(sf.status())

    def do_ping(self, line):
        sf.ping()

    def do_config(self, line):
        if line == "help":
            print("Available sensors:")
            print([i for i in configs.keys()])
        else:
            i = 0
            read = True
            configuration_list = []
            while read:
                sensor_config = input("Sensor {i}: ".format(i=i))
                params = sensor_config.split()
                if len(params) > 0:
                    sensor_type = params.pop(0)
                    if sensor_type in configs:
                        try:
                            configuration_list.append(configs[sensor_type.lower()](params))
                            i += 1
                        except Exception as e:
                            print("Error")
                            print(str(e))
                    else:
                        print("{sensor_type} is not available, available are:")
                        print([i for i in configs.keys()])
                else:
                    read = False

            response = None
            while response is None:
                response = input("Will be written the configuration for {n}, sensors. Continue with it? (y/n)".format(n=len(configuration_list)))
                if response == "y":
                    print(configuration_list)
                    print(sf.configure(configuration_list))
                elif response != "n":
                    response = None




    def do_exit(self, line):
        sf.close()
        exit()

    # def do_greet(self, line):
    #     from roams.fonio.kernel_dev_command import greet
    #     try:
    #         greet()
    #     except:
    #         print("Exception in user code:")
    #         print('-' * 60)
    #         traceback.print_exc(file=sys.stdout)
    #         print('-' * 60)

try:
    SensorflowCommands().cmdloop()
except KeyboardInterrupt:
    sf.close()
