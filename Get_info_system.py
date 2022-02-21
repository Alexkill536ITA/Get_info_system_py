import os
import sys
import datetime
import platform
import psutil
import wmi
import json
import uuid
from colored import fg
import pymongo

computer = wmi.WMI()
config = {}

def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")

def config_writer():
    def writer_file(data):
        with open("config.json", "w") as json_data_file:
            json_data_file.write(json.dumps(data, indent=4))

    if (os.path.isfile("config.json")):
        with open("config.json", "r+") as json_data_file:
            read_conf = json.load(json_data_file)
        enable = True
        while enable:
            print("/=============================================\\")
            print("|                                             |")
            print("|                 %sEdit Config%s                 |" % (fg('light_yellow'), fg(251)))
            print("|                                             |")
            print("|=============================================|")
            print("|                                             |")
            print("|    1 - Print Config %sCLI%s                     |" % (fg('light_cyan'), fg(251)))
            print("|    2 - Change Save %sPath%s                     |" % (fg(202), fg(251)))
            print("|    3 - Change URL %sMongoDB%s                   |" % (fg('light_green'), fg(251)))
            print("|    4 - Change DataBase %sMongoDB%s              |" % (fg('light_green'), fg(251)))
            print("|    5 - Change Table %sMongoDB%s                 |" % (fg('light_green'), fg(251)))
            print("|    6 - %sExit%s Edit Config                     |" % (fg('light_red'), fg(251)))
            print("|                                             |")
            print("\\=============================================/\n")
            select = input(" Insert options: ")
            if select == "1":
                print(f" Save Path: {read_conf['root_save']}")
                print(f" MongoDB URL: {read_conf['mongo_url']}")
                print(f" MongoDB DataBase: {read_conf['mongo_db']}")
                print(f" MongoDB Table: {read_conf['mongo_tabs']}\n")
                input("Press Enter to continue...")
            elif select == "2":
                new = input(" Insert New Path: ")
                print(f"New Path Insert: {fg('light_yellow')}{new}{fg(251)}")
                if (query_yes_no("\nare you sure you apply the changes?")):
                    read_conf['root_save'] = new   
                    writer_file(read_conf)
            elif select == "3":
                new = input(" Insert New MongoDB URL: ")
                print(f"New URL Insert: {fg('light_yellow')}{new}{fg(251)}")
                if (query_yes_no("\nare you sure you apply the changes?")):  
                    read_conf['mongo_url'] = new
                    writer_file(read_conf)
            elif select == "4":
                new = input(" Insert New MongoDB DataBase: ")
                print(f"New DataBase Insert: {fg('light_yellow')}{new}{fg(251)}")
                if (query_yes_no("\nare you sure you apply the changes?")):
                    read_conf['mongo_db'] = new
                    writer_file(read_conf)
            elif select == "5":
                new = input(" Insert New Table: ")
                print(f" New Table Insert: {fg('light_yellow')}{new}{fg(251)}")
                if (query_yes_no("\nare you sure you apply the changes?")):
                    read_conf['mongo_tabs'] = new
                    writer_file(read_conf)
            elif select == "6":
                enable = False
            select = 0
    else:
        data = {
            "root_save": r"list.json",
            "mongo_url": "mongodb://localhost:27017/",
            "mongo_db": "List_pc",
            "mongo_tabs": "pc"
        }
        writer_file(data)

