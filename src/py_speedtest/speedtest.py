import contextlib
import os
import re
import subprocess
import time

from influxdb import InfluxDBClient

response = (
    subprocess.Popen(
        "/usr/bin/speedtest --accept-license --accept-gdpr",
        shell=True,
        stdout=subprocess.PIPE,
    )
    .stdout.read()
    .decode("utf-8")
)

ping = re.search("Latency:\s+(.*?)\s", response, re.MULTILINE)  # noqa: W605
download = re.search("Download:\s+(.*?)\s", response, re.MULTILINE)  # noqa: W605, E501
upload = re.search("Upload:\s+(.*?)\s", response, re.MULTILINE)  # noqa: W605
jitter = re.search(
    "Latency:.*?jitter:\s+(.*?)ms", response, re.MULTILINE  # noqa: W605, E501
)

if ping:
    ping = float(ping[1])
    download = float(download[1])
    upload = float(upload[1])
    jitter = float(jitter[1])
else:
    ping = float(0)
    download = float(0)
    upload = float(0)
    jitter = float(0)

with contextlib.suppress(Exception):
    fid = open("/home/pi/speedtest/speedtest.csv", "a+")
    if os.stat("/home/pi/speedtest/speedtest.csv").st_size == 0:
        fid.write(
            "Date,Time,Ping (ms),Jitter (ms),Download (Mbps),Upload (Mbps)\r\n"  # noqa: E501
        )
    fid.write(
        f'{time.strftime("%m/%d/%y")},{time.strftime("%H:%M")},{ping},{jitter},{download},{upload}\r\n'  # noqa: W605, E501
    )

speed_data = [
    {
        "measurement": "internet_speed",
        "tags": {"host": "RaspberryPi4"},
        "fields": {
            "download": download,
            "upload": upload,
            "ping": ping,
            "jitter": jitter,
        },
    }
]

client = InfluxDBClient(
    host="localhost",
    port=8086,
    username="speedmonitor",
    password="speedmo",
    database="internetspeed",
)

res = client.write_points(speed_data)

if not res:
    speed_data = [
        {
            "measurement": "internet_speed",
            "tags": {"host": "RaspberryPi4"},
            "fields": {
                "download": float(0),
                "upload": float(0),
                "ping": float(0),
                "jitter": float(0),
            },
        }
    ]
    time.sleep(5)
    res = client.write_points(speed_data)
