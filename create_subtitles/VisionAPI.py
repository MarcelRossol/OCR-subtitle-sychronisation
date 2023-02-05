import os
import io
from google.cloud import vision

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'vision_api_key.json'


def text_detection(file_path):
    """ Detects text in an image, using Google VisionAPI

    Args:
        file_path (str): Path to the image

    Returns:
        words (list): List of words, detected in an image
    """

    client = vision.ImageAnnotatorClient()

    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    words = []
    for text in texts:
        words.append('{}'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                     for vertex in text.bounding_poly.vertices])

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return words


if __name__ == "__main__":
    file_path = 'test_materials/zdj_test3.jpg'
    print(text_detection(file_path))
