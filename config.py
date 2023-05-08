import os

root_dir = os.path.abspath(os.path.dirname(__file__))
# **************** you can custom  this settings *************************************
main_user = 3052589
gpu = False
player_action = "q"
bb_action = "a"

# **************** please don't change this constant directory ***********************
# hover_save_path
hover_list = [os.path.join(root_dir, rf'src\runs_data\{i + 1}.png') for i in range(4)]
# train val
train_dir = os.path.join(root_dir, rf'src\runs_data\train')
# val
validation_dir = os.path.join(root_dir, rf'src\runs_data\validation')
# yolov5_repo
yolov5_repo = os.path.join(root_dir, rf'yolov5')
#
runs_data = os.path.join(root_dir, rf'src\runs_data')