import cv2 as cv
import detect_words as det
import os
from alive_progress import alive_bar
import datetime
import srt
from pathlib import Path


def count_frames(video):
    """ Counts how many frames there are in a video
    
    Args:
        video (cv2.VideoCapture): Video loaded via cv2
    Returns:
        total (int): Number of frames from a video
    """

    (major_ver, minor_ver, subminor_ver) = cv.__version__.split('.')
    if int(major_ver) < 3:
        total = int(video.get(cv.cv.CV_CAP_PROP_FRAME_COUNT))
    else:
        total = int(video.get(cv.CAP_PROP_FRAME_COUNT))
    return total


def get_time(video):
    """ Returns the time of a frame in a video

    Args:
        video (cv2.VideoCapture): Video loaded via cv2
    Returns:
        time (list): list of the seconds and milliseconds of the frame
    """

    milliseconds = video.get(cv.CAP_PROP_POS_MSEC)
    seconds, milliseconds = divmod(milliseconds, 1000)
    microseconds = milliseconds * 1000

    time = [seconds, microseconds]
    return time


def save_frame(frame, index):
    """ Saves frame in a folder and returns filename

    Args:
        frame (numpy.ndarray): information about frame (cv2)
        index (int): index of frame
    Returns:
        name (str): name of frame file
    """

    name = f'./frames_from_video/frame{str(index)}.jpg'
    cv.imwrite(name, frame)
    return name


def load_subtitles(subtitles_path):
    """ Loads subtitles from .txt file, removes end spaces and end \n symbol

    Args:
        subtitles_path (str): path to subtitle text file
    Returns:
        subtitles (list): list of individual words from the sentences
        native_subtitles (list): list of whole sentences
    """

    file = open(subtitles_path, "r+", encoding="utf8")

    # removes blank lines
    temp = []
    subtitles = []
    for line in file:
        if repr(line) == repr('\n'):
            block = ''.join(temp)
            subtitles.append(block)
            temp = []
        else:
            temp.append(line)

    block = ''.join(temp)
    subtitles.append(block)

    # removes the new-line character from the back
    for element in subtitles:
        subtitles[subtitles.index(element)] = element.rstrip(' \n')
    native_subtitles = list(subtitles)

    # splits the sentence into list of words
    for element in subtitles:
        split = element.split()
        temp = []
        for word in split:
            if "-" in word:
                word = word.split("-")
                for split_word in word:
                    temp.append(split_word)
            else:
                temp.append(word)
        subtitles[subtitles.index(element)] = temp

    file.close()
    return subtitles, native_subtitles


def solo_clear_ocr(ocr_text):
    """ Clears OCR text. Deletes all "wrong" characters. Characters that are not letters.
        Prepares text for recovery file.

    Args:
        ocr_text (list): Text that the OCR found
    Returns:
        clear_ocr (list): Clear OCR text
    """

    wrong_char = [",", ".", "?", "/", "\\", "<", ">", ";", ":", "'", "|", "[", "]", "{", "}", "!",
                  "@", "#", "$", "%", "^", "&", "*", "(", ")", "=", "+", "`", "~", "-"]
    clear_ocr = []
    for element in ocr_text:
        element = element.lower()
        if element not in wrong_char:
            for char in wrong_char:
                element = element.rstrip(char)
                element = element.lstrip(char)
            clear_ocr.append(element)

    return clear_ocr


def key_words(current_sub, next_sub):
    """ Finds words that are in the current subtitle, but are not in the next one.

    Args:
        current_sub (list): list of words in the current subtitle
        next_sub (list): list of words in the next subtitle

    Returns:
        words (list): list of "keywords"
    """

    # creates a list of same words
    similar_words = []
    for element in current_sub:
        if element in next_sub:
            similar_words.append(element)

    # removes same words, leaving only keywords
    for element in similar_words:
        current_sub.remove(element)
    words = current_sub

    return words


def text_prep(ocr_text, subtitles, text_index):
    """ Clears needed text. Deletes all "wrong" characters. Characters that are not words.

    Args:
        ocr_text (list): Text that the OCR found
        subtitles (list): Loaded subtitles
        text_index (int): Index of subtitle
    Returns:
        clear_current (list): Clear current subtitle
        clear_next (list): Clear next subtitle
        clear_ocr (list): Clear OCR text
    """

    current_sub = subtitles[text_index]
    next_sub = subtitles[text_index+1]
    wrong_char = [",", ".", "?", "/", "\\", "<", ">", ";", ":", "'", "|", "[", "]", "{", "}", "!",
                  "@", "#", "$", "%", "^", "&", "*", "(", ")", "=", "+", "`", "~", "-"]

    # clears current subtitle
    clear_current = []
    for element in current_sub:
        element = element.lower()
        if element not in wrong_char:
            for char in wrong_char:
                element = element.rstrip(char)
                element = element.lstrip(char)
            clear_current.append(element)

    # clears next subtitle
    clear_next = []
    for element in next_sub:
        element = element.lower()
        if element not in wrong_char:
            for char in wrong_char:
                element = element.rstrip(char)
                element = element.lstrip(char)
            clear_next.append(element)

    # clear OCR text
    clear_ocr = []
    for element in ocr_text:
        element = element.lower()
        if element not in wrong_char:
            for char in wrong_char:
                element = element.rstrip(char)
                element = element.lstrip(char)
            clear_ocr.append(element)

    return clear_current, clear_next, clear_ocr


def how_similar_ocr(clear_ocr_text, current_sub):
    """ Determines how similar the OCR text is to the current subtitle

    Args:
        clear_ocr_text (list): List of current OCR text
        current_sub (list): List of current subtitle text
    Returns:
        how_similar (float): Percentage of how similar the OCR is to the subtitle
    """

    temp_ocr = list(clear_ocr_text)
    similar_words = 0
    for element in current_sub:
        if element in temp_ocr:
            temp_ocr.remove(element)
            similar_words += 1
    how_similar = (similar_words * 100) / len(current_sub)
    return how_similar


