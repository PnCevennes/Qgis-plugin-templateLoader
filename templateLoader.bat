@echo off
IF exist %UserProfile%\.qgis2\python\plugins ( echo QGIS dir exists )
ELSE ( echo QGIS dir doesn't exists contact an administrator Exit)