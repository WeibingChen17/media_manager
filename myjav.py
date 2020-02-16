#!/usr/bin/python3
from client import MediaManagerClient


database = "MyJav"
collection = "FileList"
watch_folders = [
        "/home/weibing/WindowsData/OneDrive/Ntest/", 
        "/home/weibing/WindowsData/Downloads",
        "/home/weibing/Downloads/", 
        "/home/weibing/dwhelper/"]

def main():
    myjav = MediaManagerClient()
    myjav.set_database(database)
    myjav.set_collection(collection)
    myjav.set_watch_folders(watch_folders)
    myjav.run()

if __name__ == "__main__":
    main()
