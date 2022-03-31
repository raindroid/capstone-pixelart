from tabnanny import check
from .models.MDMModel import create_model
import torch
import sys
from torch.autograd import Variable
from PIL import Image
from skimage.transform import resize as skresize
import os
import numpy as np
from pathlib import Path

max_resize_ratio = 0.5
max_image_width = 1080


class MyOpt(object):
    pass

def get_test_opt(checkpoint="./pretrain/depthmap.pth"):
    opt = MyOpt()

    attrs = (
        ("batchSize", 1),
        ("beta1", 0.5),
        ("checkpoints_dir", checkpoint),
        ("continue_train", False),
        ("display_freq", 100),
        ("display_id", 1),
        ("display_winsize", 256),
        ("fineSize", 256),
        ("gpu_ids", [0]),
        ("identity", 0.0),
        ("input_nc", 3),
        ("isTrain", True),
        ("lambda_A", 10.0),
        ("lambda_B", 10.0),
        ("loadSize", 286),
        ("lr", 0.0002),
        ("max_dataset_size", float("inf")),
        ("model", "pix2pix"),
        ("nThreads", 2),
        ("name", "test_local"),
        ("ndf", 64),
        ("ngf", 64),
        ("niter", 100),
        ("niter_decay", 100),
        ("no_flip", False),
        ("no_html", False),
        ("no_lsgan", False),
        ("norm", "instance"),
        ("output_nc", 3),
        ("phase", "train"),
        ("pool_size", 50),
        ("print_freq", 100),
        ("save_epoch_freq", 5),
        ("save_latest_freq", 5000),
        ("serial_batches", False),
        ("use_dropout", False),
        ("which_epoch", "latest"),
        ("which_model_netG", "unet_256"),
    )

    for attr_name, attr_value in attrs:
        setattr(opt, attr_name, attr_value)

    return opt

class MegaDepthMap(object):
    def __init__(self, checkpoint_path):
        opt = get_test_opt(checkpoint_path)
        model = create_model(opt)
        model.switch_to_eval()
        
        self.model = model
        
    def predict(self, img):
        if img.shape[-1] > 3: img = img[..., :3]
        if np.max(img) > 1.0: img = img.astype(np.float32) / 255.0
            
        resize_ratio = min(
            1. / (img.shape[1] / max_image_width), max_resize_ratio)
        input_height = int(img.shape[0] * resize_ratio / 16) * 16
        input_width = int(img.shape[1] * resize_ratio / 16) * 16

        img = skresize(img, (input_height, input_width), order=1)
        input_img = torch.from_numpy(np.transpose(
            img, (2, 0, 1))).contiguous().float()
        input_img = input_img.unsqueeze(0)

        input_images = Variable(input_img)
        pred_log_depth = self.model.netG.forward(input_images)
        pred_log_depth = torch.squeeze(pred_log_depth)

        pred_depth = torch.exp(pred_log_depth)

        # visualize prediction using inverse depth, so that we don't need sky segmentation (if you want to use RGB map for visualization, \
        # you have to run semantic segmentation to mask the sky first since the depth of sky is random from CNN)
        pred_inv_depth = 1/pred_depth
        pred_inv_depth = pred_inv_depth.data.cpu().numpy()
        # you might also use percentile for better visualization
        pred_inv_depth = pred_inv_depth/np.amax(pred_inv_depth)
        
        return (pred_inv_depth * 255.).astype(np.uint8)
