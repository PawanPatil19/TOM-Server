import cv2


# FIXME: add unit tests

def get_cropped_frame(frame, x1, y1, x2, y2):
    return frame[y1:y2, x1:x2]


def read_image_file_bytes(image_path):
    with open(image_path, 'rb') as image_file:
        return image_file.read()


def get_png_image_bytes(opencv_frame):
    _, encoded_image = cv2.imencode('.png', opencv_frame)
    return encoded_image.tobytes()


def save_image(filename, opencv_frame):
    cv2.imwrite(filename, opencv_frame)


def save_image_bytes(filename, image_bytes):
    with open(filename, 'wb') as f:
        f.write(image_bytes)
