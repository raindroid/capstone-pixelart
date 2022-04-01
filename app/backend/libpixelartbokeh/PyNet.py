import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

import tensorflow as tff
import tensorflow.compat.v1 as tf

from .models.PyNETModel import createPyNet
from .helper import crop_32x

tf.compat.v1.reset_default_graph()
tf.disable_v2_behavior()
import numpy as np
from PIL import Image

class PyNet():
    def __init__(self, checkpoint_path, meta="./libpixelartbokeh/models/PyNET_model.meta"):
        self.checkpoint_path = checkpoint_path
        self.meta = meta

    def predict(self, img, mask=None):
        """
        Predict a single image
        Input: image or numpy array
        Output: Blurred image
        """
        if img.shape[-1] > 3: img = img[..., :3]
        if np.max(img) > 1.0: img = img.astype(np.float32) / 255.
        img = crop_32x(img)
        I = np.zeros((1, img.shape[0], img.shape[1], 4))
        
        if mask is not None and np.max(mask) > 1: mask = mask.astype(np.float32) / 255.
        if mask is not None:
            mask = (mask * 255.).astype(np.uint8)
            mask = np.array(Image.fromarray(mask).resize((img.shape[-2], img.shape[-3]))) / 255.
            mask = np.squeeze(crop_32x(mask[..., np.newaxis]), 2)
            
        I[0][:, :, :3] = img.astype(np.float32)
        self.net = createPyNet()
        with tf.Session() as sess:
            saver = tf.train.Saver()
            saver.restore(sess, self.checkpoint_path)
            x, bokeh_image = self.net
            if mask is not None: I[0][..., 3] = mask
            result_img = sess.run(bokeh_image, feed_dict={x: I})
            sess.close()
        
        return result_img
        