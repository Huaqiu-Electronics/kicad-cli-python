# test_kicad_cli.ps1 - Clear output dir first, ensure it exists, then process files

# Define paths
$kicadCli = "./build/out/bin/kicad-cli.exe"
$inputDir = "./tests/ad"
$outputDir = "./tests/out"
$pcbInput = "$inputDir/PWRMOD-001-RevA.PcbDoc"
$schInput = "$inputDir/PWRMOD-001-RevA.SchDoc"

# Copied input files (in output directory)
$pcbCopy = "$outputDir/PWRMOD-001-RevA.PcbDoc"
$schCopy = "$outputDir/PWRMOD-001-RevA.SchDoc"

# Output files
$pcbOutput = "$outputDir/PWRMOD-001-RevA.kicad_pcb"
$schOutput = "$outputDir/PWRMOD-001-RevA.kicad_sch"

# 3D export paths
$pcb3dInput = "./tests/3d/pcb_with_local_3d_model.kicad_pcb"
$pcb3dOutput = "./tests/3d/pcb_with_local_3d_model.glb"


# Clear output directory if it exists, then ensure it exists
if (Test-Path $outputDir) {
    Write-Host "Clearing output directory: $outputDir" -ForegroundColor Yellow
    Get-ChildItem -Path $outputDir -Recurse | Remove-Item -Force -Recurse
} 

# Ensure output directory exists
Write-Host "Ensuring output directory exists: $outputDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

# Ensure 3D directory exists
$3dDir = "./tests/3d"
Write-Host "Ensuring 3D directory exists: $3dDir" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $3dDir -Force | Out-Null

# Function to run conversion with error checking and full output
function Convert-File {
    param(
        [string]$command,
        [string]$inputFile,
        [string]$outputFile
    )
    
    Write-Host "Converting $inputFile to $outputFile..." -ForegroundColor Cyan
    
    if (!(Test-Path $inputFile)) {
        Write-Error "Input file not found: $inputFile"
        return $false
    }
    
    # Capture all output from kicad-cli
    Write-Host "=== kicad-cli output start ===" -ForegroundColor Yellow
    $output = & $kicadCli $command convert $inputFile -o $outputFile 2>&1
    $exitCode = $LASTEXITCODE
    Write-Host "$output"
    Write-Host "=== kicad-cli output end ===" -ForegroundColor Yellow
    
    if ($exitCode -ne 0) {
        Write-Error "Conversion failed for $inputFile with exit code: $exitCode"
        return $false
    }
    
    if (Test-Path $outputFile) {
        Write-Host "Successfully created $outputFile" -ForegroundColor Green
        return $true
    } else {
        Write-Error "Output file was not created: $outputFile"
        return $false
    }
}

# Function to copy and convert file
function Copy-And-Convert-File {
    param(
        [string]$command,
        [string]$inputFile,
        [string]$copyFile,
        [string]$outputFile,
        [string]$from
    )
    
    Write-Host "Copying $inputFile to $copyFile..." -ForegroundColor Cyan
    
    if (!(Test-Path $inputFile)) {
        Write-Error "Input file not found: $inputFile"
        return $false
    }
    
    # Copy file to output directory
    try {
        Copy-Item $inputFile $copyFile -Force
        Write-Host "Successfully copied to $copyFile" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to copy $inputFile to $copyFile : $_"
        return $false
    }
    
    Write-Host "Converting $copyFile to $outputFile..." -ForegroundColor Cyan
    
    # Capture all output from kicad-cli
    Write-Host "=== kicad-cli output start ===" -ForegroundColor Yellow
    $output = & $kicadCli $command convert --from $from $copyFile -o $outputFile 2>&1
    $exitCode = $LASTEXITCODE
    Write-Host "$output"
    Write-Host "=== kicad-cli output end ===" -ForegroundColor Yellow
    
    if ($exitCode -ne 0) {
        Write-Error "Conversion failed for $copyFile with exit code: $exitCode"
        return $false
    }
    
    if (Test-Path $outputFile) {
        Write-Host "Successfully created $outputFile" -ForegroundColor Green
        return $true
    } else {
        Write-Error "Output file was not created: $outputFile"
        return $false
    }
}

