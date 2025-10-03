import os
import json

def rename_files_and_folders(directory):
    """Rename all files and folders by replacing spaces with underscores"""
    for root, dirs, files in os.walk(directory, topdown=False):
        # Rename files first
        for file in files:
            if ' ' in file:
                old_path = os.path.join(root, file)
                new_file = file.replace(' ', '_')
                new_path = os.path.join(root, new_file)

                try:
                    os.rename(old_path, new_path)
                    # print(f"Renamed file: {old_path} -> {new_path}")
                except Exception as e:
                    print(f"Error renaming file {old_path} to {new_path}: {e}")
        
        # Rename directories
        for dir_name in dirs:
            if ' ' in dir_name:
                old_path = os.path.join(root, dir_name)
                new_dir = dir_name.replace(' ', '_')
                new_path = os.path.join(root, new_dir)

                try:
                    os.rename(old_path, new_path)
                    # print(f"Renamed directory: {old_path} -> {new_path}")
                except Exception as e:
                    print(f"Error renaming directory {old_path} to {new_path}: {e}")

# Rename files and folders in the word data path, replace ' ' with '_'
# rename_files_and_folders('ISL_CSLRT_Corpus')


def save_all_classes(data_path, json_path):
    """List all class names (folder names) in the given data path and save to a JSON file"""
    classes = [d for d in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, d))]
    
    json.dump(classes, open(json_path, 'w'), indent=4)
    print(f"Class names saved to {json_path}")

save_all_classes('ISL_CSLRT_Corpus/Videos_Sentence_Level', 'data/sentence_class_names.json')