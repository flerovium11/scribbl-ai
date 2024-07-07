import numpy as np
from skimage.transform import resize
from skimage import exposure
import math


def squarify(img_array: np.array, val: float = 1) -> np.array:
    len_x, len_y = len(img_array[0]), len(img_array)
    # calculate how many rows have to be added
    diff_x, diff_y = max(0, len_y - len_x), max(0, len_x - len_y)
    pad_t, pad_r, pad_b, pad_l = math.ceil(
        diff_y / 2), math.floor(diff_x / 2), math.floor(diff_y / 2), math.ceil(diff_x / 2)
    # make the array square shaped
    img_array = np.pad(img_array, ((pad_t, pad_b), (pad_l, pad_r)),
                       mode='constant', constant_values=val)
    return img_array


def motive_crop(img_array: np.array, padding: int, empty_val: float = 1) -> np.array:
    # Find indices where non-empty values start and end from each side
    top = np.argmax(np.any(img_array != empty_val, axis=1))
    bottom = np.argmax(np.any(img_array[::-1] != empty_val, axis=1))
    left = np.argmax(np.any(img_array != empty_val, axis=0))
    right = np.argmax(np.any(img_array[:, ::-1] != empty_val, axis=0))

    # Crop the array based on non-empty values
    img_array = img_array[top:img_array.shape[0] -
                          bottom, left:img_array.shape[1]-right]

    # Pad the cropped array
    img_array = np.pad(img_array, ((padding, padding), (padding,
                       padding)), mode='constant', constant_values=empty_val)

    return img_array


def format_for_ai(img_array: np.array) -> np.array:
    img_array = resize(np.flip(np.rot90(np.array(img_array),
                       k=-1), axis=1), (28, 28), anti_aliasing=True)
    img_array = motive_crop(img_array, 0, 0)
    img_array = squarify(img_array, 0)
    # img_array = exposure.rescale_intensity(img_array, in_range=(0, 1))
    return img_array
