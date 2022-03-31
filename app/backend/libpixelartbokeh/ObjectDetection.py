import torch
import torchvision
from PIL import Image
import numpy as np
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

class ObejctDetection():
  def __init__(self, checkpoint_path, hidden=1024):
    """
    Model Initialization.
    Input: path to the checkpoint, under /content/drive/MyDrive/ECE496 Team/object_detection/maskrcnn_checkpoints/

    NOTE: Some models have different hidden layers, adjustment needed!!!
    """
    self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, 2)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask,
                              hidden, 2)
    model.to(self.device)
    checkpoint = torch.load(checkpoint_path, map_location=self.device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    self.model = model
    self.transform = torchvision.transforms.ToTensor()
  
  def predict(self, img):
    """
    Predict a single image
    Input: image or numpy array
    Output: A list of 0-1 masks
    """
    tensor = self.transform(img)
    with torch.no_grad():
        prediction = self.model([tensor.to(self.device)])
        masks = ((prediction[0]['masks']).cpu().numpy() * 255.).astype(np.uint8)
        confidences = prediction[0]['scores'].cpu().numpy()
    return masks, confidences