"""
Credits
This application uses Open Source components. You can find the source code of their open source projects along with license information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: MegaDepth: Learning Single-View Depth Prediction from Internet Photos https://github.com/zhengqili/MegaDepth
License (MIT) https://github.com/zhengqili/MegaDepth/blob/master/LICENSE
"""

import os
import torch
import numpy as np
import torch
import os
from torch.autograd import Variable
import sys
from . import pytorch_DIW_scratch

class BaseModel():
    def name(self):
        return 'BaseModel'

    def initialize(self, opt):
        self.opt = opt
        self.gpu_ids = opt.gpu_ids
        self.isTrain = opt.isTrain
        self.Tensor = torch.FloatTensor if self.gpu_ids else torch.Tensor
        self.save_dir = str(opt.checkpoints_dir)

    def set_input(self, input):
        self.input = input

    def forward(self):
        pass

    # used in test time, no backprop
    def test(self):
        pass

    def get_image_paths(self):
        pass

    def optimize_parameters(self):
        pass

    def get_current_visuals(self):
        return self.input

    def get_current_errors(self):
        return {}

    def save(self, label):
        pass

    # helper saving function that can be used by subclasses
    def save_network(self, network, network_label, epoch_label, gpu_ids):
        save_filename = '_%s_net_%s.pth' % (epoch_label, network_label)
        torch.save(network.cpu().state_dict(), self.save_dir)

    # helper loading function that can be used by subclasses
    def load_network(self, network, network_label, epoch_label):
        save_filename = '%s_net_%s.pth' % (epoch_label, network_label)
        model = torch.load(self.save_dir)
        return model

    def update_learning_rate():
        pass

class HGModel(BaseModel):
    def name(self):
        return 'HGModel'

    def __init__(self, opt):
        BaseModel.initialize(self, opt)

        print("===========================================LOADING Hourglass NETWORK====================================================")
        model = pytorch_DIW_scratch.pytorch_DIW_scratch
        model= torch.nn.parallel.DataParallel(model, device_ids = [0,1])
        model_parameters = self.load_network(model, 'G', 'best_vanila')
        model.load_state_dict(model_parameters)
        self.netG = model.cpu()


    def batch_classify(self, z_A_arr, z_B_arr, ground_truth ):
        threashold = 1.1
        depth_ratio = torch.div(z_A_arr, z_B_arr)

        depth_ratio = depth_ratio.cpu()

        estimated_labels = torch.zeros(depth_ratio.size(0))

        estimated_labels[depth_ratio > (threashold)] = 1
        estimated_labels[depth_ratio < (1/threashold)] = -1

        diff = estimated_labels - ground_truth
        diff[diff != 0] = 1

        # error 
        inequal_error_count = diff[ground_truth != 0]
        inequal_error_count =  torch.sum(inequal_error_count)

        error_count = torch.sum(diff) #diff[diff !=0]
        # error_count = error_count.size(0)

        equal_error_count = error_count - inequal_error_count


        # total 
        total_count = depth_ratio.size(0)
        ground_truth[ground_truth !=0 ] = 1

        inequal_count_total = torch.sum(ground_truth)
        equal_total_count = total_count - inequal_count_total


        error_list = [equal_error_count, inequal_error_count, error_count]
        count_list = [equal_total_count, inequal_count_total, total_count]

        return error_list, count_list 


    def computeSDR(self, prediction_d, targets):
        #  for each image 
        total_error = [0,0,0]
        total_samples = [0,0,0]

        for i in range(0, prediction_d.size(0)):

            if targets['has_SfM_feature'][i] == False:
                continue
            
            x_A_arr = targets["sdr_xA"][i].squeeze(0)
            x_B_arr = targets["sdr_xB"][i].squeeze(0)
            y_A_arr = targets["sdr_yA"][i].squeeze(0)
            y_B_arr = targets["sdr_yB"][i].squeeze(0)

            predict_depth = torch.exp(prediction_d[i,:,:])
            predict_depth = predict_depth.squeeze(0)
            ground_truth = targets["sdr_gt"][i]

            # print(x_A_arr.size())
            # print(y_A_arr.size())

            z_A_arr = torch.gather( torch.index_select(predict_depth, 1 ,x_A_arr.cpu()) , 0, y_A_arr.view(1, -1).cpu())# predict_depth:index(2, x_A_arr):gather(1, y_A_arr:view(1, -1))
            z_B_arr = torch.gather( torch.index_select(predict_depth, 1 ,x_B_arr.cpu()) , 0, y_B_arr.view(1, -1).cpu())

            z_A_arr = z_A_arr.squeeze(0)
            z_B_arr = z_B_arr.squeeze(0)

            error_list, count_list  = self.batch_classify(z_A_arr, z_B_arr,ground_truth)

            for j in range(0,3):
                total_error[j] += error_list[j]
                total_samples[j] += count_list[j]

        return  total_error, total_samples


    def evaluate_SDR(self, input_, targets):
        input_images = Variable(input_.cpu() )
        prediction_d = self.netG.forward(input_images) 

        total_error, total_samples = self.computeSDR(prediction_d.data, targets)

        return total_error, total_samples

    def rmse_Loss(self, log_prediction_d, mask, log_gt):
        N = torch.sum(mask)
        log_d_diff = log_prediction_d - log_gt
        log_d_diff = torch.mul(log_d_diff, mask)
        s1 = torch.sum( torch.pow(log_d_diff,2) )/N 

        s2 = torch.pow(torch.sum(log_d_diff),2)/(N*N)  
        data_loss = s1 - s2

        data_loss = torch.sqrt(data_loss)

        return data_loss

    def evaluate_RMSE(self, input_images, prediction_d, targets):
        count = 0            
        total_loss = Variable(torch.FloatTensor(1))
        total_loss[0] = 0
        mask_0 = Variable(targets['mask_0'].cpu(), requires_grad = False)
        d_gt_0 = torch.log(Variable(targets['gt_0'].cpu(), requires_grad = False))

        for i in range(0, mask_0.size(0)):
 
            total_loss +=  self.rmse_Loss(prediction_d[i,:,:], mask_0[i,:,:], d_gt_0[i,:,:])
            count += 1

        return total_loss.data[0], count


    def evaluate_sc_inv(self, input_, targets):
        input_images = Variable(input_.cpu() )
        prediction_d = self.netG.forward(input_images) 
        rmse_loss , count= self.evaluate_RMSE(input_images, prediction_d, targets)

        return rmse_loss, count


    def switch_to_train(self):
        self.netG.train()

    def switch_to_eval(self):
        self.netG.eval()


def create_model(opt):
    model = None
    model = HGModel(opt)
    print("model [%s] was created" % (model.name()))
    return model