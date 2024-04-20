import numpy as np
import math

def squarify(img_array:np.array, val:float=1)->np.array:
    len_x, len_y = len(img_array[0]), len(img_array)
    diff_x, diff_y = max(0, len_y - len_x), max(0, len_x - len_y) # calculate how many rows have to be added
    pad_t, pad_r, pad_b, pad_l = math.ceil(diff_y / 2), math.floor(diff_x / 2), math.floor(diff_y / 2), math.ceil(diff_x / 2)
    # make the array square shaped
    img_array = np.pad(img_array, ((pad_t, pad_b), (pad_l, pad_r)), mode='constant', constant_values=val)
    return img_array

def motive_crop(img_array:np.array, padding:int, empty_val:float=1)->np.array:
    # Find indices where non-empty values start and end from each side
    top = np.argmax(np.any(img_array != empty_val, axis=1))
    bottom = np.argmax(np.any(img_array[::-1] != empty_val, axis=1))
    left = np.argmax(np.any(img_array != empty_val, axis=0))
    right = np.argmax(np.any(img_array[:, ::-1] != empty_val, axis=0))

    # Crop the array based on non-empty values
    img_array = img_array[top:img_array.shape[0]-bottom, left:img_array.shape[1]-right]

    # Pad the cropped array
    img_array = np.pad(img_array, ((padding, padding), (padding, padding)), mode='constant', constant_values=empty_val)

    return img_array
