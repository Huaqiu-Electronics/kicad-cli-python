import os
import subprocess
import uuid
import logging

from utils import KICAD_FULL_IMAGE_ID


kicad_img_home_path ="/home/kicad"

# ./build/out/bin/kicad-cli.exe pcb convert --output ./build/out/kicad/foo.kicad_pcb ./build/out/ad/PWRMOD-001-RevA.PcbDoc

# ./build/out/bin/kicad-cli.exe sch convert --output ./build/out/kicad/foo.kicad_sch ./build/out/ad/PWRMOD-001-RevA.SchDoc


Altium_DOC_TO_KICAD_DOC_EXT_MAP = {
"PcbDoc" : "kicad_pcb",
"SchDoc" : "kicad_sch"
}

EXT_TO_KICAD_CLI_ARG = {
"PcbDoc" : "pcb",
"SchDoc" : "sch"
}


def convert_kicad_to_ad(ori_fp) ->str :
    kicad_project_dir = os.path.dirname(ori_fp)
    ori_fn = os.path.basename(ori_fp)

    ori_suffix = ori_fn.split(".")[-1]

    if ori_suffix not in Altium_DOC_TO_KICAD_DOC_EXT_MAP:
        return

    converted_fn = ori_fn.replace(ori_suffix, Altium_DOC_TO_KICAD_DOC_EXT_MAP[ori_suffix])

    mounted_prj_path = os.path.join(kicad_img_home_path, str(uuid.uuid4())).replace("\\", "/")
    mounted_fp = os.path.join(mounted_prj_path, ori_fn).replace("\\", "/")
    output_file_name = converted_fn
    docker_output_fn = os.path.join(mounted_prj_path, output_file_name).replace("\\", "/")

    first_cmd = ["docker", "run", "--rm",
                 "-v", f"{kicad_project_dir}:{mounted_prj_path}",
                 KICAD_FULL_IMAGE_ID, "kicad-cli", EXT_TO_KICAD_CLI_ARG[ori_suffix],
                 "convert", "--output", docker_output_fn,
                 mounted_fp
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

    return os.path.join(kicad_project_dir, output_file_name).replace("\\", "/")


def main():
    import time

    convert_kicad_to_ad("D:/pcb_projects/Altium/large/MiniPC.PcbDoc")



if __name__ == "__main__":
    main()