def how_similar_next(current_sub, next_sub):
    """ Determines how similar the current subtitle is to the next subtitle

    Args:
        current_sub (list): List of current subtitle text
        next_sub (list): List of next subtitle text

    Returns:
        how_similar (float): Percentage of how similar the current subtitle is to the next subtitle
    """

    similar_words = 0
    for element in current_sub:
        if element in next_sub:
            next_sub.remove(element)
            similar_words += 1
    how_similar = (similar_words * 100) / len(current_sub)

    return how_similar


def is_similar(ocr_text, text_index, subtitles, acceptable_value=50):
    """ Decides if the OCR is similar to the current subtitle.
    If current subtitle is not similar to next one - decides based only on similarity.
    If current subtitle is similar to next one - decides based on similarity and keywords.
    Keywords are words that are in the current subtitle, but are not in the next one.

    Args:
        ocr_text (list): Current OCR text
        text_index (int): Index of current subtitle
        subtitles (list): List of all subtitles
        acceptable_value (int): Percentage from where the OCR text is considered similar to subtitle
    Returns:
        True (bool): If similar and (keywords are in the current subtitle)
        False (bool: If not similar or (no keywords in the current subtitle)
    """

    # prepares the text and finds keywords
    current_sub, next_sub, clear_ocr_text = text_prep(ocr_text, subtitles, text_index)
    key_word = key_words(current_sub, next_sub)

    # finds how similar the OCR is to the subtitle and how similar the current subtitle is to the next one
    how_similar_to_ocr = how_similar_ocr(clear_ocr_text, current_sub)
    how_similar_to_next = how_similar_next(current_sub, next_sub)

    # counts how many keywords appear in the OCR
    keys_in_ocr = 0
    temp_ocr = list(clear_ocr_text)
    for word in key_word:
        if word in temp_ocr:
            temp_ocr.remove(word)
            keys_in_ocr += 1

    if how_similar_to_next >= 70:
        if how_similar_to_ocr >= acceptable_value and keys_in_ocr == len(key_word):
            return True
        else:
            return False
    else:
        if how_similar_to_ocr >= acceptable_value:
            return True
        else:
            return False


def create_srt(frame_info):
    """ Creates srt file, from collected frame info

    Args:
        frame_info (list): list of information about start and end frames
    """

    file = open("subtitles/Finished_subtitles.txt", "w+", encoding="utf8")
    subtitles = []

    for element in frame_info:
        start = datetime.timedelta(seconds=element[0][0], microseconds=element[0][1])
        end = datetime.timedelta(seconds=element[1][0], microseconds=element[1][1])
        index = element[2]
        content = element[3]

        subtitle = srt.Subtitle(index=index, start=start, end=end, content=content)
        subtitles.append(subtitle)

    text = srt.compose(subtitles)
    file.write(text)
    file.close()

    if os.path.exists("subtitles/Finished_subtitles.srt"):
        os.remove("subtitles/Finished_subtitles.srt")
    p = Path("subtitles/Finished_subtitles.txt")
    p.rename(p.with_suffix('.srt'))
    file.close()


def save_recovery(recovery_file, text_index, ocr_text, name_of_frame, time):
    """ Creates recovery file, containing all information, for later recovery
    of collected data. File can be read with the recovery.py program, in which
    all parameters can be change, but no new OCR is needed

    Args:
        recovery_file: opened recovery file
        text_index (int): index of current subtitle
        ocr_text (list): clear OCR text of current frame
        name_of_frame (str): name of current frame
        time (list): list containing time of frame
    """

    ocr_text = ' '.join(ocr_text)
    recovery_info = [text_index, ocr_text, name_of_frame, time[0], time[1]]

    str_info = '|'.join([str(elem) for elem in recovery_info])
    recovery_file.write(str_info)
    recovery_file.write("\n")


def main(video_path, subtitles_path):
    video = cv.VideoCapture(video_path)
    subtitles, native_subtitles = load_subtitles(subtitles_path)
    recovery_file = open("subtitles/recovery_file.txt", "w+", encoding="utf8")

    if not os.path.exists('frames_from_video'):
        os.makedirs('frames_from_video')

    with alive_bar(count_frames(video), force_tty=True) as bar:
        frame_index = 0
        text_index = 0
        time_of_frame = []
        frame_info = []
        while True:
            ret, frame = video.read()
            time = get_time(video)
            if not ret:
                break
            if frame_index % 2 == 0:
                name_of_frame = save_frame(frame, frame_index)
                ocr_text = det.ocr(name_of_frame)

                if len(ocr_text) != 0:
                    del ocr_text[0]

                    if text_index + 1 < len(subtitles):
                        similar = is_similar(ocr_text, text_index, subtitles)

                    save_recovery(recovery_file, text_index, solo_clear_ocr(ocr_text), name_of_frame, time)

                    if similar is True:
                        time_of_frame.append(time)
                    elif len(time_of_frame) != 0:
                        frame_info.append([time_of_frame[0], time_of_frame[-1], text_index, native_subtitles[text_index]])
                        time_of_frame = []
                        text_index += 1

                        if text_index + 1 < len(subtitles):
                            similar = is_similar(ocr_text, text_index, subtitles)
                        if similar is True:
                            time_of_frame.append(time)

            bar()
            frame_index += 1

    create_srt(frame_info)
    recovery_file.close()
    video.release()


if __name__ == "__main__":
    test_video = "subtitles/film_test.mp4"
    test_subtitles = "subtitles/subtitles.txt"
    main(test_video, test_subtitles)
