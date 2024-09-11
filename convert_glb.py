import os
import subprocess
import uuid
import logging
import time

from utils import KICAD_FULL_IMAGE_ID


kicad_img_home_path ="/home/kicad"
# kicad-cli pcb export glb --subst-models --include-tracks --include-pads --include-zones  --include-silkscreen  .\complex_hierarchy.kicad_pcb -o .\complex_hierarchy.glb
def export_glb(root_sch_file_name):
    enter_time = time.time()

    kicad_project_dir = os.path.dirname(root_sch_file_name)
    pcb_name = os.path.basename(root_sch_file_name)
    mounted_prj_path = os.path.join(kicad_img_home_path, str(uuid.uuid4())).replace("\\", "/")
    mouted_pcb_fp = os.path.join(mounted_prj_path, pcb_name).replace("\\", "/")
    output_file_name = str(uuid.uuid4()) + ".glb"
    docker_output_fn = os.path.join(mounted_prj_path, output_file_name).replace("\\", "/")

    first_cmd = ["docker", "run", "--rm",
                 "-v", f"{kicad_project_dir}:{mounted_prj_path}",
                 KICAD_FULL_IMAGE_ID, "kicad-cli", "pcb",
                 "export", "glb", "--subst-models", "--include-soldermask","--include-tracks","--include-pads" , "--include-zones","--include-silkscreen",
                 mouted_pcb_fp, "-o",
                 docker_output_fn
                 ]
    print(" ".join(first_cmd))

    start_time = time.time()

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

    print(f"PCB to glb  Time taken: {time.time() - enter_time} secs")



    c_output_file_name = str(uuid.uuid4()) + ".glb"
    c_docker_output_fn = os.path.join(mounted_prj_path, c_output_file_name).replace("\\", "/")

    second_cmd = ["docker", "run", "--rm", "-v", f"{kicad_project_dir}:{mounted_prj_path}",
                  KICAD_FULL_IMAGE_ID, "gltfpack",
                  "-i",
                  docker_output_fn, "-v", "-cc", "-tc", "-ts", "0.5", "-o",
                  c_docker_output_fn
                  ]

    print(" ".join(second_cmd))

    start_time = time.time()

    try:
        process_pack = subprocess.Popen(second_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, stderr = process_pack.communicate()
        if stderr:
            logging.error(stderr.decode())
    except Exception as e:
        logging.error(e)

    try:
        process_pack.wait()
    except Exception as e:
        logging.error(e)

    print(f"Compress glb {time.time() - start_time} secs")

    print(f"PCB to glb  Time taken: {time.time() - enter_time} secs")



    return os.path.join(kicad_project_dir, c_output_file_name).replace("\\", "/")


def main():
    # export_glb("D:/pcb_projects/Altium/large/MiniPC.kicad_pcb")
    # D:\pcb_projects\StepperServoCAN\hardware\PCB
    export_glb("D:/pcb_projects/StepperServoCAN/hardware/PCB/StepperServoCAN.kicad_pcb")
    # export_glb("D:/code/kicad/build/out/share/kicad/demos/video/video.kicad_pcb")
    # npx gltfpack -v -cc -tc -ts 0.5 -i 215cfeae-450f-4097-a2a6-0e423ca5b6a4.glb -o a.glb


if __name__ == "__main__":
    main()
