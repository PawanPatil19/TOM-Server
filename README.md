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
- make sure `pyhton3` is installed


## Installation
- install `conda` (e.g., [Anaconda](https://docs.anaconda.com/anaconda/install/)/[Miniconda](https://docs.conda.io/en/latest/miniconda.html))
- create new conda environment `tom` using `conda env create -f environment-cpu.yml`
- activate `tom` environment, `conda activate tom`
- create a file `config/fitbit_credential.json` with Fitbit credentials such as `{"client_id": "ID","client_secret": "SECRET"}` (Note: json format must be correct) 
- create a file `config/google_credential.json` with Google credentials such as `{"map_api_key": "KEY"}` (Note: json format must be correct)
- create a file `config/openai_credential.json` with OpenAI credentials such as `{"openai_api_key": "KEY"}` (Note: json format must be correct)
- download the pretrained weights for YOLOv8 from [ultralytics](https://github.com/ultralytics/ultralytics) (e.g., [yolov8n.pt](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt)) and copy it to `modules/yolov8/weights/` and rename it as `model.pt` (i.e., `modules/yolov8/weights/model.pt`)
- [Configure](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal) the Hololens Device Portal. Save [your user credentials](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal#creating-a-username-and-password) to `modules/hololens/hololens_config.py`


## Application execution 
- run `main.py` (e.g., `python main.py`)
- for tests, run `pytest` (or `pytest tests\...\yy.py`)

## Protobuf
- Install protobuf using `pip install protobuf`.
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
- [google-maps](https://developers.google.com/maps/documentation/maps-static/start)
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Hololens YOLOv4 Object Detection](https://github.com/Interactions-HSG/21-MT-JanickSpirig-HoloLens-ObjectDetection) from [tensorflow-yolov4-tflite](https://github.com/theAIGuysCode/tensorflow-yolov4-tflite)

