import os

KICAD_FULL_IMAGE_ID = "registry.cn-shanghai.aliyuncs.com/kicad/kicad:full"
KICAD_LITE_IMAGE_ID = "registry.cn-shanghai.aliyuncs.com/kicad/kicad:lite"

FILE_SRV_PORT = 7676

OUT_DIR_NAME = "out"

CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

OUT_DIR = os.path.join(CURRENT_SCRIPT_DIR, OUT_DIR_NAME)

# mkdir out in current dir
if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)