# Change log (version history)

## main
- description

## demo/learning

### v1.2
- 

### v1.1
- enable support `demo/running_coach_v2.1`
- add Google's CloudVision
- add FaceBook's Detic (not tested)
- 

### v1.0
- enable to detect pointed objects by finger tip
- use ChatGPT to generate learning content based on detected object

## demo/running_coach

### v2.1
- make running a service
- add waypoints (and enable running route)

### v2.0
- new UI
- add Google Maps API for directions, places and static maps
- add Openrouteservice API for directions
- add Nominatim OpenStreetMap API for places 
- add Geoapify API for static maps


## dev/running_coach_demo

### dev/running_coach_demo5
- integrate ChatGPT support

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
- change print to logging