import PySide
from PySide import QtCore, QtGui, QtSvg

import httplib, urllib
import base64

import json

from dateutil.parser import parse

import os, sys

class Data:
  appPath = os.path.dirname(sys.executable)
  status = False

class Connection(QtCore.QThread):
  def __init__(self, parent=None):
    super(Connection, self).__init__(parent)
    self._running = False

    settings = json.loads(open(Data.appPath+"/setting.json").read())
    self.repos = []
    if settings[u"login"] is True:
      self.token = settings[u"token"]
      Data.status = True
      self.getRepos()

  def auth(self, username, password):
    # encode username:password using base64
    self.username = username
    auth = base64.encodestring('%s:%s' % (username, password))[:-1]

    # fill params, headers, connection
    params = '{"scopes":["repo"]}'
    headers = {"Authorization": "Basic %s" % auth}
    conn = httplib.HTTPSConnection("api.github.com")

    # request and get the response
    conn.request("POST", "/authorizations", params, headers)
    response = conn.getresponse()
    print "\n#### Auth ####"
    print response.status, response.reason
    data = response.read()
    print data
    jsonResponse = json.loads(data)
    self.token = jsonResponse[u"token"].encode('utf-8', 'ignore')

    # close connection
    conn.close()
    Data.status = True
    self.getRepos()


  def simpleApiCall(self, method, url):
    conn = httplib.HTTPSConnection("api.github.com")
    print "{url}?access_token={token}".format(url=url, token=self.token)
    conn.request(method, "{url}?access_token={token}".format(url=url, token=self.token))
    response = conn.getresponse()
    print "\n#### {method}: {url} ####".format(method=method, url=url)
    # print response.status, response.reason
    data = response.read()
    # print data
    conn.close()

    return json.loads(data)

  def getRepos(self):
    # get my repos
    jsonResponse = self.simpleApiCall("GET", "/user/repos")
    # print jsonResponse
    self.repos.extend([repo[u"full_name"].encode('utf-8', 'ignore') for repo in jsonResponse])

    # get repos of my organizations
    jsonResponse = self.simpleApiCall("GET", "/user/orgs")
    orgs = ([org[u"login"].encode('utf-8', 'ignore') for org in jsonResponse])

    for org in orgs:
      jsonResponse = self.simpleApiCall("GET", "/orgs/%s/repos" % org)
      orgRepos = ([repo[u"full_name"].encode('utf-8', 'ignore') for repo in jsonResponse])
      self.repos.extend(orgRepos)

    self.repos = dict([(r, None) for r in self.repos])

    print "\n#### Repos ####"
    print self.repos

  def run(self):
    self._running = True
    while self._running:
      self.getCommits()
      self.msleep(1000*60)

  def stop(self, wait=False):
    self._running = False
    if wait:
      self.wait()

  alarmMsg = QtCore.Signal(str, str)

  def getCommits(self):
    print "\n#### Get Commits ####"
    if self.repos == []:
      print "#### No repos yet! ####"
      return
    for r, t in self.repos.items():
      jsonResponse = self.simpleApiCall("GET", "/repos/%s/commits" % r)
      if jsonResponse.__class__.__name__ == 'list':
        commit = jsonResponse[0][u"commit"]
        msg = commit[u"message"]
        author = commit[u"author"]
        name = author[u"name"]
        date = parse(author[u"date"])
        repo = r
        if t == None:
          self.repos[r] = date
        elif t < date:
          self.repos[r] = date
          growlTitle = "{name} Comitted to {repo}".format(name=name, repo=repo)
          growlMsg = msg
          print "#### %s ####\n" % growlTitle
          # self.emit(QtCore.SIGNAL("SHOWMSG"), growlTitle, growlMsg)
          self.alarmMsg.emit(growlTitle, growlMsg)
          # meow.showMsg(growlTitle, growlMsg)

    print "\n#### Commits Retrieved ####"
    print self.repos


class Preferences(QtGui.QWidget):
  def __init__(self):
    super(Preferences, self).__init__()
    self.initUI()

  accountMsg = QtCore.Signal(str, str)

  def initUI(self):
    formLayout = QtGui.QFormLayout()
    self.usernameEdit = QtGui.QLineEdit()
    self.passwordEdit = QtGui.QLineEdit()
    self.passwordEdit.setEchoMode(QtGui.QLineEdit.Password)
    formLayout.addRow(self.tr("&Username: "), self.usernameEdit)
    formLayout.addRow(self.tr("&Password: "), self.passwordEdit)

    if Data.status is False:
      self.btn = QtGui.QPushButton("&Login", self)
      formLayout.addRow(self.btn)
      self.btn.clicked.connect(self.login)

    else:
      self.btn = QtGui.QPushButton("&Logout", self)
      self.usernameEdit.setReadOnly(True)
      self.passwordEdit.setReadOnly(True)
      formLayout.addRow(self.btn)
      self.btn.clicked.connect(self.login)

    self.setLayout(formLayout)
    self.setWindowTitle('Meow Preferences')

  def login(self):
    if Data.status is False:
      self.btn.setText("&Logout")
      self.usernameEdit.setReadOnly(True)
      self.passwordEdit.setReadOnly(True)
      self.accountMsg.emit(self.usernameEdit.text(), self.passwordEdit.text())
    else:
      Data.status = False
      self.btn.setText("&Login")
      self.usernameEdit.setReadOnly(False)
      self.passwordEdit.setReadOnly(False)
      self.usernameEdit.setText("")
      self.usernameEdit.setText("")


class Meow(QtGui.QSystemTrayIcon):
  def __init__(self):
    super(Meow, self).__init__()

    self.c = Connection(self)
    self.c.alarmMsg.connect(self.showMsg)
    self.initUI()

  def initUI(self):
    menu = QtGui.QMenu()
    menu.addAction('Preferences...', self.preferencesCB)
    menu.addAction('Quit', self.quitCB)
    QtCore.QObject.connect(menu, QtCore.SIGNAL('aboutToShow()'), self.aboutToShowCB)
    self.setContextMenu(menu)
    icon = QtGui.QIcon(Data.appPath+"/cat.png")
    self.setIcon(icon)
    self.p = Preferences()
    self.p.accountMsg.connect(self.c.auth)

  def startThread(self):
    self.c.start()

  def quitCB(self):
    self.c.quit()
    QtGui.QApplication.quit()
  def preferencesCB(self):
    print 'preferences'
    self.p.show()
  def aboutToShowCB(self):
    print 'tray icon clicked'
  def showMsg(self, title, msg):
    self.showMessage(title, msg, QtGui.QSystemTrayIcon.Information, 1000)


app = QtGui.QApplication([])
app.setQuitOnLastWindowClosed(False)
"""
if sys.platform == "darwin":
  import AppKit
  # https://developer.apple.com/library/mac/#documentation/AppKit/Reference/NSRunningApplication_Class/Reference/Reference.html
  NSApplicationActivationPolicyRegular = 0
  NSApplicationActivationPolicyAccessory = 1
  NSApplicationActivationPolicyProhibited = 2
  AppKit.NSApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)
"""
meow = Meow()
meow.show()
meow.startThread()
app.exec_()

del app
