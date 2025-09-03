# test_kicad_cli.py
import os
import subprocess
import uuid
import logging
from pathlib import Path

# Configuration
KICAD_LITE_IMAGE_ID = "registry.cn-shanghai.aliyuncs.com/kicad/kicad:lite"
kicad_img_home_path = "/home/kicad"

# Define paths
inputDir = "./tests/ad"
outputDir = "./tests/out"
pcbInput = f"{inputDir}/PWRMOD-001-RevA.PcbDoc"
schInput = f"{inputDir}/PWRMOD-001-RevA.SchDoc"

# Copied input files (in output directory)
pcbCopy = f"{outputDir}/PWRMOD-001-RevA.PcbDoc"
schCopy = f"{outputDir}/PWRMOD-001-RevA.SchDoc"

# Output files
pcbOutput = f"{outputDir}/PWRMOD-001-RevA.kicad_pcb"
schOutput = f"{outputDir}/PWRMOD-001-RevA.kicad_sch"

# 3D export paths
pcb3dInput = "./tests/3d/pcb_with_local_3d_model.kicad_pcb"
pcb3dOutput = "./tests/3d/pcb_with_local_3d_model.glb"

def setup_directories():
    """Clear output directory if it exists, then ensure it exists"""
    # Clear output directory if it exists
    if os.path.exists(outputDir):
        print(f"Clearing output directory: {outputDir}")
        for root, dirs, files in os.walk(outputDir):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
    
    # Ensure output directory exists
    print(f"Ensuring output directory exists: {outputDir}")
    os.makedirs(outputDir, exist_ok=True)
    
    # Ensure 3D directory exists
    dir3d = "./tests/3d"
    print(f"Ensuring 3D directory exists: {dir3d}")
    os.makedirs(dir3d, exist_ok=True)

