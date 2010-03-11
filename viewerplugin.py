#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gridhelper.py (c) 2009 rene.milk@uni-muenster.de

It is licensed to you under the terms of the WTFPLv2 (see below).

This program is free software. It comes with no warranty,
to the extent permitted by applicable law.


            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar
  14 rue de Plaisance, 75014 Paris, France
 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
"""

from PyQt4 import *
import viewer

class GeoLocationPlugin(QPyDesignerCustomWidgetPlugin):

	def __init__(self, parent = None):
		QPyDesignerCustomWidgetPlugin.__init__(self)
		self.initialized = False

	def initialize(self, formEditor):
		if self.initialized:
			return

		#manager = formEditor.extensionManager()
		#if manager:
			#self.factory = \
				#MeshWidgetTaskMenuFactory(manager)
			#manager.registerExtensions(
				#self.factory,
				#"com.trolltech.Qt.Designer.TaskMenu")

		self.initialized = True

	def createWidget(self, parent):
		return viewer.MeshWidget(parent)

	def name(self):
		return "MeshViewer"

	def includeFile(self):
		return "viewer"

	def group(self):
        return "Custom"

	def icon(self):
		return QtGui.QIcon()

	def toolTip(self):
		return ""

	def whatsThis(self):
		return ""

	def isContainer(self):
		return False

	def domXml(self):
		return (
				'<widget class="MeshWidget" name=\"MeshWidget\">\n'
				" <property name=\"toolTip\" >\n"
				"  <string>The current mesh</string>\n"
				" </property>\n"
				" <property name=\"whatsThis\" >\n"
				"  <string>.</string>\n"
				" </property>\n"
				"</widget>\n"
				)