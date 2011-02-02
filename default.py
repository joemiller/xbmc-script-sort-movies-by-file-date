import os
import re
import xbmc
import xbmcaddon
from stat import *
from operator import itemgetter
from urllib import quote_plus, unquote_plus

Addon = xbmcaddon.Addon(id=os.path.basename(os.getcwd()))

class Main:

    def __init__(self):
        if(Addon.getSetting('debug')):
            self.debug = True

        max_movie_id = self.get_max_movie_id()
        max_file_id  = self.get_max_file_id()
        movie_list   = self.get_movies()

        # iterate through each video, sorting by ctime, then update
	# the video's id in the database
        i = 0
        for movie in sorted(movie_list, key=itemgetter(0)):
            (ctime, old_idMovie, old_idFile, fullFilePath) = (movie[0], movie[1], movie[2], movie[3])
            i += 1
            new_idMovie = max_movie_id + i
            new_idFile  = max_file_id + i
            if self.debug:
                xbmc.log("ctime: %d old_idMovie: %d new_idMovie: %d old_idFile: %d new_idFile: %d file: %s" %
                         (ctime, old_idMovie, new_idMovie, old_idFile, new_idFile, fullFilePath))
            self.update_movie_and_file_id(old_idMovie, new_idMovie, old_idFile, new_idFile)
        
        xbmc.log('script.sortmoviesbyfiledate addon run complete')

    def get_max_movie_id(self):
        get_maxid_sql = "select max(idMovie) from movieview"
        sql_result = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( get_maxid_sql ), )
        return int((re.findall( "<field>(.+?)</field>", sql_result, re.DOTALL ))[0])

    def get_max_file_id(self):
        get_maxid_sql = "select max(idFile) from files"
        sql_result = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( get_maxid_sql ), )
        return int((re.findall( "<field>(.+?)</field>", sql_result, re.DOTALL ))[0])

    def get_movies(self):
        """ fetch the idMovie, idFile, and path+filename of all movies in
            the Movie Library, then stat each file to get the CTIME
            (creation time).  Returns a list of tuples containing
              (ctime, idMovie, idFile, filename)
            eg:
            
            [ (12312312312, 1, 5, "c:/Movies/Gladiator (2000)/gladiator.mkv"),
              (12423234223, 2, 4, "smb://user:pass@server/Movies/Something (2010)/something.avi") ]
        """
        movie_list = []
        xbmc.executehttpapi( "SetResponseFormat()" )
        xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( "<record>", ) )
        xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( "</record>", ) )

        movies_sql = "select idMovie,idFile,strPath,strFileName from movieview"
        sql_result = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( movies_sql ), )
        records = re.findall( "<record>(.+?)</record>", sql_result, re.DOTALL )
        for record in records:
            fields = re.findall( "<field>(.*?)</field>", record, re.DOTALL )
            idMovie = int(fields[0])
            idFile  = int(fields[1])
            strPath = xbmc.makeLegalFilename(fields[2])
            strFileName = xbmc.makeLegalFilename(fields[3])
            fullFilePath = xbmc.makeLegalFilename(os.path.join(strPath, strFileName))
	    try:
            	ctime = os.stat(fullFilePath)[ST_CTIME]
            	movie_list.append( (ctime, idMovie, idFile, fullFilePath) )
	    except OSError, e:
	        xbmc.log("OSerror: %s, file: %s" % (e.strerror, e.filename))
        return movie_list

    def update_movie_and_file_id(self, old_idMovie, new_idMovie, old_idFile, new_idFile):
        update_sql = ("update movie set idMovie=%d, idFile=%d where idMovie=%d" %
                     (new_idMovie, new_idFile, old_idMovie))
        xbmc.executehttpapi( "ExecVideoDatabase(%s)" % quote_plus( update_sql ), )
        
        update_sql = ("update files set idFile=%d where idFile=%d" %
                     (new_idFile, old_idFile))
        xbmc.executehttpapi( "ExecVideoDatabase(%s)" % quote_plus( update_sql ), )

        
#run the program
run_program = Main()