# Function to export PCB to GLB (3D model)
function Export-Pcb-To-Glb {
    param(
        [string]$inputFile,
        [string]$outputFile
    )
    
    Write-Host "Exporting $inputFile to $outputFile (GLB format)..." -ForegroundColor Cyan
    
    if (!(Test-Path $inputFile)) {
        Write-Error "Input PCB file not found: $inputFile"
        return $false
    }
    
    # Capture all output from kicad-cli
    Write-Host "=== kicad-cli output start ===" -ForegroundColor Yellow
    $output = & $kicadCli pcb export glb --subst-models --include-tracks --include-soldermask --include-pads --include-zones --include-silkscreen $inputFile -o $outputFile 2>&1
    $exitCode = $LASTEXITCODE
    Write-Host "$output"
    Write-Host "=== kicad-cli output end ===" -ForegroundColor Yellow
    
    if ($exitCode -ne 0) {
        Write-Error "GLB export failed for $inputFile with exit code: $exitCode"
        return $false
    }
    
    if (Test-Path $outputFile) {
        Write-Host "Successfully created $outputFile" -ForegroundColor Green
        return $true
    } else {
        Write-Error "GLB output file was not created: $outputFile"
        return $false
    }
}


Write-Host "`Updating PCB file..." -ForegroundColor Yellow

$olderPcbInput = "./tests/kicad5/main-board.kicad_pcb"
$olderPcbOutput = "$outputDir/main-board.kicad_pcb"
$olderPCBCopy = "$outputDir/main-board-copy.kicad_pcb"
$schSuccess = Copy-And-Convert-File "pcb" $olderPcbInput $olderPCBCopy $olderPcbOutput "kicad_pcb"

$ArduinoPcbInput = "./tests/kicad5/Arduino_MEGA_2560-Rev3.kicad_pcb"
$ArduinoPcbOutput = "$outputDir/Arduino_MEGA_2560-Rev3.kicad_pcb"
$ArduinoPCBCopy = "$outputDir/Arduino_MEGA_2560-Rev3-copy.kicad_pcb"
$schSuccess = Copy-And-Convert-File "pcb" $ArduinoPcbInput $ArduinoPCBCopy $ArduinoPcbOutput "kicad_pcb"

Write-Host "`Updating SCH file..." -ForegroundColor Yellow

$ArduinoSchInput = "./tests/kicad5/Arduino_MEGA_2560-Rev3.sch"
$ArduinoSchOutput = "$outputDir/Arduino_MEGA_2560-Rev3.kicad_sch"
$ArduinoPCBCopy = "$outputDir/Arduino_MEGA_2560-Rev3-copy.sch"
$schSuccess = Copy-And-Convert-File "sch" $ArduinoSchInput $ArduinoPCBCopy $ArduinoSchOutput "kicad_sch"

# Process PCB file
Write-Host "Processing PCB file..." -ForegroundColor Yellow
$pcbSuccess = Copy-And-Convert-File "pcb" $pcbInput $pcbCopy $pcbOutput "altium_designer"

# Process schematic file
Write-Host "`nProcessing schematic file..." -ForegroundColor Yellow
$schSuccess = Copy-And-Convert-File "sch" $schInput $schCopy $schOutput "sch_altium"


# Export 3D model (GLB)
Write-Host "`nExporting PCB to 3D model (GLB)..." -ForegroundColor Yellow
$glbSuccess = Export-Pcb-To-Glb $pcb3dInput $pcb3dOutput



# Exit with appropriate code
if ($pcbSuccess -and $schSuccess -and $glbSuccess) {
    Write-Host "All processes completed successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Error "Some processes failed"
    exit 1
}