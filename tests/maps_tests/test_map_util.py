from math import sqrt

coordinates = [(1.293749, 103.775822),
               (1.293690, 103.775317),
               (1.2932756, 103.7750778),
               (1.292167, 103.774453),
               (1.292328, 103.773825),
               (1.293184, 103.772804),
               (1.293415, 103.772192),
               (1.293698, 103.772195),
               (1.293942, 103.772308),
               (1.294275, 103.772697),
               (1.294361, 103.772605)]

size = (600, 400)


def compare_images(image1, image2, threshold):
    # check if same size and same colour mode
    if image1.size != image2.size or image1.mode != image2.mode:
        return False

    pixel_count = image1.size[0] * image1.size[1]
    pixel_diff_count = 0

    pixels1 = image1.load()
    pixels2 = image2.load()

    # compare pixel by pixel for difference
    for x in range(image1.size[0]):
        for y in range(image1.size[1]):
            # as long as pixel diff is less than threshold, it is considered the same pixel
            if calculate_pixel_diff(pixels1[x, y], pixels2[x, y]) > threshold:
                pixel_diff_count += 1

    similarity = 1 - (pixel_diff_count / pixel_count)
    return similarity


def calculate_pixel_diff(pixel1, pixel2):
    r1, g1, b1 = pixel1[:3]
    r2, g2, b2 = pixel2[:3]
    # Calculate the Euclidean distance between two pixels
    distance = sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)
    return distance
