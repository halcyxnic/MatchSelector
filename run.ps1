# --------------------------------------------------------------------------
# PowerShell Script: VALORANT Match Selection Setup and Run
# 1. Sets up the Python virtual environment (.env).
# 2. Prompts the user for two required options (-s and -p).
# 3. Runs the main Python script with the selected arguments.
# 4. Cleans up the environment.
# --------------------------------------------------------------------------

# --- Configuration ---
$VENV_NAME = ".env"
$REQUIREMENTS_FILE = "requirements.txt" # Ensure this file exists for pip install

# --- 0. Pre-Chck: Ensure playerlist.txt is valid ---
$lines = Get-Content playerlist.txt

if ($lines.Count -ne 10) {
    Write-Host "playerlist must have exactly 10 lines."
    Read-Host -Prompt "Please press Enter, update this file, then re-run the program."
    exit 1
}

$regex = '^.*,\d+,\d+$'
$counter = 1

foreach ($line in $lines) {
    if ($line -notmatch $regex) {
        Write-Host "Invalid line ${counter}: ${line}. Must be in format (name),(acs),(trackerscore)."
        Read-Host -Prompt "Please press Enter, update this file, then re-run the program."
        exit 1
    }
    $counter++
}

Write-Host "File is valid"

# --- 1. Pre-Check: Ensure Python is available ---
try {
    Write-Host "Checking for Python..."
    $pythonVersion = (python -V)
    Write-Host "Found $($pythonVersion)"
} catch {
    Write-Error "Error: Python executable not found. Please install Python and ensure it is in your PATH."
    exit
}

# --- 2. VENV Setup ---
Write-Host "Creating virtual environment '$VENV_NAME'..."
python -m venv $VENV_NAME

# --- 3. Activation and Dependency Installation ---

$ACTIVATE_PATH = Join-Path $VENV_NAME "Scripts\Activate.ps1"

if (Test-Path $ACTIVATE_PATH) {
    Write-Host "Activating virtual environment..."
    . $ACTIVATE_PATH

    Write-Host "Installing dependencies from $REQUIREMENTS_FILE..."
    # Suppress pip output for cleaner terminal view, but capture errors
    pip install -r $REQUIREMENTS_FILE | Out-Null 2>&1

    Write-Host "--- VENV IS ACTIVE ---"
    Clear-Host
    
    # --------------------------------------------------------------------------
    # --- 4. Interactive Menu for Map Selection (-s) ---
    # --------------------------------------------------------------------------
    
    $MapMenu = @{
        1 = "1" # Veto Selection (1 map ban each)
        3 = "3" # Draft Selection (3 maps pre-selected)
        5 = "5" # Full Random Selection (5 maps)
    }
    $MapDescriptions = @{
        1 = "Best of 1"
        3 = "Best of 3 (default)"
        5 = "Best of 5"
    }
    $MapDefault = 3 # Default to BO3
    $SelectedMapStrategy = $MapMenu[$MapDefault]

    $UserSelection = 0
    
    do {
        $MapMenu.Keys | Sort-Object | ForEach-Object {
            $num = $_
            $desc = $MapDescriptions[$num]
            if ($num -eq $MapDefault) {
                Write-Host "$num. $desc" -ForegroundColor Green
            } else {
                Write-Host "$num. $desc"
            }
        }
        Write-Host "----------------------------------"

        $PromptText = "Enter selection (1-3) or press Enter for default map strategy"
        $UserInput = Read-Host -Prompt $PromptText

        if ([string]::IsNullOrWhiteSpace($UserInput)) {
            Write-Host "Using default map strategy: -s $SelectedMapStrategy" -ForegroundColor Yellow
            break
        }
        
        if ([int]::TryParse($UserInput, [ref]$UserSelection)) {
            if ($MapMenu.ContainsKey($UserSelection)) {
                $SelectedMapStrategy = $MapMenu[$UserSelection]
                Write-Host "Map strategy selected: -s $SelectedMapStrategy" -ForegroundColor Cyan
                break
            } else {
                Write-Warning "Invalid option. Please select 1, 2, or 3."
            }
        } else {
            Write-Warning "Invalid input. Please enter a number."
        }

    } while ($true)

    # --------------------------------------------------------------------------
    # --- 5. Interactive Menu for Player Selection (-p) ---
    # --------------------------------------------------------------------------
    
    $PlayerMenu = @{
        1 = "snake"
        2 = "corerand"
        3 = "acs"
        4 = "trackerscore"
    }
    $PlayerDefault = 3 # Default to ACS
    $SelectedPlayerStrategy = $PlayerMenu[$PlayerDefault]

    $UserSelection = 0
    
    do {
        $PlayerMenu.Keys | Sort-Object | ForEach-Object {
            $num = $_
            $name = $PlayerMenu[$num]
            if ($num -eq $PlayerDefault) {
                Write-Host "$num. $name (Default: -p $name)" -ForegroundColor Green
            } else {
                Write-Host "$num. $name (-p $name)"
            }
        }
        Write-Host "------------------------------------"

        $PromptText = "Enter selection (1-4) or press Enter for default player strategy"
        $UserInput = Read-Host -Prompt $PromptText

        if ([string]::IsNullOrWhiteSpace($UserInput)) {
            Write-Host "Using default player strategy: -p $SelectedPlayerStrategy" -ForegroundColor Yellow
            break
        }
        
        if ([int]::TryParse($UserInput, [ref]$UserSelection)) {
            if ($PlayerMenu.ContainsKey($UserSelection)) {
                $SelectedPlayerStrategy = $PlayerMenu[$UserSelection]
                Write-Host "Player strategy selected: -p $SelectedPlayerStrategy" -ForegroundColor Cyan
                break
            } else {
                Write-Warning "Invalid option. Please select a number between 1 and 4."
            }
        } else {
            Write-Warning "Invalid input. Please enter a number."
        }

    } while ($true)

    # --------------------------------------------------------------------------
    # --- 6. Run the Main Script with Selected Options ---
    # --------------------------------------------------------------------------

    Write-Host "`n--- Starting VALORANT Match Selection ---" -ForegroundColor DarkCyan
    
    # Construct and run the final command using the variables
    $FinalCommand = "python main.py -s $SelectedMapStrategy -p $SelectedPlayerStrategy"
    Write-Host "Executing: $FinalCommand" -ForegroundColor DarkCyan

    Invoke-Expression $FinalCommand

    # --- 7. Deactivate the Environment ---
    deactivate

} else {
    Write-Error "Activation script not found. Venv creation may have failed."
    exit 1
}

# Pause to prevent the window from immediately closing on double-click
Read-Host -Prompt "Execution complete. Press Enter to close this window..."