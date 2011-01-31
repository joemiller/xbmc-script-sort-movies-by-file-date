Purpose
-------

This script will "fix" the "sort-by: Date Added" feature in your Movie Library.  It does this
by looking at the file creation time of all of the movies in your library and re-sorting the
movie database using these timestamps.

The main use case for this would be after you have to reset your XBMC Library and all of
your movies are now sorted alphabetically instead of by the date you added the files
to your library.

This was inspired by my own personal needs, and apparantly many others on this thread:
http://forum.xbmc.org/showthread.php?t=58525

How to install and run
----------------------
- Copy this directory to your XBMC userdata addons folder, eg:

  (Vista,Win7): c:\Users\<username>\AppData\Roaming\XBMC\addons\script.fixmoviesdateadded

   For other platforms, find your "special://home" path in the wiki: 
     http://wiki.xbmc.org/?title=Special_protocol

- Launch XBMC
- Go into "Programs"
- Execute "Fix Movie Date's Added"
- Re-launch XBMC (may not be required, but probably a good idea to reload the database)


How it works
------------
First, some background:  The XBMC Movie Library is contained in a SQLite database with each
movie contained in a row in the 'movie' table.  There is no timestamp in the database
indicating "Date Added", instead, XBMC simply relies on the order of the rows in the DB.
This is why sorting by Date Added looks more like sorting by alphabetical order when you
reset your movie library.

This script changes the order of the movies by modifiying the ID ('idMovie') column in
the 'movies' table to be in the same order as the creation-timestamps of the movie 
files themselves.  The 'idFile' column is also updated in both the 'movie' table and
the 'files' table.

In order to accomplish this, the first thing the script will do is find the largest 'idMovie'
value in the 'movie' table.  If you have 100 movies, then this id will probably be 100. 
All of the ID's in the 'movie' table will be shifted to be between 101 and 200. 
The same is done for file ID's in the 'files' table.

Each time the script is run, the ID's will be shifted higher.  This will leave a lot of holes
at the "bottom" of the ID range, but this should not be a problem.  It doesn't look like
XBMC uses the movie ID for anything other than sort order (as far as I know.)  However,
because of this, I wouldn't recommend running this script very often.  You should
only need to run it after you reset your Library.

Caveats:
--------
I have only done limited testing on this script.  It was tested on Windows 7, XBMC 10.0,
and all of my movies were stored remotely via SMB.  It should work for local movies too,
but other protocols may not work.  

Known Bugs
----------

1. Script will break if a movie in your library no longer exists on disk.
   Workaround:  clean library before running this script

Author
------
Joe Miller - 1/23/2011
www.joeym.net