import cv2 as cv
import VisionAPI as Vision


def crop_image(img_file):
    """ Process and crop image, for better ocr

    Args:
        img_file (str): Path to image
    """

    img = cv.imread(img_file)
    img_h, img_w, channels = img.shape
    x = int(img_w / 15)
    w = int(img_w - 2 * x)
    y = int(img_h * (7 / 10))
    h = int(img_h / 4.5)

    img = cv.imread(img_file)
    roi = img[y:y + h, x:x + w]
    cv.imwrite(f"temp/box_roi.png", roi)

    img_file = f"temp/box_roi.png"
    return img_file


def ocr(img_file, index=0):
    """ Performs OCR with pre-processing and cropping of image.

    Args:
        index: for tests
        img_file (str): Path to image

    Returns:
        words (list): List of words, detected in an image
    """

    img = crop_image(img_file, index)
    words = Vision.text_detection(img)
    return words


if __name__ == "__main__":
    test_img_file = "test_materials/test.png"
    x = ocr(test_img_file)
    print(x)
