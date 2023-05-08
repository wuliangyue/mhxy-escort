import cv2
import numpy
import numpy as np
from skimage.metrics import structural_similarity

DEBUG = False


def find_template(im_source, im_search, threshold=0.5, rgb=False, bgremove=False, mask=None, method=None):
    """
    @return find location
    if not found; return None
    """
    result = find_all_template(im_source, im_search, threshold, 1, rgb, bgremove, mask, method)
    return result[0] if result else None


def find_all_template(im_source, im_search, threshold=0.5, maxcnt=0, rgb=False, bgremove=False, mask=None, method=None):
    """
    Locate image position with cv2.templateFind

    Use pixel match to find pictures.

    Args:
        im_source(string): 图像、素材
        im_search(string): 需要查找的图片
        threshold: 阈值，当相识度小于该阈值的时候，就忽略掉

    Returns:
        A tuple of found [(point, score), ...]

    Raises:
        IOError: when file read error
        :param method:
        :param bgremove:
        :param rgb:
        :param im_source:
        :param im_search:
        :param threshold:
        :param maxcnt:
    """
    # print(type(im_source), type(im_search), type(mask))
    # method = cv2.TM_CCORR_NORMED
    # method = cv2.TM_SQDIFF_NORMED
    cv2_method = cv2.TM_CCOEFF_NORMED
    if method is not None:
        cv2_method = method

    if rgb:
        s_bgr = cv2.split(im_search)  # Blue Green Red
        i_bgr = cv2.split(im_source)
        weight = (0.3, 0.3, 0.4)
        resbgr = [0, 0, 0]
        for i in range(3):  # bgr
            resbgr[i] = cv2.matchTemplate(i_bgr[i], s_bgr[i], cv2_method, mask=mask)
        res = resbgr[0] * weight[0] + resbgr[1] * weight[1] + resbgr[2] * weight[2]
    else:
        s_gray = cv2.cvtColor(im_search, cv2.COLOR_BGR2GRAY)
        i_gray = cv2.cvtColor(im_source, cv2.COLOR_BGR2GRAY)
        # 边界提取(来实现背景去除的功能)
        if bgremove:
            s_gray = cv2.Canny(s_gray, 100, 200)
            i_gray = cv2.Canny(i_gray, 100, 200)

        res = cv2.matchTemplate(i_gray, s_gray, cv2_method, mask=mask)
    w, h = im_search.shape[1], im_search.shape[0]

    result = []
    while True:
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if cv2_method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        if DEBUG:
            print('templmatch_value(thresh:%.1f) = %.3f' % (threshold, max_val))  # not show debug
        if max_val < threshold:
            break
        # calculator middle point
        middle_point = (top_left[0] + w / 2, top_left[1] + h / 2)
        result.append(dict(
            result=middle_point,
            rectangle=(top_left, (top_left[0], top_left[1] + h), (top_left[0] + w, top_left[1]),
                       (top_left[0] + w, top_left[1] + h)),
            confidence=max_val
        ))
        if maxcnt and len(result) >= maxcnt:
            break
        # floodfill the already found area
        cv2.floodFill(res, None, max_loc, (-1000,), max_val - threshold + 0.1, 1, flags=cv2.FLOODFILL_FIXED_RANGE)
    return result


def match_img(img_src, img_obj, phone_x, phone_y, confidence_value=0.0, mask=None, method=None):
    """
    :param img_src: 需要查询的图片
    :param img_obj: 查询的模板图
    :param phone_x:
    :param phone_y:
    :param confidence_value: 阈值
    :param mask: 掩码图，适用于非矩形模板匹配
    :param method: 模板匹配使用的方法，默认为None
    :return:
    """
    if not isinstance(img_src, numpy.ndarray):
        img_src = cv2.imread(img_src)
    if not isinstance(img_obj, numpy.ndarray):
        img_obj = cv2.imread(img_obj)
    if mask is None:
        img_mask = mask
    else:
        if not isinstance(mask, numpy.ndarray):
            img_mask = cv2.imread(mask, 0)
        else:
            img_mask = mask
    match_result = find_template(img_src, img_obj, confidence_value, rgb=False, mask=img_mask, method=method)
    if match_result is not None:
        match_result['shape'] = (img_src.shape[1], img_src.shape[0])  # 0为高，1为宽
        x, y = match_result['result']  # 标准图中小图位置x,y
        shape_x, shape_y = tuple(map(int, match_result['shape']))  # 标准图中x,y
        position_x, position_y = int(phone_x * (x / shape_x)), int(phone_y * (y / shape_y))
    else:
        return None, None, None, None
    return position_x, position_y, str(match_result['confidence'])[:4], match_result


def match_all_img(img_src, img_obj, phone_x, phone_y, confidence_value=0.0, mask=None,
                  method=None):  # img_src=原始图像，img_obj=待查找的图片
    if not isinstance(img_src, numpy.ndarray):
        img_src = cv2.imread(img_src)
    if not isinstance(img_obj, numpy.ndarray):
        img_obj = cv2.imread(img_obj)
    if mask is None:
        img_mask = mask
    else:
        if not isinstance(mask, numpy.ndarray):
            img_mask = cv2.imread(mask, cv2.COLOR_BGR2GRAY)
        else:
            img_mask = mask
    match_result = find_all_template(img_src, img_obj, confidence_value, maxcnt=1, rgb=False, mask=img_mask,
                                     method=method)
    print(match_result)
    return match_result


def take_red_line(result, image, name):
    """
    模板匹配后的结果进行二次绘图，标出模板匹配位置
    :param result:
    :param image: 原图片
    :param name: 保存的图片名
    :return:
    """
    rectangle = result[3]["rectangle"]
    x_min = rectangle[0][0]
    y_min = rectangle[0][1]
    x_max = rectangle[2][0]
    y_max = rectangle[3][1]

    if not isinstance(image, numpy.ndarray):
        image = cv2.imread(image)
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 0, 255), 3)
    cv2.imwrite(name, image)


def compare_image(image_a, image_b, channel_axis=True):
    """
    对图片A 和 图片B的相似度进行计算，0为最低，1为最大
    :param image_a: 图片A
    :param image_b: 图片B
    :param channel_axis:
    :return: 相似度得分
    """
    if not isinstance(image_a, numpy.ndarray):
        image_a = cv2.imread(image_a)
    if not isinstance(image_b, numpy.ndarray):
        image_b = cv2.imread(image_b)
    gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)
    (score, diff) = structural_similarity(gray_a, gray_b, full=True, channel_axis=channel_axis)
    return score


def crop_image_data(image_data, left_up, right_down):
    """
    :param image_data: 裁剪的图片，类型为numpy.ndarray
    :param left_up: 裁剪的左顶点
    :param right_down: 裁剪的右顶点
    :return:裁剪后的图像
    """
    if not isinstance(image_data, np.ndarray):
        image_data = cv2.imread(image_data)
    img = image_data[int(left_up[1]):int(right_down[1]), int(left_up[0]):int(right_down[0])]
    return img



