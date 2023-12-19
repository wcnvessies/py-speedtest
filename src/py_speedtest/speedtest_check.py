import json
import os
import re
import subprocess
import time

import numpy as np

data = []
results = []
amount_of_runs = 10

for ns in range(1, amount_of_runs):
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

    if ns < amount_of_runs:
        time.sleep(60)

with open(
    os.path.join(
        os.path.dirname(os.path.abspath("__file__")), "json", "data_dump.json"
    ),
    "w",
) as f:
    json.dump(data, f)

with open(
    os.path.join(
        os.path.dirname(os.path.abspath("__file__")), "json", "results_dump.json"
    ),
    "w",
) as f:
    json.dump(results, f)
