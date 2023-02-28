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
- Project folder: [here](project_link)
- Documentation: [here](guide_link)
- [Version info](VERSION.md)


## Requirements
- make sure `pyhton3` is installed


## Installation
- install `conda` (e.g., [Anaconda](https://docs.anaconda.com/anaconda/install/)/[Miniconda](https://docs.conda.io/en/latest/miniconda.html))
- create new conda environment `tom` using `conda env create -f environment-cpu.yml`
- activate `tom1` environment, `conda activate tom1`
- create a file `fitbit_credential.json` with Fitbit credentials (Note: json format must be correct)
-- ```json
      {
      "client_id": "XXXXX",
      "client_secret": "YYYYYYYYYYYY"
      }
      ```
- [Configure](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal) the Hololens Device Portal. Save [your user credentials](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal#creating-a-username-and-password) to `modules/hololens/hololens_config.py`


## Configure YOLOv4 ([source](https://github.com/Interactions-HSG/21-MT-JanickSpirig-HoloLens-ObjectDetection))
- Download the pre-traiend [coco weights](https://cocodataset.org/#home) ([yolov4.weights](https://drive.google.com/open?id=1cewMfusmPjYWbrnuJRuKhPMwRe_b9PaT), [yolov4-tiny.weights](https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights)) __OR__ pre-trained [interactions weights](https://drive.google.com/file/d/10xhruakVoIGTGAzH7BTxPX7rrcfWJByo/view?usp=sharing) (office and shopfloor evnironment) __OR__ train yolo for your custom classes by following the steps in [this video](https://www.youtube.com/watch?v=mmj3nxGT2YQ)
- Move the according `.weights` file (pretrained or custom) into the folder detector\data. If you use custom wieights, make sure that the file is named as `custom.weights`
- If you use custom weights, place your custom `.names` file (e.g. `obj.names`) ([download](https://drive.google.com/file/d/1lttBOLLfv_L71n6GMPmJasXOws_eMzF8/view?usp=sharing) the interactions `.names`) into folder detector\data and comment out line 18 in file detector\core\config.py and comment line 15. It should look like in the screenshot below. Remember that anytime you switch between custom wnd pretrained coco weights (pre-trained) you have to adjust these two lines of code.

<img width="541" alt="Screenshot 2021-08-15 at 15 04 22" src="https://user-images.githubusercontent.com/43849960/129479546-edf3ba64-9743-4e59-96b2-e42444e83af5.png">

- Convert the yolo weights from darkent to TensorFlow format by executing one of the commands below in the terminal
```
cd modules/yolov4

# pretrained
python save_model.py --weights detector/data/yolov4.weights --output detector/checkpoints/yolov4-416 --input_size 416 --model yolov4 

# pretrained tiny
python save_model.py --weights detector/data/yolov4-tiny.weights --output detector/checkpoints/yolov4-tiny-416 --input_size 416 --model yolov4 --tiny

# custom
python save_model.py --weights detector/data/custom.weights --output detector/checkpoints/custom-416 --input_size 416 --model yolov4
```

## Application execution 
- run `main.py` (e.g., `python main.py`)
- for tests, run `pytest`


## References
- [Structuring Your Project](https://docs.python-guide.org/writing/structure/)
- [Modules](https://docs.python.org/3/tutorial/modules.html#packages)
- [python-testing](https://realpython.com/python-testing/)
- To find/update dependencies, use `pip freeze > requirements.txt` or `conda env export > environment.yml` [ref](https://stackoverflow.com/questions/31684375/automatically-create-requirements-txt)


## Third-party libraries
- [python-fitbit](https://github.com/orcasgit/python-fitbit)
- [Hololens YOLOv4 Object Detection](https://github.com/Interactions-HSG/21-MT-JanickSpirig-HoloLens-ObjectDetection) from [tensorflow-yolov4-tflite](https://github.com/theAIGuysCode/tensorflow-yolov4-tflite)


## Training YOLOv4 weights ([source](https://github.com/Interactions-HSG/21-MT-JanickSpirig-HoloLens-ObjectDetection))
- [Pre-trained weights](https://drive.google.com/file/d/10xhruakVoIGTGAzH7BTxPX7rrcfWJByo/view?usp=sharing)
- [Dataset](https://drive.google.com/file/d/1BIaNZc5XUflGz9IqpJOeGOvYWzgVebk-/view?usp=sharing) of train images and label files
- [Dataset](https://drive.google.com/file/d/1MYIQ4cp_okxA7f0QPiTUYUpZsLWIr6gn/view?usp=sharing) of test images and label files