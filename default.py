# -*- coding: utf-8 -*-

import os
import xbmcgui, xbmcaddon

from lib.sort import libraryList, Sort

addon = xbmcaddon.Addon("script.sort-media")
SOURCEPATH = addon.getAddonInfo('path')
ACTION_PREVIOUS_MENU = 10

class SortDialog(xbmcgui.WindowXMLDialog):

    def onInit(self):
        self.getControl(1).setLabel("Select library to be sorted")
        self.getControl(5).setLabel("Settings")
        self.list = self.getControl(6)
        self.settings = self.getControl(5)

        self.list.controlLeft(self.settings)
        self.list.controlRight(self.list)

        self.settings.controlLeft(self.settings)
        self.settings.controlRight(self.settings)
        self.settings.controlUp(self.list)
        self.settings.controlDown(self.settings)

        self.library = None

        for item in libraryList:
            listitem = xbmcgui.ListItem(item[1], iconImage=item[2])
            self.list.addItem(listitem)

        self.setFocus(self.list)

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        if controlID in (3, 6):
            self.library = self.list.getSelectedPosition()
            self.close()
        elif controlID == 5:
            addon.openSettings()

    def onFocus(self, controlID):
        pass

if __name__ == '__main__':
    w = SortDialog("DialogSelect.xml", SOURCEPATH)
    w.doModal()

    if w.library is not None:
        dp = xbmcgui.DialogProgress()
        dp.create("Sorting %s" % libraryList[w.library][1])

        Sort(w.library, lambda x, y: dp.update(x, y))

        dp.close()
        del dp

        xbmcgui.Dialog().ok("Sorting %s" % libraryList[w.library][1], "Sorting complete")

    w.close()
    del w
