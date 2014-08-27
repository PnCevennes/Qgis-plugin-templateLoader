@echo off
If not exist %UserProfile%\.qgis2\python\plugins (
	Echo QGIS dir doesn't exists contact an administrator 
	Exit /b
) ELSE Echo QGIS dir exist

IF exist %UserProfile%\.qgis2\python\plugins\templateLoader (
	rmdir /S /Q %UserProfile%\.qgis2\python\plugins\templateLoader
	Echo QGIS templateLoader dir deleted
)

mkdir %UserProfile%\.qgis2\python\plugins\templateLoader
xcopy /D /E /C /R /H /I /K /Y /Q "templateLoader" %UserProfile%\.qgis2\python\plugins\templateLoader

REG ADD "HKEY_CURRENT_USER\Software\QGIS\QGIS2\PythonPlugins" /v "templateLoader" /d "true"  /f
