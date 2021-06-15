import os
import sys
import time
import platform
import psutil
import wmi
import json
import uuid
# import pymongo

computer = wmi.WMI()


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def print_cli_data():
    print("==================== INFO =====================")
    my_system = computer.Win32_ComputerSystem()[0]
    print(f"Computer Name: {platform.node()}")
    print(f"Manufacturer: {my_system.Manufacturer}")
    print(f"Model: {my_system.Model}")
    print("===============================================")

    print("==================== CPU ======================")
    proc_info = computer.Win32_Processor()[0]
    print('CPU Name: {0}'.format(proc_info.Name))
    print(f"Type CPU: {platform.processor()}")
    print(f"Machine type: {platform.machine()}")
    print(f"Physical Cores: {psutil.cpu_count(logical=False)}")
    print(f"Logical Cores: {psutil.cpu_count(logical=True)}")
    print("===============================================")

    print("==================== RAM ======================")
    print(
        f"Total RAM installed: {round(psutil.virtual_memory().total/1000000000, 2)} GB")
    print("===============================================")

    print("==================== GPU ======================")
    gpu_info = computer.Win32_VideoController()[0]
    print('GPU Name: {0}'.format(gpu_info.Name))
    print("===============================================")

    print("==================== DISK =====================")
    print("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        print(f"  Total Size: {get_size(partition_usage.total)}")
        print(f"  Used: {get_size(partition_usage.used)}")
        print(f"  Free: {get_size(partition_usage.free)}")
        print(f"  Percentage: {partition_usage.percent}%")

    print("==================== OS =======================")
    print(f"OS: {platform.system()}")
    print(f"OS Release: {platform.release()}")
    print(f"OS Version: {platform.version()}")
    print(f"Platform type: {platform.platform()}")
    print(f"Arch: {platform.architecture()}")
    print("===============================================\n")
    time.sleep(5)


def save_json():
    my_system = computer.Win32_ComputerSystem()[0]
    proc_info = computer.Win32_Processor()[0]
    gpu_info = computer.Win32_VideoController()[0]
    partitions = psutil.disk_partitions()
    Disk = {}
    for partition in partitions:
        num = 0
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        Disk[num] = {
            "Device": partition.device,
            "Mountpoint": partition.mountpoint,
            "File system": partition.fstype,
            "Total Size": get_size(partition_usage.total),
            "Used": get_size(partition_usage.used),
            "Free": get_size(partition_usage.free),
            "Percentage": str(partition_usage.percent) + "%"
        }
    data = {
        "ID": uuid.uuid4().hex,
        "INFO": {
            "Computer Name": platform.node(),
            "Manufacturer": my_system.Manufacturer,
            "Model": my_system.Model
        },
        "CPU": {
            "Name": proc_info.Name,
            "Type": platform.processor(),
            "Physical Cores": psutil.cpu_count(logical=False),
            "Logical Cores": psutil.cpu_count(logical=True)
        },
        "RAM": {
            "Total": str(round(psutil.virtual_memory().total/1000000000, 2)) + "GB"
        },
        "GPU": {
            "Name": gpu_info.Name
        },
        "OS": {
            "System": platform.system(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Type": platform.platform(),
            "Arch": str(platform.architecture()).replace('"',"").replace('(',"").replace(')',"").replace("'","")
        }
    }
    data["DISK"] = Disk

    # with open('List.json', 'w') as outfile:
    #     json.dump(data, outfile, indent=4)
    root = r'\\srvfs\DATI\Utenti\ALIZZI'
    os.chdir(root)
    write_json(data)

# function to add to JSON
def write_json(new_data, filename = 'list.json'):
    with open(filename,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_dat3a with file_data
        file_data.update(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)

# def db_insert_data(mydict):
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     mydb = myclient["IMS_srl"]
#     mycol = mydb["PC"]
#     mycol.insert_one(mydict)

def main():
    while True:
        print("/=============================================\\")
        print("|                                             |")
        print("|      Get System Info by Alexkill536ITA      |")
        print("|                                             |")
        print("|=============================================|")
        print("|                                             |")
        print("|    1 - Print Info System to CLI             |")
        print("|    2 - Save Info System to JSON             |")
        print("|    3 - Exit                                 |")
        print("|                                             |")
        print("\=============================================/\n")
        select = input("Insert options: ")
        if select == "1":
            print_cli_data()
        elif select == "2":
            save_json()
        elif select == "3":
            sys.exit()
        select = 0


if __name__ == "__main__":
    main()
