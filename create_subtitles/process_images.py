import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np
import os

if not os.path.exists('temp'):
    os.makedirs('temp')


def display(im_path):
    """ Display images using matplotlib

    Args:
        im_path (str): path to the image
    """

    dpi = 80
    im_data = plt.imread(im_path)

    height, width = im_data.shape[:2]

    # What size does the figure need to be in inches to fit the image?
    figsize = width / float(dpi), height / float(dpi)

    # Create a figure of the right size with one axes that takes up the full figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes([0, 0, 1, 1])

    # Hide spines, ticks, etc.
    ax.axis('off')

    # Display the image.
    ax.imshow(im_data, cmap='gray')
    plt.show()


def invert(image_path):
    """ Invert the colors in image

    Args:
        image_path (numpy.ndarray): Image loaded into memory, using "cv.imread()"
    Return:
        inverted_image (numpy.ndarray): Image with inverted colors
    """

    image = cv.imread(image_path)
    inverted_image = cv.bitwise_not(image)
    cv.imwrite("temp/inverted.png", inverted_image)
    return "temp/inverted.png"


def grayscale(image_path):
    """ Convert image into grayscale

    Args:
        image_path (numpy.ndarray): Image loaded into memory, using "cv.imread()"
    """

    image = cv.imread(image_path)
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def binarization(image_path, par1=200, par2=230):
    """ Binarize image. Turn every pixel into black or white.

    Args:
        image_path (numpy.ndarray): Image loaded into memory, using "cv.imread()"
        par1 (int): First parameter for threshold (default = 200)
        par2 (int): Second parameter for threshold (default = 230)
    Return:
        im_bw (numpy.ndarray): binarized image
    """

    image = grayscale(image_path)

    cv.imwrite("temp/gray.png", image)

    thresh, im_bw = cv.threshold(image, par1, par2, cv.THRESH_BINARY)
    cv.imwrite("temp/bw_image.png", im_bw)
    return "temp/bw_image.png"


def noise_removal(image_path):
    """ Removes noise from image.

    Args:
        image_path (numpy.ndarray): Image loaded into memory, using "cv.imread()"

    Returns:
        image (numpy.ndarray): De-noised image
    """

    image = binarization(image_path)
    image = cv.imread(image)

    kernel = np.ones((1, 1), np.uint8)
    image = cv.dilate(image, kernel, iterations=1)
    kernel = np.ones((1, 1), np.uint8)
    image = cv.erode(image, kernel, iterations=1)
    image = cv.morphologyEx(image, cv.MORPH_CLOSE, kernel)
    image = cv.medianBlur(image, 3)

    cv.imwrite("temp/no_noise.png", image)
    return "temp/no_noise.png"


def font_thickness(image_path, mode, par1=2, par2=2, iterations=1):
    """ Modifies the thickness of fonts in image, depending on the mode that is used

    With black text on white background:
        mode = 0: The text is made thinner
        mode = 1: The text is made thicker

    With white text on black background:
        mode = 0: The text is made thicker
        mode = 1: The text is made thinner

    Args:
        image_path (numpy.ndarray): Image loaded into memory, using "cv.imread()"
        mode (int): mode that defines if text is made thinner or thicker
        par1 (int): First parameter for kernel (default = 2)
        par2 (int): Second parameter for kernel (default = 2)
        iterations (int): How many passes (default = 1)
    """

    image = noise_removal(image_path)
    image = cv.imread(image)
    image = cv.bitwise_not(image)
    kernel = np.ones((par1, par2), np.uint8)

    if mode == 1:
        image = cv.erode(image, kernel, iterations=iterations)
    elif mode == 0:
        image = cv.dilate(image, kernel, iterations=iterations)
    else:
        raise AttributeError

    image = cv.bitwise_not(image)

    cv.imwrite("temp/eroded_image.png", image)
    return "temp/eroded_image.png"


# https://becominghuman.ai/how-to-automatically-deskew-straighten-a-text-image-using-opencv-a0c30aed83df
def getSkewAngle(cvImage) -> float:
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()
    gray = cv.cvtColor(newImage, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (9, 9), 0)
    thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]

    # Apply dilate to merge text into meaningful lines/paragraphs.
    # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
    # But use smaller kernel on Y axis to separate between different blocks of text
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (30, 5))
    dilate = cv.dilate(thresh, kernel, iterations=2)

    # Find all contours
    contours, hierarchy = cv.findContours(dilate, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv.contourArea, reverse=True)
    for c in contours:
        rect = cv.boundingRect(c)
        x, y, w, h = rect
        cv.rectangle(newImage, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    print(len(contours))
    minAreaRect = cv.minAreaRect(largestContour)
    cv.imwrite("temp/boxes.jpg", newImage)
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle


# Rotate the image around its center
def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv.warpAffine(newImage, M, (w, h), flags=cv.INTER_CUBIC, borderMode=cv.BORDER_REPLICATE)
    return newImage


# Deskew image
def deskew(image_path):
    cvImage = cv.imread(image_path)
    angle = getSkewAngle(cvImage)
    fixed = rotateImage(cvImage, -1.0 * angle)
    cv.imwrite("temp/deskewed_image.png", fixed)
    return "temp/deskewed_image.png"


def remove_borders(image_path):
    """ Crops image to remove borders. Use if borders are not defined, otherwise use batch crop
    in editing software.

    Args:
        image_path (numpy.ndarray): Image loaded into memory, using "cv.imread()"
    """

    image = cv.imread(image_path)
    contours, heiarchy = cv.findContours(image, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cntsSorted = sorted(contours, key=lambda x: cv.contourArea(x))
    cnt = cntsSorted[-1]
    x, y, w, h = cv.boundingRect(cnt)
    crop = image[y:y+h, x:x+w]
    cv.imwrite("temp/croped_image.png", crop)
    return "temp/croped_image.png"


def add_borders(image_path, width=150, R=255, G=255, B=255):
    """ Add borders to image.

    Args:
        image_path (numpy.ndarray): Image loaded into memory, using "cv.imread()"
        width (int): Width of added borders. (default = 150)
    """

    image = cv.imread(image_path)

    color = [R, G, B]
    top, bottom, left, right = [width]*4

    image_with_border = cv.copyMakeBorder(image, top, bottom, left, right, cv.BORDER_CONSTANT, value=color)
    cv.imwrite("temp/image_with_border.png", image_with_border)
    return "temp/image_with_border.png"


if __name__ == "__main__":
    file_path = 'test_materials/zdj_test3.jpg'
    display(invert(file_path))
    display(binarization(file_path))
    display(noise_removal(file_path))
