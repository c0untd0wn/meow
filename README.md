Meow
====

A platform-independent Github notifier

# Build Environment
## Mac OS X
* Python 2.7.1
* PySide 1.1.0 (which uses Qt 4.8.2)
* cx-Freeze 4.3

# Troubleshooting
cx-Freeze seems to have some problems when freezing Python scripts on Mac OS X
Please edit the macdist.py file as below

* line 106-107: ```subprocess.call(('install_name_tool', '-id',
@executable_path/'+fileName, filePath))
```

* line 146-147: ```libpath = str(QtCore.QLibraryInfo.location( \
path = os.path.join(libpath, subpath)
```

# Etc.
* Icon: http://www.iconspedia.com/icon/black-cat-6166.html
