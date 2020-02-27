# media manager
A small media manager 

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
* ~~p2 - add duration and size~~
* p2 - refractor code
* p2 - Issue warning when the watch folder is large
* p1 - Exception handling
* p2 - Maintain client - server connection
* p2 - enable server mode and module mode in jsonclient and jsonserver. This can decreases the number of servers we need
* p2 - use threading pooling
* p1 - use better update command to avoid multiple socket connections
* p2 - Async promgramming in python
* ~~p1 - Different client should use different database when they are running - register app\_name and database/collection~~
    * ~~p2 - multiple clients support~~
* p1 - `set watcher folders` needs better design. `Add watch folder` and `remove watch folder` should be enabled
* p0 - ~~when files are moved, it is deleted and then created. md5 is calculated again. move never works~~
    * - ~~delete is wrong. Some entry still has the old path~~
* p0 - when to watch? : when server launches, all must be indexed
* p0 - ~~Use cmd module~~
* p0 - Refractoring player to use mime; remove MEDIA\_SUFFIX
* p0 - ~~ remove md5; unique path and name~~
* p0 - avoid duplicate tag
* p2 - enable `update all tags using the search query`
* p2 - creating time?
* p0 - error message logging
* ~~p0 - for different client, watcher should write to different database. ~~

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
* ~~p0 fix: player does not show video~~
* ~~p0 fix: registerred app database/collection are not updated~~
* p0 fix: You cannot always open a thread for each folder
* p1 fix: error message from logging: keyerror: 'host'; reason: logging from other library

# log
* [Sat 15 Feb 2020 10:57:13 PM PST] start testing
* [Mon 17 Feb 2020 11:24:56 AM PST] Refactoring
* [Tue 25 Feb 2020 12:00:00 AM PST] Dogfooding