def config_read():
    global config
    if (os.path.isfile("config.json")):
        with open("config.json", 'r') as json_data_file:
            config = json.load(json_data_file)
    else:
        config_writer()

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
    print("\n==================== %sINFO%s =====================" % (fg('light_blue'), fg(251)))
    my_system = computer.Win32_ComputerSystem()[0]
    print(f" Computer Name: {platform.node()}")
    print(f" Manufacturer: {my_system.Manufacturer}")
    print(f" Model: {my_system.Model}")

    print("\n==================== %sCPU%s ======================" %  (fg('light_cyan'), fg(251)))
    proc_info = computer.Win32_Processor()[0]
    print(' CPU Name: {0}'.format(proc_info.Name))
    print(f" CPU Type: {platform.processor()}")
    print(f" Machine type: {platform.machine()}")
    print(f" Physical Cores: {psutil.cpu_count(logical=False)}")
    print(f" Logical Cores: {psutil.cpu_count(logical=True)}")

    print("\n==================== %sRAM%s ======================" % (fg('light_magenta'), fg(251)))
    print(f" Total RAM installed: {round(psutil.virtual_memory().total/1000000000, 2)} GB")

    print("\n==================== %sGPU%s ======================" % (fg('light_green'), fg(251)))
    gpu_info = computer.Win32_VideoController()[0]
    print(' GPU Name: {0}'.format(gpu_info.Name))

    print("\n==================== %sDISK%s =====================" % (fg('light_yellow'), fg(251)))
    print(" Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if (partition.device == "C:\\"):
            color = 'light_yellow'
        elif (partition.device == "A:\\" or partition.device == "B:\\"):
            color = 'light_red'
        else:
            color = 6
        print(f"  === Device: {fg(color)}{partition.device}{fg(251)} ===")
        print(f"  | Mountpoint: {partition.mountpoint}")
        print(f"  | File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        print(f"  | Total Size: {get_size(partition_usage.total)}")
        print(f"  | Used: {get_size(partition_usage.used)}")
        print(f"  | Free: {get_size(partition_usage.free)}")
        print(f"  | Percentage: {partition_usage.percent}%\n")

    print("\n==================== %sOS%s =======================" % (fg('light_red'), fg(251)))
    Arch = str(platform.architecture()).replace('"', "").replace('(', "").replace(')', "").replace("'", "")
    print(f" OS: {platform.system()}")
    print(f" OS Release: {platform.release()}")
    print(f" OS Version: {platform.version()}")
    print(f" Platform type: {platform.platform()}")
    print(f" Arch: {Arch}")
    print("\n===============================================\n")
    input("Press Enter to continue...")

def save_json(enable = False):
    global config
    my_system = computer.Win32_ComputerSystem()[0]
    proc_info = computer.Win32_Processor()[0]
    gpu_info = computer.Win32_VideoController()[0]
    partitions = psutil.disk_partitions()
    Disk = {}
    num = 0
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        Disk[str(num)] = {
            "Device": partition.device,
            "Mountpoint": partition.mountpoint,
            "File system": partition.fstype,
            "Total Size": get_size(partition_usage.total),
            "Used": get_size(partition_usage.used),
            "Free": get_size(partition_usage.free),
            "Percentage": str(partition_usage.percent) + "%"
        }
        num = num + 1
    data = {
        "ID": uuid.uuid4().hex,
        "Data Insert": str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
        "INFO": {
            "Computer Name": platform.node(),
            "Manufacturer": my_system.Manufacturer,
            "Model": my_system.Model
        },
        "CPU": {
            "Name": proc_info.Name,
            "Type": platform.processor(),
            "Machine": platform.machine(),
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
            "Arch": str(platform.architecture()).replace('"', "").replace('(', "").replace(')', "").replace("'", "")
        }
    }
    data["DISK"] = Disk
    if (enable):
        db_insert_data(data)
    else :
        if os.getcwd() != config['root_save']:
            os.chdir(config['root_save'])
        write_json(data)

def write_json(new_data, filename='list.json'):
    if os.path.isfile(filename):
        with open(filename, 'a') as outfile:
            outfile.write(",")
            outfile.write(json.dumps(new_data, indent=4))
    else:
        with open(filename, 'a') as outfile:
            outfile.write(json.dumps(new_data, indent=4))
    path_out = os.getcwd() + "\\" + filename
    print("[ %s OK   %s] Saved File: %s\n" % (fg('light_green'), fg(251), path_out))

def db_insert_data(mydict):
    global config
    try:
        myclient = pymongo.MongoClient(config['mongo_url'])
        mydb = myclient[config['mongo_db']]
        mycol = mydb[config['mongo_tabs']]
        mycol.insert_one(mydict)
        print("[ %s OK   %s] Insert Data Compleate\n" % (fg('light_green'), fg(251)))
    except:
        print("[ %sERROR %s] ERROR Fail Insert Data\n" % (fg('light_red'), fg(251)))

def main():
    while True:
        print("%s/=============================================\\" % (fg(251)))
        print("|                                             |")
        print("|      Get System Info by %sAlexkill536ITA%s      |" % (fg('light_yellow'), fg(251)))
        print("|                                             |")
        print("|=============================================|")
        print("|                                             |")
        print("|    1 - Print Info System to %sCLI%s             |" % (fg('light_cyan'), fg(251)))
        print("|    2 - Save Info System to %sJSON%s             |" % (fg(202), fg(251)))
        print("|    3 - Insert To DataBase %sMongoDB%s           |" % (fg('light_green'), fg(251)))
        print("|    4 - Edit %sConfig%s                          |" % (fg('light_yellow'), fg(251)))
        print("|    5 - %sExit%s                                 |" % (fg('light_red'), fg(251)))
        print("|                                             |")
        print("\=============================================/\n")
        config_read()
        select = input(" Insert options: ")
        if select == "1":
            print_cli_data()
        elif select == "2":
            save_json()
        elif select == "3":
            save_json(enable=True)
        elif select == "4":
            config_writer()
        elif select == "5":
            sys.exit()
        select = 0

if __name__ == "__main__":
    main()
