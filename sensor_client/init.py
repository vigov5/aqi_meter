from influxdb import InfluxDBClient

client = InfluxDBClient('IP_SERVER', 8086, 'root',
                        'root_password', 'aqi_mesurement')
client.create_database('aqi_mesurement')
