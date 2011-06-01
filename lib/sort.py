# -*- coding: utf-8 -*-

from platform import system
import os
import re
import xbmc
import xbmcaddon
from stat import *
from operator import itemgetter
from urllib import quote_plus, unquote_plus
from datetime import datetime

MOVIES, TV_EPISODES, MUSIC_VIDEOS = range(3)

libraryList =((MOVIES, "Movies", "DefaultMovies.png"),
              (TV_EPISODES, "TV Episodes", "DefaultTVShows.png"),
              (MUSIC_VIDEOS, "Music Videos", "DefaultMusicVideos.png"),
             )

addon = xbmcaddon.Addon(id='script.sort-media')

class Sort:

    def __init__(self, library, progress=None):
        if(addon.getSetting('debug')):
            self.debug = True
            sort_setting = addon.getSetting('sort_key')
        if (sort_setting == "Platform default" and system() == 'Windows') \
         or sort_setting == "Creation (Windows)":
            self.sort_key = ST_CTIME
            self.debug and xbmc.log("[media-sort] using CTIME")
        else:
            self.sort_key = ST_MTIME
            self.debug and xbmc.log("[media-sort] using MTIME")

        self.library = libraryList[library][0]
        self.progress = progress

        max_item_id = self.get_max_item_id()
        max_file_id = self.get_max_file_id()
        item_list   = self.get_items()

        # iterate through each item, sorting by ctime, then update
        # the item's id in the database
        i = 0
        count = len(item_list)

        self.debug and xbmc.log("[media-sort] max_item_id: %d max_file_id: %d item_count:%d" % (max_item_id, max_file_id, len(item_list)))

        for item in sorted(item_list, key=itemgetter(0)):
            if self.progress:
                self.progress(int(i * 100 / count), item[4])
            (ctime, old_idItem, old_idFile, fullFilePath) = (item[0], item[1], item[2], item[3])
            i += 1
            new_idItem = max_item_id + i
            new_idFile  = max_file_id + i
            if self.debug:
                xbmc.log("[media-sort] time: %s old_idItem: %d new_idItem: %d old_idFile: %d new_idFile: %d file: %s" %
                         (str(datetime.fromtimestamp(ctime)), old_idItem, new_idItem, old_idFile, new_idFile, fullFilePath))
            self.update_item_and_file_id(old_idItem, new_idItem, old_idFile, new_idFile)

        xbmc.log('[media-sort] sorting complete')

    def get_max_item_id(self):
        if self.library == MOVIES:
            get_maxid_sql = "select max(idMovie) from movieview"
        elif self.library == TV_EPISODES:
            get_maxid_sql = "select max(idEpisode) from episodeview"
        elif self.library == MUSIC_VIDEOS:
            get_maxid_sql = "select max(idMVideo) from musicvideoview"

        if self.library in (MOVIES, TV_EPISODES, MUSIC_VIDEOS):
            sql_result = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( get_maxid_sql ), )
        return int((re.findall( "<field>(.+?)</field>", sql_result, re.DOTALL ))[0])

    def get_max_file_id(self):
        get_maxid_sql = "select max(idFile) from files"
        if self.library in (MOVIES, TV_EPISODES, MUSIC_VIDEOS):
            sql_result = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( get_maxid_sql ), )
        return int((re.findall( "<field>(.+?)</field>", sql_result, re.DOTALL ))[0])

    def get_items(self):
        """ fetch the idItem, idFile, and path+filename of all items in
            the Library, then stat each file to get the CTIME / MTIME
            (creation time).  Returns a list of tuples containing
              (ctime, idItem, idFile, filename, title)
            eg:

            [ (12312312312, 1, 5, "c:/Movies/Gladiator (2000)/gladiator.mkv", "Gladiator"),
              (12423234223, 2, 4, "smb://user:pass@server/Movies/Something (2010)/something.avi", "Something") ]
        """
        item_list = []
        xbmc.executehttpapi( "SetResponseFormat()" )
        xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( "<record>", ) )
        xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( "</record>", ) )

        if self.library == MOVIES:
            items_sql = "select idMovie,idFile,strPath,strFileName,c00 from movieview"
        elif self.library == TV_EPISODES:
            items_sql = "select idEpisode,idFile,strPath,strFileName,c00 from episodeview"
        elif self.library == MUSIC_VIDEOS:
            items_sql = "select idMVideo,idFile,strPath,strFileName,c00 from musicvideoview"
        if self.library in (MOVIES, TV_EPISODES, MUSIC_VIDEOS):
            sql_result = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( items_sql ), )
        records = re.findall( "<record>(.+?)</record>", sql_result, re.DOTALL )
        for record in records:
            fields = re.findall( "<field>(.*?)</field>", record, re.DOTALL )
            idItem = int(fields[0])
            idFile  = int(fields[1])
            # only choose the first file from a stack
            if fields[3].startswith('stack://'):
                fields[3] = fields[3][8:].split(' , ')[0].replace(',,', ',')
            strPath = xbmc.makeLegalFilename(fields[2])
            strFileName = xbmc.makeLegalFilename(fields[3])
            fullFilePath = xbmc.makeLegalFilename(os.path.join(strPath, strFileName))
            strTitle = fields[4]
            try:
                ctime = os.stat(fullFilePath)[self.sort_key]
                item_list.append( (ctime, idItem, idFile, fullFilePath, strTitle) )
            except OSError, e:
                xbmc.log("[media-sort] OSerror: %s, file: %s" % (e.strerror, e.filename))
        return item_list

    def update_item_and_file_id(self, old_idItem, new_idItem, old_idFile, new_idFile):
        sql_dict = {'newItemId': new_idItem, 'newFileId': new_idFile, 'oldItemId': old_idItem, 'oldFileId': old_idFile}
        if self.library == MOVIES:
            update_sql = ["update movie set idMovie=%(newItemId)d, idFile=%(newFileId)d where idMovie=%(oldItemId)d;",
                          "update actorlinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d;",
                          "update countrylinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d;",
                          "update directorlinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d;",
                          "update genrelinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d;",
                          "update movielinktvshow set idMovie=%(newItemId)d where idMovie=%(oldItemId)d;",
                          "update setlinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d;",
                          "update studiolinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d;",
                          "update writerlinkmovie set idMovie=%(newItemId)d where idMovie=%(oldItemId)d;"]

        elif self.library == TV_EPISODES:
            update_sql = ["update episode set idEpisode=%(newItemId)d, idFile=%(newFileId)d where idEpisode=%(oldItemId)d;",
                          "update actorlinkepisode set idEpisode=%(newItemId)d where idEpisode=%(oldItemId)d;",
                          "update directorlinkepisode set idEpisode=%(newItemId)d where idEpisode=%(oldItemId)d;",
                          "update tvshowlinkepisode set idEpisode=%(newItemId)d where idEpisode=%(oldItemId)d;",
                          "update writerlinkepisode set idEpisode=%(newItemId)d where idEpisode=%(oldItemId)d;"]

        elif self.library == MUSIC_VIDEOS:
            update_sql = ["update musicvideo set idMVideo=%(newItemId)d, idFile=%(newFileId)d where idMVideo=%(oldItemId)d;",
                          "update actorlinkmusicvideo set idMVideo=%(newItemId)d where idMVideo=%(oldItemId)d;",
                          "update directorlinkmusicvideo set idMVideo=%(newItemId)d where idMVideo=%(oldItemId)d;",
                          "update genrelinkmusicvideo set idMVideo=%(newItemId)d where idMVideo=%(oldItemId)d;",
                          "update studiolinkmusicvideo set idMVideo=%(newItemId)d where idMVideo=%(oldItemId)d;"]

        if self.library in (MOVIES, TV_EPISODES, MUSIC_VIDEOS):
            update_sql += ["update files set idFile=%(newFileId)d where idFile=%(oldFileId)d;",
                          "update bookmark set idFile=%(newFileId)d where idFile=%(oldFileId)d;",
                          "update stacktimes set idFile=%(newFileId)d where idFile=%(oldFileId)d;",
                          "update streamdetails set idFile=%(newFileId)d where idFile=%(oldFileId)d;"]

            for q in update_sql:
                xbmc.executehttpapi( "ExecVideoDatabase(%s)" % quote_plus( q % sql_dict ), )
