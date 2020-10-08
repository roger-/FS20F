# Wellue FS20F pulse oximeter logger

Python script for connecting to and parsing data from the ~$30 [Wellue FS20F](https://getwellue.com/pages/fs20f-bluetooth-finger-oximeter) pulse oximeter (Bluetooth model).

# Usage

Install [bluepy](https://github.com/IanHarvey/bluepy) (requires Linux) and run with

```sh
sudo python fs20f_logger.py <MAC_ADDRESS>
```

where `<MAC_ADDRESS>` is the MAC address of your FS20F (find "VTM 20F" with a BLE sniffer like nRF Connect on Android/iOS).

The script will keep trying to connect (and reconnect when disconnected) and print output in JSON, like this (see also `sample_output.json`):

```json
{"type": "wave", "unknown_1": 0, "unknown_2": 29, "counter": 129, "ppg": 54, "spo2_wave_val": 8, "sensor_off": false, "parse_time": 1601991825.1619356}
{"type": "wave", "unknown_1": 0, "unknown_2": 30, "counter": 130, "ppg": 54, "spo2_wave_val": 8, "sensor_off": false, "parse_time": 1601991825.1625514}
{"type": "wave", "unknown_1": 0, "unknown_2": 31, "counter": 131, "ppg": 54, "spo2_wave_val": 8, "sensor_off": false, "parse_time": 1601991825.191919}
{"type": "wave", "unknown_1": 0, "unknown_2": 33, "counter": 132, "ppg": 55, "spo2_wave_val": 8, "sensor_off": false, "parse_time": 1601991825.251962}
{"type": "param", "unknown_1": 146, "pulse_rate": 78, "spo2": 99, "counter": 18, "perfusion_index": 4.702, "parse_time": 1601991825.252156}
{"type": "wave", "unknown_1": 0, "unknown_2": 35, "counter": 133, "ppg": 56, "spo2_wave_val": 8, "sensor_off": false, "parse_time": 1601991825.2524467}
{"type": "wave", "unknown_1": 0, "unknown_2": 39, "counter": 134, "ppg": 58, "spo2_wave_val": 9, "sensor_off": false, "parse_time": 1601991825.2532318}
{"type": "wave", "unknown_1": 0, "unknown_2": 43, "counter": 135, "ppg": 61, "spo2_wave_val": 9, "sensor_off": false, "parse_time": 1601991825.2818196}
```

## Simple continuous Sp02 logger

This command will automatically log Sp02 readings to the file `log.json` anytime your FS20F is turned on (and in Bluetooth range):

```sh
sudo python fs20f_logger.py <MAC_ADDRESS> | grep param > log.json
```

The resulting file can be read with [pandas](https://pandas.pydata.org/) using `pd.read_json('log.json', lines=True)`.

Note that the FS20F will not turn off while measuring, so you could potentially log Sp02 over many hours this way (e.g. overnight).

# Details

Upon connecting, the FS20F (which advertises itself as "VTM 20F") will automatically start publishing binary data under attribute `FFE4`. Some sample raw data is included in the file `sample_raw_data.hex`.

Two types of messages are published:

1) wave data at 50 Hz with photoplethysmogram (PPG) waveform data.
2) parameter data at 1 Hz with SpO2, pulse rate and perfusion index data.

There are a couple other fields that are currently unknown, which are parsed as `unknown_X` (they don't seem very important). Field `spo2_wave_val` seems to be a scaled version of `ppg`, so probably use the latter.
