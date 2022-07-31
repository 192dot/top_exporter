# top_exporter
Prometheus exporter to capture top

## Usage and Examples
To bring up the help menu
```sh
python3 top_exporter.py -h
```

To print top 5 processes by memory usage
```sh
python3 top_exporter.py -n 5 -m
```

To print top 5 proccess by CPU usage
```sh
python3 top_exporter.py -n 5
```

