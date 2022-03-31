def crop_32x(img):
    """ Crop image to 32x width/height """
    new_height = int(img.shape[0] / 32) * 32
    new_width = int(img.shape[1] / 32) * 32
    return img[0:new_height, 0:new_width, :]   