def run_kicad_cli_docker(*args):
    """
    Run kicad-cli via Docker, similar to convert_glb.py approach
    """
    # Find input and output files in the arguments
    input_file = None
    output_file = None
    
    args_list = list(args)
    for i in range(len(args_list)):
        if args_list[i] == "-o" and (i + 1) < len(args_list):
            output_file = args_list[i + 1]
            break
    
    # Look for input files
    for arg in args_list:
        if "." in arg and arg != output_file:
            if os.path.exists(arg):
                input_file = arg
                break
            elif input_file is None:
                input_file = arg
    
    # Determine the working directory for volume mapping
    work_dir = "."
    if input_file:
        input_dir = os.path.dirname(os.path.abspath(input_file))
        if input_dir and input_dir != ".":
            work_dir = input_dir
    if output_file:
        output_dir_path = os.path.dirname(os.path.abspath(output_file))
        if output_dir_path and output_dir_path != ".":
            work_dir = output_dir_path
    
    # Generate a unique container path
    container_work_dir = os.path.join(kicad_img_home_path, str(uuid.uuid4())).replace("\\", "/")
    
    # Create mapped arguments with container paths
    mapped_args = []
    for arg in args_list:
        if arg == input_file and input_file:
            # Map input file path to container path
            try:
                abs_input = os.path.abspath(input_file)
                rel_path = os.path.relpath(abs_input, work_dir).replace("\\", "/")
                mapped_args.append(f"{container_work_dir}/{rel_path}")
            except:
                # Fallback to simple approach
                file_name = os.path.basename(input_file)
                mapped_args.append(f"{container_work_dir}/{file_name}")
        elif arg == output_file and output_file:
            # Map output file path to container path
            try:
                abs_output = os.path.abspath(output_file)
                rel_path = os.path.relpath(abs_output, work_dir).replace("\\", "/")
                mapped_args.append(f"{container_work_dir}/{rel_path}")
            except:
                # Fallback to simple approach
                file_name = os.path.basename(output_file)
                mapped_args.append(f"{container_work_dir}/{file_name}")
        else:
            mapped_args.append(arg)
    
    # Run Docker command with proper volume mapping
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(work_dir)}:{container_work_dir}",
        KICAD_LITE_IMAGE_ID, "kicad-cli"
    ] + mapped_args
    
    print(f"Running: {' '.join(docker_cmd)}")
    
    try:
        result = subprocess.run(docker_cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Error running kicad-cli: {e}")
        return False

def convert_file(command, input_file, output_file):
    """Run conversion with error checking"""
    print(f"Converting {input_file} to {output_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return False
    
    # Run kicad-cli
    print("=== kicad-cli output start ===")
    success = run_kicad_cli_docker(command, "convert", input_file, "-o", output_file)
    print("=== kicad-cli output end ===")
    
    if not success:
        print(f"Error: Conversion failed for {input_file}")
        return False
    
    if os.path.exists(output_file):
        print(f"Successfully created {output_file}")
        return True
    else:
        print(f"Error: Output file was not created: {output_file}")
        return False

def copy_and_convert_file(command, input_file, copy_file, output_file, from_format):
    """Copy and convert file"""
    print(f"Copying {input_file} to {copy_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return False
    
    # Copy file to output directory
    try:
        os.makedirs(os.path.dirname(copy_file), exist_ok=True)
        with open(input_file, 'rb') as src, open(copy_file, 'wb') as dst:
            dst.write(src.read())
        print(f"Successfully copied to {copy_file}")
    except Exception as e:
        print(f"Error: Failed to copy {input_file} to {copy_file}: {e}")
        return False
    
    print(f"Converting {copy_file} to {output_file}...")
    
    # Run kicad-cli
    print("=== kicad-cli output start ===")
    success = run_kicad_cli_docker(command, "convert", "--from", from_format, copy_file, "-o", output_file)
    print("=== kicad-cli output end ===")
    
    if not success:
        print(f"Error: Conversion failed for {copy_file}")
        return False
    
    if os.path.exists(output_file):
        print(f"Successfully created {output_file}")
        return True
    else:
        print(f"Error: Output file was not created: {output_file}")
        return False

def export_pcb_to_glb(input_file, output_file):
    """Export PCB to GLB (3D model)"""
    print(f"Exporting {input_file} to {output_file} (GLB format)...")
    
    if not os.path.exists(input_file):
        print(f"Error: Input PCB file not found: {input_file}")
        return False
    
    # Run kicad-cli
    print("=== kicad-cli output start ===")
    success = run_kicad_cli_docker(
        "pcb", "export", "glb",
        "--subst-models",
        "--include-tracks",
        "--include-soldermask",
        "--include-pads",
        "--include-zones",
        "--include-silkscreen",
        input_file,
        "-o", output_file
    )
    print("=== kicad-cli output end ===")
    
    if not success:
        print(f"Error: GLB export failed for {input_file}")
        return False
    
    if os.path.exists(output_file):
        print(f"Successfully created {output_file}")
        return True
    else:
        print(f"Error: GLB output file was not created: {output_file}")
        return False

def main():
    setup_directories()
    
    print("\nUpdating PCB file...")
    olderPcbInput = "./tests/kicad5/main-board.kicad_pcb"
    olderPcbOutput = f"{outputDir}/main-board.kicad_pcb"
    olderPCBCopy = f"{outputDir}/main-board-copy.kicad_pcb"
    schSuccess = copy_and_convert_file("pcb", olderPcbInput, olderPCBCopy, olderPcbOutput, "kicad_pcb")
    
    ArduinoPcbInput = "./tests/kicad5/Arduino_MEGA_2560-Rev3.kicad_pcb"
    ArduinoPcbOutput = f"{outputDir}/Arduino_MEGA_2560-Rev3.kicad_pcb"
    ArduinoPCBCopy = f"{outputDir}/Arduino_MEGA_2560-Rev3-copy.kicad_pcb"
    schSuccess = copy_and_convert_file("pcb", ArduinoPcbInput, ArduinoPCBCopy, ArduinoPcbOutput, "kicad_pcb")
    
    print("\nUpdating SCH file...")
    ArduinoSchInput = "./tests/kicad5/Arduino_MEGA_2560-Rev3.sch"
    ArduinoSchOutput = f"{outputDir}/Arduino_MEGA_2560-Rev3.kicad_sch"
    ArduinoSchCopy = f"{outputDir}/Arduino_MEGA_2560-Rev3-copy.sch"
    schSuccess = copy_and_convert_file("sch", ArduinoSchInput, ArduinoSchCopy, ArduinoSchOutput, "kicad_sch")
    
    # Process PCB file
    print("Processing PCB file...")
    pcbSuccess = copy_and_convert_file("pcb", pcbInput, pcbCopy, pcbOutput, "altium_designer")
    
    # Process schematic file
    print("\nProcessing schematic file...")
    schSuccess = copy_and_convert_file("sch", schInput, schCopy, schOutput, "sch_altium")
    
    # Export 3D model (GLB)
    print("\nExporting PCB to 3D model (GLB)...")
    glbSuccess = export_pcb_to_glb(pcb3dInput, pcb3dOutput)
    
    # Exit with appropriate code
    if pcbSuccess and schSuccess and glbSuccess:
        print("All processes completed successfully!")
        return 0
    else:
        print("Some processes failed")
        return 1

if __name__ == "__main__":
    exit(main())