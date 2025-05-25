import os
import zipfile
import rarfile
from tqdm import tqdm  # Progress bar support
import re  # Regex for part detection

# Set path for WinRAR's extraction tool
rarfile.UNRAR_TOOL = "C:\\Program Files\\WinRAR\\Rar.exe"

# ASCII Art for a welcoming banner
banner = """
  ____  _                 _ _         
 |  _ \| | ___   ___   __| | |__  ___ 
 | |_) | |/ _ \ / _ \ / _` | '_ \/ __|
 |  __/| | (_) | (_) | (_| | | | \__ \\
 |_|   |_|\___/ \___/ \__,_|_| |_|___/

"""
print(banner)

# Ask user for the folder path
folder_path = input("Enter the folder where your compressed files are located: ")

# Check if the folder exists
if not os.path.isdir(folder_path):
    print("Invalid folder path! Please enter a correct path.")
else:
    print(f"Processing files in: {folder_path}")

    # Define paths for 'Successful' and 'Un-Successful' folders
    success_folder = os.path.join(folder_path, "Successful")
    unsuccessful_folder = os.path.join(folder_path, "Un-Successful")

    # Create the folders if they don't already exist
    os.makedirs(success_folder, exist_ok=True)
    os.makedirs(unsuccessful_folder, exist_ok=True)

    # Dictionary to track multi-part file groups
    part_groups = {}

    # First pass: Identify files and group multi-part archives
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.zip', '.rar')):
            part_match = re.match(r"(.+?)\.part\d+\.rar", file, re.IGNORECASE)
            
            if part_match:
                base_name = part_match.group(1)  # Extract base name before .Part1
                if base_name not in part_groups:
                    part_groups[base_name] = []
                part_groups[base_name].append(file)
            elif 'part' not in file.lower():  # Process regular compressed files
                part_groups[file] = [file]

    # Second pass: Process each archive group
    for base_name, files in part_groups.items():
        extraction_folder = os.path.join(folder_path, base_name)

        # Fix: Prevent folder creation error if a file with the same name exists
        if os.path.exists(extraction_folder) and not os.path.isdir(extraction_folder):
            print(f"⚠️ Warning: A file with the name '{extraction_folder}' already exists.")
            extraction_folder += "_extracted"

        os.makedirs(extraction_folder, exist_ok=True)

        # Move all grouped files into their folder
        for file in files:
            file_path = os.path.join(folder_path, file)
            new_file_path = os.path.join(extraction_folder, file)
            os.rename(file_path, new_file_path)

        # Try extracting only from the `.Part1.rar` file (if exists)
        part1_file = next((f for f in files if ".part1.rar" in f.lower()), files[0])  # Default to first file

        try:
            part1_file_path = os.path.join(extraction_folder, part1_file)
            
            # Extract based on file type with progress bar
            if part1_file.lower().endswith('.zip'):
                with zipfile.ZipFile(part1_file_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    for item in tqdm(file_list, desc=f"Extracting {base_name}"):
                        zip_ref.extract(item, extraction_folder)

            elif part1_file.lower().endswith('.rar'):
                with rarfile.RarFile(part1_file_path, 'r') as rar_ref:
                    file_list = rar_ref.namelist()
                    for item in tqdm(file_list, desc=f"Extracting {base_name}"):
                        rar_ref.extract(item, extraction_folder)

            # Move only the `.zip` or `.rar` files into 'Successful'
            for file in files:
                os.rename(os.path.join(extraction_folder, file), os.path.join(success_folder, file))

            print(f"✅ Extraction Successful: {base_name}")

        except Exception as e:
            # Move only the `.zip` or `.rar` files into 'Un-Successful' if extraction fails
            for file in files:
                os.rename(os.path.join(extraction_folder, file), os.path.join(unsuccessful_folder, file))

            print(f"❌ Extraction Failed: {base_name} - {str(e)}")

    # Once all files are processed, display completion message
    print("\n🎉 All files processed successfully!")