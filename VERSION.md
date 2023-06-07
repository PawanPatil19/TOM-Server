# Change log (version history)

### main
- description

### dev/running_coach_demo4
- add YOLOv8 support
- remove YOLOv4
- add support for WearOS devices to read sensor data via network
- add support for ProtoBuf

### dev/running_coach_demo3
- use WearOS mock for testing
- fix issue with websocket communication

### dev/running_coach_demo2
- add obstacle detection to `dev/running_coach_demo1` via 'YOLOv4'

### dev/running_coach_demo1
- get heart rate from FitBit API and display on HoloLens2 via websocket connection

## TODO
- move `hololens_config.py` to `config` folder with json
- add test cases for all modules
- remove saving token, e.g., `fitbit_credential.json`, `fitbit_token.json`

## Known issues/limitations
- 