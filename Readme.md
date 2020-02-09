# media manager
A small manager for media

# todo (phase 1)
* ~~implement player~~
* ~~implement watcher~~
* ~~implement indexer~~
* ~~p0 - implement searcher~~
* ~~p0 - implement updateer~~ 
* ~~p0 push indexer to watcher~~
* p1 - JsonClient and JsonServer, JsonProtocol
    * ~~JsonClient/Server without database~~
    * ~~JsonClient/Server with database~~
* p0 - remove the strong dependency in mongo
* ~~p1 - add __enter__ and __exit__ in all server to atuo close~~
* ~~p0 - implement server launcher~~
* p0 - use server launcher for python cli. Use Cmd module
* p0 - use logging 
* p1 - design scheme for indexer
    * add duration and size 
* p2 - refractor code
* p2 - Issue warning when the watch folder is large
* p1 - Exception handling
* p2 - Maintain client - server connection
* p2 - multiple clients support

# todo (phase 2)
* p0 - use javascript to talk to servers
* p0 - embeded video player and image viewer
* p0 - build web page on javascript 
* p0 - launch html server

# dependencies
* pymongo
* filetype
* Daemonize

# Bugs
* p0 fix: when watcher launches, all files are indexed
