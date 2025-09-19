import os
import subprocess
import uuid
import logging

from utils import KICAD_LITE_IMAGE_ID

kicad_img_home_path ="/home/kicad"

'''
        String[] firstCmd = { "docker", "run", "-v", kicad_project_dir + ":" + mounted_prj_path,
                KICAD_IMAGE_ID, "kicad-cli", "sch",
                "export", "netlist", "--format", "allegro",
                mouted_sch_root_path, "-o",
                mounted_prj_path + "/" + output_file_name
        };


'''
#
def start_srv(data_path):
    mounted_prj_path = os.path.join(kicad_img_home_path, "data").replace("\\", "/")

    first_cmd = [
        "docker", "run", "--rm",
        "-v", f"{data_path}:{mounted_prj_path}",
        "-p", "8080:8080",
        KICAD_LITE_IMAGE_ID,
        "kicad-cli", "server"
    ]

    print(" ".join(first_cmd))

    try:
        process_export = subprocess.Popen(first_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process_export.communicate()
        if stderr:
            logging.error(stderr.decode())
    except Exception as e:
        logging.error(e)

    try:
        process_export.wait()
    except Exception as e:
        logging.error(e)

def main():
    import time


    start_srv(r"D:\code\kicad-cli-python\pic")


if __name__ == "__main__":
    main()
