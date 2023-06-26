# TOM-Server-Python
A server for TOM

## Publications
- [publication_name](publication_link), VENUE'XX

```
<Bibtext>
```

## Contact person
- [Name](personal_website)


## Project links
- Project folder: [here](https://drive.google.com/drive/folders/1m1x-o5gUZXmEZly4BEQ52Q4oHKShcE4W?usp=sharing)
- Documentation: [here](https://docs.google.com/document/d/1hHGNQhuB4jhhsSh3hr7fSNV9Hs2YzJCQxtxhX05q5ic/view)
- [Version info](VERSION.md)


## Requirements
- Make sure `python3` is installed


## Installation
- Install `conda` (e.g., [Anaconda](https://docs.anaconda.com/anaconda/install/)/[Miniconda](https://docs.conda.io/en/latest/miniconda.html))
- Create new conda environment `tom` using `conda env create -f environment-cpu.yml` (If you have a previous environment, then remove it first; `conda remove -n tom --all`)
- Activate `tom` environment, `conda activate tom`
- Download the pretrained weights for YOLOv8 from [ultralytics](https://github.com/ultralytics/ultralytics) (e.g., [yolov8n.pt](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt)) and copy it to `modules/yolov8/weights/` and rename it as `model.pt` (i.e., `modules/yolov8/weights/model.pt`)
- Create the required credential files inside `credential` folder. Please refer to [Third-party libraries](##Third-party-libraries) section to obtain credentials. (Note: json format must be correct)
  - Create a file `credential/hololens_credential.json` with Hololens credentials such as `{"ip": "IP","username": "USERNAME","password": "PASSWORD"}`
    - [Configure](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal) the Hololens Device Portal. Save [your credentials](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal#creating-a-username-and-password) to `credential/hololens_credential.json`
  - Create a file `credential/fitbit_credential.json` with Fitbit credentials such as `{"client_id": "ID","client_secret": "SECRET"}` 
  - Create a file `credential/openai_credential.json` with OpenAI credentials such as `{"openai_api_key": "KEY"}`
  - Create a file `credential/google_credential.json` with Google credentials such as `{"map_api_key": "KEY"}`
  - Create a file `credential/ors_credential.json` with Openrouteservice credentials such as `{"map_api_key": "KEY"}`
  - Create a file `credential/geoapify_credential.json` with Geoapify credentials such as `{"map_api_key": "KEY"}`
  


## Application execution
- Run `main.py` (e.g., `python main.py`)
- For tests, run `pytest` (or `pytest tests\...\yy.py`)


## Adding third-party libraries
- Add the links of libraries/reference/API docs to [Third-party libraries](#Third-party-libraries) section
- If credentials are required, add the instructions to [Installation](#Installation) section
- Update the [environment-cpu.yml](environment-cpu.yml) file with the new library and version details
- Update [VERSION](VERSION.md) file with added capabilities/changes


## Protobuf
- Ensure you have `protoc` installed by typing `protoc --version` in your terminal. If it is not installed, you may follow the instructions [here](https://github.com/protocolbuffers/protobuf#protocol-compiler-installation).
- Create your proto file in `modules/dataformat`. For more information on how to structure proto data, please refer [here](https://protobuf.dev/getting-started/pythontutorial/).
- `cd` to `modules` and run this command in your terminal `protoc -I=dataformat --python_out=dataformat dataformat/proto_name.proto` to generate the builder class. Note that you have to run the command again if you edit the proto file.


## References
- [Structuring Your Project](https://docs.python-guide.org/writing/structure/)
- [Modules](https://docs.python.org/3/tutorial/modules.html#packages)
- [python-testing](https://realpython.com/python-testing/)
- To find/update dependencies, use `pip3 freeze > requirements.txt` or `conda env export > environment.yml` [ref](https://stackoverflow.com/questions/31684375/automatically-create-requirements-txt)


## Third-party libraries
- [python-fitbit](https://github.com/orcasgit/python-fitbit)
- [google-maps](https://developers.google.com/maps/documentation), [google-maps-services-python](https://github.com/googlemaps/google-maps-services-python)
- [OpenAI](https://platform.openai.com/docs/api-reference)
- [Nominatim OpenStreetMap](https://nominatim.org/release-docs/latest/api/Overview/)
- [Openrouteservice](https://openrouteservice.org/dev/#/api-docs), [OpenStreetMap](https://www.openstreetmap.org/copyright)
- [Geoapify](https://apidocs.geoapify.com/)
- [GeographicLib](https://geographiclib.sourceforge.io/html/python/code.html)
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Hololens YOLOv4 Object Detection](https://github.com/Interactions-HSG/21-MT-JanickSpirig-HoloLens-ObjectDetection)
