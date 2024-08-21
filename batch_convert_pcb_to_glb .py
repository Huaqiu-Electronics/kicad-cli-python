import os
import subprocess
import uuid
import logging
import time
import zipfile
import shutil
import sys

from utils import KICAD_FULL_IMAGE_ID

kicad_img_home_path = "/home/kicad"
archive_dir = "D:/achieves"

def export_glb(root_sch_file_name):
    kicad_project_dir = os.path.dirname(root_sch_file_name)
    pcb_name = os.path.basename(root_sch_file_name)
    pcb_name_no_ext = os.path.splitext(pcb_name)[0]
    mounted_prj_path = os.path.join(kicad_img_home_path, str(uuid.uuid4())).replace("\\", "/")
    mounted_pcb_fp = os.path.join(mounted_prj_path, pcb_name).replace("\\", "/")
    output_file_name = pcb_name_no_ext + ".glb"
    docker_output_fn = os.path.join(mounted_prj_path, output_file_name).replace("\\", "/")

    first_cmd = [
        "docker", "run", "--rm",
        "-v", f"{kicad_project_dir}:{mounted_prj_path}",
        KICAD_FULL_IMAGE_ID, "kicad-cli", "pcb",
        "export", "glb", "--subst-models", "--include-tracks",
        mounted_pcb_fp, "-o", docker_output_fn
    ]

    try:
        process_export = subprocess.Popen(first_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process_export.communicate()

        if stdout:
            logging.info(stdout.decode())
        if stderr:
            logging.error(stderr.decode())

        process_export.wait()
    except Exception as e:
        logging.error(f"Error during export: {e}")

    return os.path.join(kicad_project_dir, output_file_name).replace("\\", "/")


def process_kicad_files(directory):
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    for root, _, files in os.walk(directory):
        pcb_files = [f for f in files if f.endswith(".kicad_pcb")]
        for pcb_file in pcb_files:
            sch_files = [os.path.join(root, f) for f in files if f.endswith(".kicad_sch")]

            if not sch_files:
                logging.info(f"No .kicad_sch files found for {pcb_file}, skipping ZIP creation.")
                continue
                        
            pcb_file_path = os.path.join(root, pcb_file)
            glb_file_path = export_glb(pcb_file_path)



            zip_file_name = os.path.splitext(pcb_file)[0] + ".zip"
            zip_file_path = os.path.join(root, zip_file_name)

            with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                zipf.write(glb_file_path, os.path.basename(glb_file_path))
                zipf.write(pcb_file_path, os.path.basename(pcb_file_path))
                for sch_file in sch_files:
                    zipf.write(sch_file, os.path.basename(sch_file))

            shutil.copy(zip_file_path, archive_dir)
            logging.info(f"Archived {zip_file_name} to {archive_dir}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)

    directory = sys.argv[1]
    if not os.path.exists(directory):
        logging.error(f"Directory {directory} does not exist.")
        sys.exit(1)

    process_kicad_files(directory)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
