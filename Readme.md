# media manager
A small manager for media

# todo (phase 1)
* ~~implement player~~
* ~~implement watcher~~
* ~~implement indexer~~
* ~~p0 - implement searcher~~
* ~~p0 - implement updateer~~ 
* ~~p0 push indexer to watcher~~
* p1 - ~~JsonClient and JsonServer, JsonProtocol~~
    * ~~JsonClient/Server without database~~
    * ~~JsonClient/Server with database~~
* ~~p1 - add __enter__ and __exit__ in all server to atuo close~~
* ~~p0 - implement server launcher~~
* p0 - ~~use server launcher for python cli.~~ 
* p0 - create a constants.py
* p0 - use logging system to replace the old one
    * use client.log/server.log in /var/log/media\_manager/
    * use init setting
* p0 - remove the strong dependency in mongo
* p1 - Use Cmd/Curse module
* ~~p1 - design scheme for indexer~~
* p2 - add duration and ~~size~~
* p2 - refractor code
* p2 - Issue warning when the watch folder is large
* p1 - Exception handling
* p2 - Maintain client - server connection
* p2 - multiple clients support
* p2 - enable server mode and module mode in jsonclient and jsonserver. This can decreases the number of servers we need
* p2 - use threading pooling
* p1 - use better update command to avoid multiple socket connections

# todo (phase 2)
* p0 - use javascript to talk to servers
* p0 - embeded video player and image viewer
* p0 - build web page on javascript 
* p0 - launch html server

# dependencies
* pymongo
* python-magic
* Daemonize

# Bugs
* ~~p0 fix: when watcher launches, all files are indexed~~
* ~~p0 fix: when folder is removed, watch does not removed the watch folder~~

# log
* [Sat 15 Feb 2020 10:57:13 PM PST] start testing
