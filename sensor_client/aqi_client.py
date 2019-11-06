import time
import datetime
from sds011 import SDS011
import aqi
from influxdb import InfluxDBClient

DEV_PATH = '/dev/ttyUSB0'
HOST = 'IP_SERVER'
PORT = 8086
USER = 'sensor'
PASSWORD = 'sensor_password'
DATABASE = 'aqi_mesurement'
PLACE = 'home'


def mesure():
    sensor = SDS011(DEV_PATH, use_query_mode=True)
    print('Sleep device...')
    sensor.sleep(sleep=True)  # Turn off fan and diode
    print('Wake-up device...')
    sensor.sleep(sleep=False)  # Turn on fan and diode
    print('Mesure for 30 secs...')
    time.sleep(30)  # Allow time for the sensor to measure properly
    print('Query data...')
    result = sensor.query()
    print('Sleep device...')
    sensor.sleep()  # Turn off fan and diode

    return result if result else (0, 0)


if __name__ == '__main__':
    pm25, pm10 = mesure()
    aqi = int(aqi.to_aqi([
        (aqi.POLLUTANT_PM25, pm25),
        (aqi.POLLUTANT_PM10, pm10),
    ]))
    print('Result: AQI: {}, PM2.5: {}, PM10: {}'.format(aqi, pm25, pm10))

    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    json_body = [
        {
            'measurement': 'aqi',
            'tags': {
                'place': PLACE,
            },
            'time': now,
            'fields': {
                'aqi': aqi,
                'pm25': pm25,
                'pm10': pm10,
            }
        }
    ]

    client = InfluxDBClient(HOST, PORT, USER, PASSWORD, DATABASE)
    client.write_points(json_body)
    print('Done...')
