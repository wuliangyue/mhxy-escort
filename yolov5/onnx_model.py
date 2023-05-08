# coding=utf-8
import os
import uuid
import cv2
import numpy as np
import onnxruntime
import torch
import torchvision
import time
import random

from game_common_action.mouse import move, move_click
from yolov5.utils.general import non_max_suppression


class YOLOV5_ONNX(object):
    def __init__(self, onnx_path):
        '''初始化onnx'''
        self.onnx_session = onnxruntime.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        print(onnxruntime.get_device())
        self.input_name = self.get_input_name()
        self.output_name = self.get_output_name()
        self.classes = ['player', 'robber', 'bandit', 'gambler', 'horseface', 'corpse',
                        "vampire", "robbername", "ghostname", "skeleton monster", "banditname",
                        "wild ghost", "tauren", "purple ghost", "general", "fiend"]

    def get_input_name(self):
        '''获取输入节点名称'''
        input_name = []
        for node in self.onnx_session.get_inputs():
            input_name.append(node.name)

        return input_name

    def get_output_name(self):
        '''获取输出节点名称'''
        output_name = []
        for node in self.onnx_session.get_outputs():
            output_name.append(node.name)

        return output_name

    def get_input_feed(self, image_tensor):
        '''获取输入tensor'''
        input_feed = {}
        for name in self.input_name:
            input_feed[name] = image_tensor

        return input_feed

    def letterbox(self, img, new_shape=(640, 640), color=(114, 114, 114), auto=False, scaleFill=False, scaleup=True,
                  stride=32):
        '''图片归一化'''
        # Resize and pad image while meeting stride-multiple constraints
        shape = img.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better test mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios

        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
        elif scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))

        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return img, ratio, (dw, dh)

    def xywh2xyxy(self, x):
        # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
        y = np.copy(x)

        y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
        y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
        y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
        y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y

        return y

    def nms(self, prediction, conf_thres=0.1, iou_thres=0.6, agnostic=False):
        if prediction.dtype is torch.float16:
            prediction = prediction.float()  # to FP32
        xc = prediction[..., 4] > conf_thres  # candidates
        min_wh, max_wh = 2, 4096  # (pixels) minimum and maximum box width and height
        max_det = 300  # maximum number of detections per image
        output = [None] * prediction.shape[0]
        for xi, x in enumerate(prediction):  # image index, image inference
            x = x[xc[xi]]  # confidence
            if not x.shape[0]:
                continue

            x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf
            box = self.xywh2xyxy(x[:, :4])

            conf, j = x[:, 5:].max(1, keepdim=True)
            x = torch.cat((torch.tensor(box), conf, j.float()), 1)[conf.view(-1) > conf_thres]
            n = x.shape[0]  # number of boxes
            if not n:
                continue
            c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
            boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
            i = torchvision.ops.boxes.nms(boxes, scores, iou_thres)
            if i.shape[0] > max_det:  # limit detections
                i = i[:max_det]
            output[xi] = x[i]

        return output

    def clip_coords(self, boxes, img_shape):
        '''查看是否越界'''
        # Clip bounding xyxy bounding boxes to image shape (height, width)
        boxes[:, 0].clamp_(0, img_shape[1])  # x1
        boxes[:, 1].clamp_(0, img_shape[0])  # y1
        boxes[:, 2].clamp_(0, img_shape[1])  # x2
        boxes[:, 3].clamp_(0, img_shape[0])  # y2

    def scale_coords(self, img1_shape, coords, img0_shape, ratio_pad=None):
        '''
        坐标对应到原始图像上，反操作：减去pad，除以最小缩放比例
        :param img1_shape: 输入尺寸
        :param coords: 输入坐标
        :param img0_shape: 映射的尺寸
        :param ratio_pad:
        :return:
        '''

        # Rescale coords (xyxy) from img1_shape to img0_shape
        if ratio_pad is None:  # calculate from img0_shape
            gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new,计算缩放比率
            pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (
                    img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding ，计算扩充的尺寸
        else:
            gain = ratio_pad[0][0]
            pad = ratio_pad[1]

        coords[:, [0, 2]] -= pad[0]  # x padding，减去x方向上的扩充
        coords[:, [1, 3]] -= pad[1]  # y padding，减去y方向上的扩充
        coords[:, :4] /= gain  # 将box坐标对应到原始图像上
        self.clip_coords(coords, img0_shape)  # 边界检查
        return coords

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def infer(self, img_path):
        '''执行前向操作预测输出'''
        # 超参数设置
        img_size = (640, 640)  # 图片缩放大小
        # 读取图片
        if not isinstance(img_path, np.ndarray):
            src_img = cv2.imread(img_path)
        else:
            src_img = img_path
        start = time.time()
        src_size = src_img.shape[:2]

        # 图片填充并归一化
        img = self.letterbox(src_img, img_size, stride=32)[0]

        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        # 归一化
        img = img.astype(dtype=np.float32)
        img /= 255.0

        # # BGR to RGB
        # img = img[:, :, ::-1].transpose(2, 0, 1)
        # img = np.ascontiguousarray(img)

        # 维度扩张
        img = np.expand_dims(img, axis=0)
        # print('img resuming: ', time.time() - start)
        # 前向推理
        # start=time.time()
        input_feed = self.get_input_feed(img)
        # ort_inputs = {self.onnx_session.get_inputs()[0].name: input_feed[None].numpy()}
        pred = torch.tensor(self.onnx_session.run(None, input_feed)[0])
        results = non_max_suppression(pred, 0.5, 0.5)
        print('onnx resuming: ', time.time() - start)
        # pred=self.onnx_session.run(output_names=self.output_name,input_feed=input_feed)

        # 映射到原始图像
        img_shape = img.shape[2:]
        for det in results:  # detections per image
            if det is not None and len(det):
                det[:, :4] = self.scale_coords(img_shape, det[:, :4], src_size).round()
        if det is not None and len(det):
            # print(det)
            self.draw(src_img, det)
        return det

    def plot_one_box(self, x, img, color=None, label=None, line_thickness=None):
        # Plots one bounding box on image img
        tl = line_thickness or round(0.002 * (img.shape[0] + img.shape[1]) / 2) + 1  # line/font thickness
        color = color or [random.randint(0, 255) for _ in range(3)]
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        cv2.rectangle(img, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)

        if label:
            tf = max(tl - 1, 1)  # font thickness
            t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(img, c1, c2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(img, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

    def find_class(self, name_list, result):
        index_list = []
        for name in name_list:
            index = self.classes.index(name)
            index_list.append(index)
        temp = []
        if result is not None and len(result):
            for *xyxy, conf, cls in result:
                if cls in index_list:
                    temp.append(xyxy)
        return temp

    def find_class_center(self, name, result):
        temp_result = self.find_class(name, result)
        temp = []
        for det in temp_result:
            x1, y1, x2, y2 = int(det[0]), int(det[1]), int(det[2]), int(det[3])
            x_center = int((x1 + x2) / 2)
            y_center = int((y1 + y2) / 2)
            temp.append((x_center, y_center))
        return temp

    def draw(self, img, boxinfo):
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.classes))]
        for *xyxy, conf, cls in boxinfo:
            label = '%s %.2f' % (self.classes[int(cls)], conf)
            print(self.classes[int(cls)], conf)
            # print('xyxy: ', xyxy)
            self.plot_one_box(xyxy, img, label=label, color=colors[int(cls)], line_thickness=1)

        # cv2.namedWindow("dst",0)
        # cv2.imshow("dst", img)
        cv2.imwrite(f"1.jpg", img)
        # cv2.waitKey(0)
        # cv2.imencode('.jpg', img)[1].tofile(os.path.join(dst, id + ".jpg"))
        return 0


def find_point(target_xy, now, player):
    ns = player
    bias_x = target_xy[0] - now[0]
    bias_y = target_xy[1] - now[1]
    print(f"target_xy: {target_xy}, now: {now}, player:{player} bias {bias_x}, {bias_y}")
    return ns[0][0] + bias_x*25,  ns[0][1] + 50 - bias_y*25

MHXY_MODEL = YOLOV5_ONNX(onnx_path=r"D:\study-ai\yolov5\best.onnx")

if __name__ == "__main__":
    import grab_screen
    import common

    k = MHXY_MODEL.infer(grab_screen.winShot(common.get_mhxy_window_by_id()))
    g = MHXY_MODEL.find_class_center(["player"], k)
    # 100 = 4
    # move_click(g[0][0]-100, g[0][1]+50)
    # 77 138 - 81 135

    point = find_point((99, 73), (102, 79), g)
    move(point[0], point[1]-50)
