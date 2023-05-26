from ultralytics import YOLO


model = YOLO("yolov8n.pt") # load a pretrained model

#Train the model
model.train(data="training.yaml", epochs=20)
metrics = model.val()
#results = model("https://ultralytics.com/images/bus.jpg")
success = model.export(format="onnx")

# model.predict(
#    source='https://media.roboflow.com/notebooks/examples/dog.jpeg',
#    conf=0.25
# )