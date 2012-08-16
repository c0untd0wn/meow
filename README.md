Meow
====

A platform-independent Github notifier

# Build Environment
## Mac OS X
* Python 2.7.1
* PySide 1.1.0 (which uses Qt 4.8.2)
* cx-Freeze 4.3

## Windows
* Python 2.7.3
* PySide 1.1.1
* cx-Freeze 4.3

# How to Build
```python build.py 
```
This command automatically builds meow depending on the host OS

# Troubleshooting
## Mac OS X
cx-Freeze seems to have some problems when freezing Python scripts on Mac OS X
Please edit the macdist.py file as below

* line 106-107: ```subprocess.call(('install_name_tool', '-id',
@executable_path/'+fileName, filePath))
```

* line 146-147: ```libpath = str(QtCore.QLibraryInfo.location( \
path = os.path.join(libpath, subpath)
```

## Windows
The default Python installation may not have some required libraries
The common missing libraries are listed below
* python-dateutil
* six

# Etc.
* Icon: http://www.iconspedia.com/icon/black-cat-6166.html
