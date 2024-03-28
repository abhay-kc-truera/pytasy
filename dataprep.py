import subprocess
from etl.spark.spark_session_helper import spark
from path_manager import raw_30_days_data_dowload_path, raw_data_dowload_path, raw_data_flatten_path
from etl.datawriter import write_bulk_historical_data, merge_new_data
from stats_creater import prepare_model_feature_data
import time

def download_and_unzip_historical_data():
    clear_command = "rm -rf %s"%(raw_data_dowload_path)
    subprocess.run(clear_command.split(" "))
    download_command = "wget --directory-prefix downloads https://cricsheet.org/downloads/all_json.zip"
    subprocess.run(download_command.split(" "))
    unzip_command = "unzip downloads/all_json.zip -d %s"%(raw_data_dowload_path)
    subprocess.run(unzip_command.split(" "))

def download_and_unzip_incremental_data():
    clear_command = "rm -rf %s"%(raw_30_days_data_dowload_path)
    subprocess.run(clear_command.split(" "))
    download_command = "wget --directory-prefix downloads https://cricsheet.org/downloads/recently_added_30_json.zip"
    subprocess.run(download_command.split(" "))
    unzip_command = "unzip recently_added_30_json.zip -d %s"%(raw_30_days_data_dowload_path)
    subprocess.run(unzip_command.split(" "))


def prepare_data(mode: str):
    create_downloads_dir_command = "mkdir -p downloads"
    subprocess.run(create_downloads_dir_command.split(" "))
    remove_zip_command = "rm -rf downloads/*.zip"
    subprocess.run(remove_zip_command.split(" "))
    if mode.lower() == "full":
        print("dowloading historical data")
        download_and_unzip_historical_data()
        print("flattening historical data")
        write_bulk_historical_data(raw_data_dowload_path,raw_data_flatten_path,spark)
    else:
        print("dowloading incremental data")
        download_and_unzip_incremental_data()
        print("flattening incremental data")
        merge_new_data(
            output_path=raw_data_flatten_path,
            historical_data_prefix=raw_data_dowload_path,
            new_data_prefix=raw_30_days_data_dowload_path,
            spark=spark)
    print("raw data download and flatten finished")
    print("moving to feature prep")
    time.sleep(10)
    prepare_model_feature_data()
    print("feature prep done")
    