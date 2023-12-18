import re
import subprocess
import time
import json
import numpy as np

ns = 0
data = []
results = []
amount_of_runs = 10

while ns <= amount_of_runs:
    response = (
        subprocess.Popen(
            "/usr/bin/speedtest --accept-license --accept-gdpr",
            shell=True,
            stdout=subprocess.PIPE,
        )
        .stdout.read()
        .decode("utf-8")
    )

    data.append(response)

    ping = re.search("Latency:\s+(.*?)\s", response, re.MULTILINE)  # noqa: W605, E501
    download = re.search(
        "Download:\s+(.*?)\s", response, re.MULTILINE  # noqa: W605, E501
    )
    upload = re.search("Upload:\s+(.*?)\s", response, re.MULTILINE)  # noqa: W605, E501
    jitter = re.search(
        "Latency:.*?jitter:\s+(.*?)ms", response, re.MULTILINE  # noqa: W605, E501
    )

    if ping:
        ping = ping[1]
        download = download[1]
        upload = upload[1]
        jitter = jitter[1]
    else:
        ping = np.nan
        download = np.nan
        upload = np.nan
        jitter = np.nan

    results.append(
        [
            time.strftime("%m/%d/%y"),
            time.strftime("%H:%M"),
            ping,
            jitter,
            download,
            upload,
        ]
    )

    ns = ns+1
    if ns < amount_of_runs:
        time.sleep(60)

with open("/home/pi/speedtest/data_dump.json", "w") as f:
    json.dump(data, f)

with open("/home/pi/speedtest/results_dump.json", "w") as f:
    json.dump(results, f)
