#!/usr/bin/python3

from client import MediaManagerClient

class MyJav(MediaManagerClient):
    def __init__(self):
        super().__init__()
        self.watch_folders = [
                "/home/weibing/WindowsData/OneDrive/Ntest/", 
                "/home/weibing/Downloads/", 
                "/home/weibing/dwhelper/"]
        self.database = "MyJav"
        self.collection = "FileList"

def main():
    myjav = MyJav()
    myjav.run()

if __name__ == "__main__":
    main()
