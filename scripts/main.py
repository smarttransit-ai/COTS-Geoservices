import pandas as pd
import os
from gtfs_functions import Feed
from combine_gtfs_feeds import cli
import zipfile
import shutil
# modify environment variable DISABLE_PANDERA_IMPORT_WARNING to True
os.environ['DISABLE_PANDERA_IMPORT_WARNING'] = 'True'

# Create a temporary folder in /bin/BOC/data called merged_gtfs
# Define the path to the temporary folder
input_folder = './data/input'
destination_temp_folder = './data/temp'

# Create the temporary folder if it does not exist
if not os.path.exists(destination_temp_folder):
    os.makedirs(destination_temp_folder)

def unzip_all_gtfs_files_in_directory(directory):
    # Define the source GTFS folder and the destination temporary folder
    source_gtfs_folders = [directory]

    # Copy the GTFS folder into the temporary folder
    for source_gtfs_folder in source_gtfs_folders:
        if os.path.exists(source_gtfs_folder):
            shutil.copytree(source_gtfs_folder, destination_temp_folder, dirs_exist_ok=True)
            print(f"Copied GTFS data from {source_gtfs_folder} to {destination_temp_folder}.")
        else:
            print(f"Source folder {source_gtfs_folder} does not exist.")

    # unzip all files in the temporary folder to a folder based on the name of the zip file

    for root, dirs, files in os.walk(destination_temp_folder):
        for file in files:
            if file.endswith('.zip'):
                zip_path = os.path.join(root, file)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(root, file[:-4]))
                os.remove(zip_path)  # Remove the zip file after extraction
                print(f"Unzipped {zip_path}.")
    
    print("All GTFS files have been unzipped.")

def update_all_calendar_dates_to_be_uniform(date_str_start='20220701', date_str_end='20261126'):
    # Make sure their `start_date,end_date` in `calendar.txt` is the same
    # loop through each folder in the temporary folder and edit calendar.txt by reading it as a csv and changing start_date,end_date
    # Set the desired start and end dates (as strings, e.g., '20250530')

    # Loop through each folder in the temporary folder and update calendar.txt
    for root, dirs, files in os.walk(destination_temp_folder):
        if 'calendar.txt' in files:
            cal_path = os.path.join(root, 'calendar.txt')
            try:
                cal_df = pd.read_csv(cal_path)
                cal_df['start_date'] = date_str_start
                cal_df['end_date'] = date_str_end
                cal_df.to_csv(cal_path, index=False)
                print(f"Updated calendar.txt in {root}")
            except Exception as e:
                print(f"Failed to update {cal_path}: {e}")
    print("All calendar.txt files have been updated to uniform start and end dates.")

def combine_all_gtfs_feeds(service_date=20250530):
    output_path = f"{destination_temp_folder}_output"
    # create output folder if it does not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    merged_gtfs = cli.run.combine(destination_temp_folder, service_date, output_path)
    merged_gtfs.routes_df.head()
    merged_gtfs.export_feed()
    return output_path

def extra_steps(output_path):
    print("Performing extra steps for stops.txt...")
    # Extra steps for parent station
    stops_df = pd.read_csv(f"{output_path}/stops.txt")
    stops_df.loc[stops_df['parent_station'].notnull(), 'parent_station'] = stops_df['stop_id'].str.split('_').str[0] + '_0:' + stops_df['parent_station'].str.split(':').str[1]
    stops_df.to_csv(f"{output_path}/stops.txt", index=False)

    # Read /Users/jose/Developer/git/COTS_SOLVERS/scripts/data/temp_output/agency.txt and change all timezones to be America/Chicago
    print("Making all timezones uniform...")
    agency_df = pd.read_csv(f"{output_path}/agency.txt")
    agency_df['agency_timezone'] = 'America/Chicago'
    agency_df.to_csv(f"{output_path}/agency.txt", index=False)

def zip_merged_directory(input_dir, output_name):
    # Example from your context
    shutil.make_archive(output_name, 'zip', input_dir)
    # delete all .txt files in the output_path
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.txt'):
                os.remove(os.path.join(root, file))
    print(f"Zipped merged directory to {output_name}.zip")

def verify_merged_zip(zip_path):
    try:
        feed = Feed(zip_path, busiest_date=False)
        parsed_calendar = Feed(zip_path).parse_calendar()
        print(f"Merged successfully: {zip_path}")
        print(f"Parsed calendar: {parsed_calendar}")
        return feed
    except Exception as e:
        print(f"Error verifying merged zip: {e}")
        return None

if __name__ == "__main__":
    unzip_all_gtfs_files_in_directory(input_folder)
    update_all_calendar_dates_to_be_uniform()

    output_path = combine_all_gtfs_feeds()
    # For cleaning the stops.txt stops names.
    extra_steps(output_path)
    zip_merged_directory(output_path, f"{output_path}/MERGED_gtfs")
    verify_merged_zip(f"{output_path}/MERGED_gtfs.zip")

    # delete temp folder
    shutil.rmtree(destination_temp_folder)