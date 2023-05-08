import win32gui

import config


def get_all_windows():
    """
    获取所有窗口句柄操作
    :return: List 所有窗口的句柄
    """
    hwnd_list = []
    win32gui.EnumWindows(lambda hWnd, param: param.append(hWnd), hwnd_list)
    return hwnd_list


def get_all_child_window(parent):
    """
    获得parent的所有子窗口句柄 返回子窗口句柄列表
    :param parent: 父句柄
    :return:
    """
    if not parent:
        return
    hwnd_child_list = []
    win32gui.EnumChildWindows(
        # win32gui.FindWindowEx(
        parent, lambda hwnd, param: param.append(hwnd), hwnd_child_list)
    return hwnd_child_list


def get_window(name):
    """
    找到所有的窗口，返回找到的第一个梦幻西游窗口(包含tab)
    :return:
    """
    hwnd_list = get_all_windows()
    for hWnd in hwnd_list:
        title = win32gui.GetWindowText(hWnd)
        if name in title and "聊天窗口" not in title:
            return hWnd
    raise Exception(f"Can't find window , please check {name} is opened")


def get_mhxy_hwnd(use_id=config.main_user):
    hwnd = get_window("梦幻西游 ONLINE")
    hwnd_list = get_all_child_window(hwnd)
    game_hwnd = 0
    for hWnd in hwnd_list:
        title = win32gui.GetWindowText(hWnd)
        if str(use_id) in title:
            return hWnd
        if "梦幻西游 ONLINE" in title:
            game_hwnd = hWnd
    return game_hwnd


def set_parent_foreground(child):
    hwnd = get_window(win32gui.GetWindowText(child))
    win32gui.SetForegroundWindow(hwnd)


WINDOW_ID = get_mhxy_hwnd()
NAME = win32gui.GetWindowText(WINDOW_ID).split('-')[-1].split('[')[0].strip()
print(NAME)