Purpose
-------

This script will re-sort your Media Libraries by looking at the timestamps
on your files.

The main use case for this would be to run this after you reset your XBMC
Library and all of your media are now sorted alphabetically instead of by
the date you added the files to your library.

This was inspired by my own personal needs, and apparantly many others
on this thread:
http://forum.xbmc.org/showthread.php?t=58525

How to install and run
----------------------
- Copy this directory to your XBMC userdata addons folder, eg:

    (Vista,Win7): c:\Users\<username>\AppData\Roaming\XBMC\addons\script.sortmoviesbyfiledate

    For other platforms, find your "special://home" path in the wiki:
    http://wiki.xbmc.org/?title=Special_protocol

- Launch XBMC
- Go into "Programs"
- Execute "Sort Media Library"
- Re-launch XBMC (not required, but a good idea to reload the database)

This script should only be ran once, after you create your
media Library for the first time (or after you reset your library.)

All future media added to the library will be added in the
correct chronological order.

How it works
------------
First, some background:  The XBMC Libraries are contained in a SQLite (or MySQL)
database with each resource contained in a row in the respective table.  There is
no timestamp in the database indicating "Date Added", instead, XBMC simply
relies on the order of the rows in the DB.  This is why sorting by
Date Added looks more like sorting by alphabetical order when you
reset your library.

This script changes the order of the resources by modifiying the ID ('idMovie', 'idEpisode' etc.)
column in the respective table to be in the same order as the creation-timestamps
of the files themselves. The id of the resource is also changed in all the additional join tables,
the 'idFile' column is updated in all the required tables.

In order to accomplish this, the first thing the script will do is find the
largest id value in the media table.  If you have 100 movies, then
the largest id will probably be 100.  All of the ID's in the 'movie' table will
then be shifted from 1-100 to 101-200.  The same is done for file ID's
('idFile') in the 'files' table.

Caveats:
--------
- Warning!  I have only done limited testing on this script.

- It was tested on Windows 7, XBMC 10.0 and Linux, XBMC 10.1

- All of my movies were stored remotely via SMB.  It works for local media,
  too, but other protocols may or may not work.

- xbmc.makeLegalFilename() is called on each file returned from XBMC's
  database before trying to access the file, but this may not work on
  all platforms.  Tested on Windows 7 with remote SMB files and on Linux
  with local files.

Known Bugs
----------

To-Do
-----
- support the Music Library, too
- localize the plugin properly

Author
------
Joe Miller - 1/23/2011
www.joeym.net
Michał (Saviq) Sawicz - 4/4/2011
michal@sawicz.net
