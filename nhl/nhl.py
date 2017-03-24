import sys
import cgi
import mc
import re
import time
import xbmc
import urllib2
import calendar
import cookielib
import bxtools as bt
import datetime as dt
import simplejson as json
from urllib import quote, quote_plus, urlencode
from xml.dom.minidom import parse, parseString

teams = {
   "ana":	{"full": "Anaheim Ducks", "code": "ducks", "short": "Ducks"},
   "atl":	{"full": "Atlanta Thrashers", "code": "thrashers", "short": "Thrashers"},
   "bos":	{"full": "Boston Bruins", "code": "bruins", "short": "Bruins"},
   "buf":	{"full": "Buffalo Sabres", "code": "sabres", "short": "Sabres"},
   "cgy":	{"full": "Calgary Flames", "code": "flames", "short": "Flames"},
   "car":	{"full": "Carolina Hurricanes", "code": "hurricanes", "short": "Hurricanes"},
   "chi":	{"full": "Chicago Blackhawks", "code": "blackhawks", "short": "Blackhawks"},
   "col":	{"full": "Colorado Avalanche", "code": "avalanche", "short": "Avalanche"},
   "clb":	{"full": "Columbus Blue Jackets", "code": "bluejackets", "short": "Blue Jackets"},
   "cbj":	{"full": "Columbus Blue Jackets", "code": "bluejackets", "short": "Blue Jackets"},
   "dal":	{"full": "Dallas Stars", "code": "stars", "short": "Stars"},
   "det":	{"full": "Detroit Red Wings", "code": "redwings", "short": "Red Wings"},
   "edm":	{"full": "Edmonton Oilers", "code": "oilers", "short": "Oilers"},
   "fla":	{"full": "Florida Panthers", "code": "panthers", "short": "Panthers"},
   "los":	{"full": "Los Angeles Kings", "code": "kings", "short": "Kings"},
   "lak":	{"full": "Los Angeles Kings", "code": "kings", "short": "Kings"},
   "min":	{"full": "Minnesota Wild", "code": "wild", "short": "Wild"},
   "mtl":	{"full": "Montreal Canadiens", "code": "canadiens", "short": "Canadiens"},
   "nsh":	{"full": "Nashville Predators", "code": "predators", "short": "Predators"},
   "njd":	{"full": "New Jersey Devils", "code": "devils", "short": "Devils"},
   "nyi":	{"full": "New York Islanders", "code": "islanders", "short": "Islanders"},
   "nyr":	{"full": "New York Rangers", "code": "rangers", "short": "Rangers"},
   "ott":	{"full": "Ottawa Senators", "code": "senators", "short": "Senators"},
   "phi":	{"full": "Philadelphia Flyers", "code": "flyers", "short": "Flyers"},
   "phx":	{"full": "Phoenix Coyotes", "code": "coyotes", "short": "Coyotes"},
   "pit":	{"full": "Pittsburgh Penguins", "code": "penguins", "short": "Penguins"},
   "sjs":	{"full": "San Jose Sharks", "code": "sharks", "short": "Sharks"},
   "stl":	{"full": "St. Louis Blues", "code": "blues", "short": "Blues"},
   "tbl":	{"full": "Tampa Bay Lightning", "code": "lightning", "short": "Lightning"},
   "tor":	{"full": "Toronto Maple Leafs", "code": "mapleleafs", "short": "Maple Leafs"},
   "van":	{"full": "Vancouver Canucks", "code": "canucks", "short": "Canucks"},
   "wsh":	{"full": "Washington Capitals", "code": "capitals", "short": "Capitals"}
   }

def log(msg, alert=False, func=''):
   if func: func = '('+str(func).lower()+') '
   mc.LogInfo('@nhlgcl %s%s' % (func, str(msg).lower()))
   if alert:
      mc.ShowDialogOk("NHL GameCenter", 'The following error has occurred: ' + str(msg).capitalize())
      mc.HideDialogWait()
      return False

#def getJson(url=False, data=False):
#    try:
#        if url: data = mc.Http().Get(url)
#        data = json.loads(data)
#        return data
#    except Exception, e:
#        return log(e, True, 'getjson')

def play(item):
   user.commitLogin()
   gameFilter = mc.GetApp().GetLocalConfig().GetValue('GameFilterByType')

   if gameFilter == 'live' and user.vaultOnly:
      dialog.show('NHL GAMECENTER', 'You are currently logged in with an NHL GAMECENTER VAULT subscription however an NHL GAMECENTER LIVE subscription is required to watch live games.')
      return False

   if user.isLoggedIn:

      if gameFilter == 'live' and item.GetProperty('gameState') == '':
         dialog.show('NHL GAMECENTER', 'This game is not yet available.  Please check back soon.')
         return False

      id = item.GetProperty('id')

      ourl_link = 'http://www.nhl.com/ice/recap.htm?id=%s' % id
      app_link = 'app://nhl/start?%s'
      direct_link = 'http://www.nhl.com/ice/gamecenterlive.htm?id=%s' % id
      flash_link = 'flash://nhl.com/src=%s&bx-cookie=%s&bx-ourl=%s'
      item_path = flash_link % (quote_plus(direct_link), quote_plus(user.cookies), quote_plus(ourl_link))

      title = item.GetLabel()
      twitter = '@nhl #%s v #%s'
      alt_label = twitter % (item.GetProperty('awayName'), item.GetProperty('homeName'))
      alt_label = alt_label.lower()

      alt_label = title

      params = {
         'title': item.GetLabel(),
         'game-id': str(id),
         'bx-ourl': ourl_link,
         'awayName': item.GetProperty('awayName'),
         'homeName': item.GetProperty('homeName')
         }

      app_link = app_link % (urlencode(params))

      ext = mc.ListItem()
      ext.SetLabel(alt_label)
      ext.SetTitle(title)
      ext.SetDescription(item.GetDescription(), False)
      ext.SetContentType('application/x-shockwave-flash')
      ext.SetThumbnail('http://dir.boxee.tv/apps/nhl/nhl_shield.png')
      ext.SetProviderSource("NHL GameCenter")
      ext.SetPath(app_link)
      item.SetProviderSource("NHL GameCenter")
      item.SetThumbnail('http://dir.boxee.tv/apps/nhl/nhl_shield.png')
      item.SetLabel(alt_label)
      item.SetTitle(title)
      item.SetAddToHistory(True)
      item.SetReportToServer(True)
      item.SetExternalItem(ext)

      item.SetPath(item_path)

      if not config.GetValue('firstplay'):
         config.SetValue('firstplay', 'true')
         mc.ShowDialogOk('NHL GAMECENTER', 'Some users may see improved quality by disabling hardware assisted decoding. If your having issues, go to Boxee settings under Media > Advanced and uncheck this box.')

      mc.GetPlayer().Play(item)
      return True
   else:
      mc.ShowDialogOk('NHL GameCenter Live', 'There was a problem authenticating your account. Please log in again.')
      user.commitLogout()
      return False

def launch(args):
   if not args:
      mc.ActivateWindow(14000)
   elif not user.isLoggedIn:
      mc.ShowDialogOk('NHL GAMECENTER', 'You must be logged into NHL GameCenter before you can watch this game.')
      mc.ActivateWindow(14000)
   else:
      user.commitLogin()
      gameFilter = mc.GetApp().GetLocalConfig().GetValue('GameFilterByType')

      if gameFilter == 'live' and user.vaultOnly:
         dialog.show('NHL GAMECENTER', 'You are currently logged in with an NHL GAMECENTER VAULT subscription however an NHL GAMECENTER LIVE subscription is required to watch live games.')
         return False

      if user.isLoggedIn:
         #id = item.GetProperty('id')
         ourl_link = 'http://www.nhl.com/ice/recap.htm?id=%s' % args['game-id'][0]
         app_link = 'app://nhl/start?%s'
         direct_link = 'http://www.nhl.com/ice/gamecenterlive.htm?id=%s' % args['game-id'][0]
         flash_link = 'flash://nhl.com/src=%s&bx-cookie=%s&bx-ourl=%s'
         item_path = flash_link % (quote_plus(direct_link), quote_plus(user.cookies), quote_plus(args['bx-ourl'][0]))

         title = args['title'][0]
         twitter = '@nhl #%s v #%s'
         alt_label = twitter % (args['awayName'][0], args['homeName'][0])
         alt_label = alt_label.lower()

         alt_label = title

         params = {
            'game-id': str(id),
            'bx-ourl': ourl_link,
            'awayName': args['awayName'][0],
            'homeName': args['homeName'][0]
            }

         app_link = app_link % (urlencode(params))

         item = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
         ext = mc.ListItem(mc.ListItem.MEDIA_VIDEO_OTHER)
         ext.SetLabel(alt_label)
         ext.SetTitle(title)
         #ext.SetDescription(item.GetDescription(), False)
         ext.SetContentType('application/x-shockwave-flash')
         ext.SetThumbnail('http://lavonardo.net/wp/wordpress/wp-content/uploads/2008/02/nhl_shield.png')
         ext.SetProviderSource("NHL GameCenter")
         ext.SetPath(app_link)
         item.SetProviderSource("NHL GameCenter")
         item.SetThumbnail('http://lavonardo.net/wp/wordpress/wp-content/uploads/2008/02/nhl_shield.png')
         item.SetLabel(alt_label)
         item.SetTitle(title)
         item.SetAddToHistory(True)
         item.SetReportToServer(True)
         item.SetExternalItem(ext)

         item.SetPath(item_path)
         item.Dump()
         mc.GetPlayer().Play(item)
         return True
      else:
         mc.ShowDialogOk('NHL GameCenter Live', 'There was a problem authenticating your account. Please log in again.')
         user.commitLogout()
         return False


def updateGameView():

   type = config.GetValue('GameFilterByType')

   if not user.isLoggedIn and type != 'highlight':
      return False

   mc.ShowDialogWait()

   baseUrl = 'rss://dir.boxee.tv/apps/nhl/nhl.php?'
   window = mc.GetWindow(14001)
   window.GetControl(1234).SetVisible(False)
   window.GetList(2000).SetItems(mc.ListItems())

   params = {}

   team = config.GetValue('GameFilterByTeam')
   season = config.GetValue('GameFilterBySeason')
   date = config.GetValue('GameFilterByDate')

   if team:
      window.GetButton(1001).SetLabel(teams[team]['short'])

   if type != 'highlight':
      params['user'] = user.username
      params['pass'] = user.password

   if type not in ['live', 'classic', 'highlight']:
      if team: params['team'] = team
      if season: params['season'] = season
      if date: params['date'] = date

   params[type] = 'true'

   if type == 'live':
      params['t'] = int(time.time())

   url = baseUrl + urlencode(params)
   items = mc.GetDirectory(url)
   window.GetList(2000).SetItems(items)

   if items: window.GetControl(1234).SetVisible(False)
   else: window.GetControl(1234).SetVisible(True)
   
   mc.HideDialogWait()

def updateStandingsView():
   mc.ShowDialogWait()
   window = mc.GetWindow(14003)
   view = config.GetValue('StandingsFilter')
   url = 'rss://dir.boxee.tv/apps/nhl/nhl.php?standings=' + view
   items = mc.GetDirectory(url)
   window.GetList(1003).SetItems(items)
   mc.HideDialogWait()

def loadNewsItems():
   try:
      if (len(mc.GetWindow(14000).GetList(301).GetItems()) == 0):
         mc.ShowDialogWait()
         items = mc.GetDirectory('rss://dir.boxee.tv/apps/nhl/nhl.php?news')
         mc.HideDialogWait()
         if len(items) > 0:
            mc.GetWindow(14000).GetList(301).SetItems(items)
   except:
      mc.HideDialogWait()

def loadNewsDialg():
   list = mc.GetActiveWindow().GetList(301)
   item = list.GetItem(list.GetFocusedItem())
   items = mc.ListItems()
   items.append(item)
   mc.GetWindow(14005).GetList(3999).SetItems(items)
   return item.GetLabel()

def onLogout():

   if not user.isLoggedIn:
      return False

   mc.ShowDialogWait()
   baseUrl = 'http://dir.boxee.tv/apps/nhl/nhl.php?logout&'
   window = mc.GetWindow(14001)
   params = {}
   params['user'] = user.username
   params['pass'] = user.password
   url = baseUrl + urlencode(params)
   items = mc.Http().Get(url)
   mc.HideDialogWait()


def setGamesSubCategory(buttonId):
   if not user.isLoggedIn and buttonId != 223:
      dialog.setDefaultMessage()
      dialog.show()
   else:

      config = mc.GetApp().GetLocalConfig()
      if buttonId != 223 and (not browser.archived or not browser.condensed):
         browser.loadAvailableGameDates(user.username, user.password)

      for id in range(221,226):
         if id != buttonId:
            config.Reset(str(id))
         else:
            config.SetValue(str(id), 'true')
      if buttonId == 221:
         config.SetValue('GameFilterByType', 'live')
      if buttonId == 222:
         config.SetValue('GameFilterByType', 'condensed')
         if browser.type != 'condensed':
            browser.type = 'condensed'
            browser.loadCalendar()
            browser.updateBrowserView()
      if buttonId == 223:
         config.SetValue('GameFilterByType', 'highlight')
      if buttonId == 224:
         config.SetValue('GameFilterByType', 'classic')
      if buttonId == 225:
         config.SetValue('GameFilterByType', 'archive')
         if browser.type != 'archived':
            browser.type = 'archived'
            browser.loadCalendar()
            browser.updateBrowserView()
         else:
            browser.buildGuiCalendar()

   updateGameView()

class nhlDialog:

   title = ''
   message = ''
   config = mc.GetApp().GetLocalConfig()

   def __init__(self):
      self.setDefaultMessage()
      self.config.Reset('dialog_title')
      self.config.Reset('dialog_message')

   def show(self, title='', msg=''):
      if title: self.title = title
      if msg: self.message = msg
      self.config.SetValue('dialog_title', self.title)
      self.config.SetValue('dialog_message', self.message)
      mc.ActivateWindow(14053)

   def close(self):
      xbmc.executebuiltin('Dialog.Close(14053)')
      self.config.Reset('dialog_title')
      self.config.Reset('dialog_message')

   def setDefaultMessage(self):
      self.title = 'SUBSCRIPTION REQUIRED'
      self.message = "To view this content, you'll need an active subscription to [COLOR ff13c3d7]NHL GameCenter LIVE[/COLOR]. (visit http://gamecenter.nhl.com/nhlgc)[CR][CR]Please enter your login information in the settings panel located at the top right corner of the screen."

class userAccount:

   username = ''
   password = ''
   firstName = ''
   cookies = ''
   refresh = False
   isLoggedIn = False
   vaultOnly = False
   hasSubscription = False
   config = mc.GetApp().GetLocalConfig()

   def __init__(self):
      #on load we'll check for saved account details
      cf = mc.GetApp().GetLocalConfig()
      self.username = cf.GetValue('auth_user')
      self.password = cf.GetValue('auth_pwd')
      self.commitLogin()

   def commitLogout(self):
      onLogout()
      self.clearStoredCreds()
      self.isLoggedIn = False
      self.username = ''
      self.password = ''
      self.firstName = ''
      self.cookies = ''
      self.refresh = False
      self.vaultOnly = False
      self.hasSubscription = False
      self.config.Reset('221')
      self.config.Reset('222')
      self.config.Reset('224')
      self.config.Reset('225')
      self.config.SetValue('223', 'true')
      self.config.SetValue('GameFilterByTeam', '')
      self.config.SetValue('GameFilterByType', 'highlight')
      xbmc.executebuiltin('Dialog.Close(14004)')
      mc.ActivateWindow(14000)

   def clearStoredCreds(self):
      cf = mc.GetApp().GetLocalConfig()
      cf.Reset('auth_user')
      cf.Reset('auth_pwd')
      cf.Reset('auth_name')
      cf.Reset('auth_nhl')

   def commitLogin(self):
      cf = mc.GetApp().GetLocalConfig()
      if not self.username or not self.password:
         self.isLoggedIn = False
      else:
         data = {'username': quote(self.username), 'password': quote(self.password)}
         auth = bt.login('https://gamecenter.nhl.com/nhlgc/secure/login', data)
         log('logging in')
         mc.ShowDialogWait()
         auth.commit()
         auth_request = auth.get_result()
         auth_request = auth_request.replace('<![CDATA[', '')
         auth_request = auth_request.replace(']]>', '')
         auth_cookies = auth.get_merged_cookies()
         self.cookies = auth_cookies

         if auth_request and '<code>' in auth_request:
            auth_code = re.compile('<code>(.*?)<').findall(auth_request)[0]
            if auth_code == 'loginsuccess' and auth_cookies:
               self.clearStoredCreds()
               if not '<hasSubscription>' in auth_request:
                  self.isLoggedIn = False
                  self.clearStoredCreds()
                  self.refresh = True
               else:
                  self.isLoggedIn = True
                  if '<vaultSubscription>' in auth_request:
                     self.vaultOnly = re.compile('<vaultSubscription>(.*?)<').findall(auth_request)[0]
                  if '<hasSubscription>' in auth_request:
                     self.hasSubscription = re.compile('<hasSubscription>(.*?)<').findall(auth_request)[0]
                  if '<givenName>' in auth_request:
                     self.firstName = re.compile('<givenName>(.*?)<').findall(auth_request)[0]
                  cf.SetValue('auth_user', self.username)
                  cf.SetValue('auth_pwd', self.password)
                  cf.SetValue('auth_name', self.firstName)
            else:
               self.isLoggedIn = False
               self.clearStoredCreds()
         mc.HideDialogWait()

   def dialogLogin(self):
      window = mc.GetWindow(14004)
      user = window.GetEdit(122).GetText()
      pwd = window.GetEdit(123).GetText()
      if not user or not pwd:
         mc.ShowDialogNotification('You must enter a username and password to login.','nhl_logo.png')
      else:
         window.GetEdit(122).SetText('')
         window.GetEdit(123).SetText('')
         mc.GetActiveWindow().PopState()
         xbmc.executebuiltin('Dialog.Close(14004)')
         self.username = user
         self.password = pwd
         self.commitLogin()
         if self.refresh and not self.isLoggedIn:
            dialog.show('NHL GAMECENTER', 'Your login is valid however your subscription is out of date or expired.[CR][CR]Please log into your account at [COLOR ff13c3d7]http://gamecenter.nhl.com/nhlgc[/COLOR] to update your subscription.')
         if not self.isLoggedIn:
            mc.ShowDialogNotification('Login Invalid. Please try again.', 'nhl_logo.png')
         else:
            mc.ShowDialogNotification('Welcome to NHL GameCenter!', 'nhl_logo.png')

class gameBrowser:
   """
   Manages the NHL archive/condensed game dates by season. All data is stored
   within 'virtual calendars' with the ability to navigate through each day of
   each season available and update the accompanying UI elements.
   """

   cal = calendar
   archived = []
   condensed = []
   active_cal = {}
   type = 'archived'
   current = time.gmtime()
   config = mc.GetApp().GetLocalConfig()

   def __init__(self):
      self.type = 'archived'
      self.cal.setfirstweekday(self.cal.SUNDAY)


   def loadAvailableGameDates(self, user, passwd):
      """
      Loads up the archived and condensed calendars with the available game
      info. This method requires the user to be authenticated so it cannot
      be called at launch if the user is not authed.
      """

      mc.ShowDialogWait()
      self.archived = self.parseAvailableDates('http://dir.boxee.tv/apps/nhl/nhl.php?availgames=archived&user=%s&pass=%s' % (user, passwd))
      self.condensed = self.parseAvailableDates('http://dir.boxee.tv/apps/nhl/nhl.php?availgames=condensed&user=%s&pass=%s' % (user, passwd))
      self.loadCalendar()
      mc.HideDialogWait()


   def buildGuiCalendar(self):
      """
      Using the active season/calendar month, builds a valid list of listitems.
      Full month name and item list will be pushed into the UI.
      """
      l = mc.ListItems()
      log('building calendar view')
      for w in self.active_cal['matrix']:
         for day in w:
            i = mc.ListItem()
            if day > 0: i.SetLabel(str(day))
            else: i.SetLabel('-')
            if day == self.active_cal['day']: i.SetProperty('active', 'true')
            if day not in self.active_cal['available']: i.SetProperty('nogames', 'true')
            l.append(i)

      log('setting calendar items to gui')
      mc.GetWindow(14001).GetButton(1003).SetLabel(self.active_cal['calendar_title'])
      mc.GetWindow(14001).GetList(1004).SetItems(l)


   def changeDay(self, day):
      """
      Sets the active calendar day
      """

      self.active_cal['day'] = int(day)
      self.config.SetValue('GameFilterByDate', self.getRequestDate())

      try:
         self.buildGuiCalendar()
      except:
         pass


   def monthPrevious(self):
      """
      Moves the the active calendar to the previous month. Returns false if the
      active calendar is already in the first month of the active season
      """

      active = self.active_cal
      if active['year'] == active['start'][0] and active['month'] == active['start'][1]: return False

      if active['month'] == 1:
         active['year'] -= 1
         active['month'] = 12
      else: active['month'] -= 1

      active['available'] = []
      for g in active['games']:
         if g[0] == active['year'] and g[1] == active['month']:
            active['available'].append(g[2])

      active['day'] = self.active_cal['available'][-1]
      active['calendar_title'] = self.cal.month_name[active['month']].upper()
      active['matrix'] = self.cal.monthcalendar(active['year'], active['month'])
      return True


   def monthNext(self):
      """
      Moves the the active calendar to the next month. Returns false if the
      active calendar is already in the last month of the active season
      """

      active = self.active_cal
      if active['year'] == active['end'][0] and active['month'] == active['end'][1]: return False

      if active['month'] == 12:
         active['year'] += 1
         active['month'] = 1
      else: active['month'] += 1

      active['available'] = []
      for g in active['games']:
         if g[0] == active['year'] and g[1] == active['month']:
            active['available'].append(g[2])

      active['day'] = self.active_cal['available'][-1]
      active['calendar_title'] = self.cal.month_name[active['month']].upper()
      active['matrix'] = self.cal.monthcalendar(active['year'], active['month'])
      return True


   def parseAvailableDates(self, url):
      """
      Retreives the available games xml from neulion. Each season will be
      pushed into its appropriate game type.
      """

      format = "%s-%s Season"
      content = mc.Http().Get(url).strip()
      results = parseString(content).getElementsByTagName('result')[0]
      season = results.getElementsByTagName('season')
      seasons = []
      for sn in season:
         year = str(sn.getAttribute('id'))
         year2 = str(int(year)+1)[2:]
         if len(sn.getElementsByTagName('g')) == 0:
            continue
         start = sn.getElementsByTagName('g')[0].firstChild.data.split('-')[:2]
         end = sn.getElementsByTagName('g')[-1].firstChild.data.split('-')[:2]
         data = [year, {'display': format % (year, year2), 'season_year': str(year)}]
         games = []
         for game in sn.getElementsByTagName('g'):
            date = game.firstChild.data.split(' ')[0]
            games.append(time.strptime(date, "%Y-%m-%d"))
         data[1]['games'] = games
         seasons.append(data)
      return seasons


   def loadCalendar(self, year=False):
      """
      Loads the defualt calendar (most recent year) for the active type
      property. If year is set, the calendar matching that season year will be
      loaded.
      """

      year_available = False
      if self.type == 'condensed':
         calendar = self.condensed
         self.active_cal['type'] = 'condensed'
      else:
         calendar = self.archived
         self.active_cal['type'] = 'archived'

      if not year:
         calendar = calendar[-1][1]
         year_available = True
      else:
         for y in calendar:
            if int(y[0]) == year:
               calendar = y[1]
               year_available = True

      if not year_available:
         return False

      day = calendar['games'][-1]
      self.active_cal['year'] = day[0]
      self.active_cal['month'] = day[1]
      self.active_cal['day'] = day[2]
      self.active_cal['start'] = calendar['games'][0]
      self.active_cal['end'] = calendar['games'][-1]
      self.active_cal['calendar_title'] = self.cal.month_name[day[1]].upper()
      self.active_cal['matrix'] = self.cal.monthcalendar(day[0], day[1])
      self.active_cal['games'] = calendar['games']
      self.active_cal['season_year'] = calendar['season_year']
      self.active_cal['display'] = calendar['display']
      self.active_cal['available'] = []
      for g in self.active_cal['games']:
         if g[0] == day[0] and g[1] == day[1]:
            self.active_cal['available'].append(g[2])

      self.config.SetValue('games_season', self.active_cal['display'])
      self.config.SetValue('GameFilterByDate', self.getRequestDate())
      self.config.SetValue('GameFilterBySeason', self.active_cal['season_year'])

      try:
         self.buildGuiCalendar()
         mc.GetActiveWindow().GetButton(1002).SetLabel(self.active_cal['display'])
      except:
         pass

      return True


   def getRequestDate(self):
      """
      Returns a string of a valid date request parameter for querying nuelion
      servers for game content
      """

      c = self.active_cal
      return "%02i/%02i/%i" % (c['month'], c['day'], c['year'])


   def getAvailableSeasons(self, type=False):
      """
      Returns a list of all available season years and display titles for the
      currently active game type.
      """

      result = []
      lookup = type
      if not type: lookup = self.type
      if lookup == 'condensed': calendar = self.condensed
      else: calendar = self.archived
      for year in calendar:
         result.append( [year[0], year[1]['display']] )
      return result


   def printActiveCal(self):
      """
      Dump the currently active calendar to log in a readable format
      """

      c = self.active_cal
      print 'type: '+str(c['type'])
      print 'year: '+str(c['year'])
      print 'month: '+str(c['month'])+' ('+c['calendar_title']+')'
      print 'day: '+str(c['day'])
      print 'days available: ' + str(len(c['games']))
      print 'season: ' + str(c['season_year']) + ' ('+c['display']+')'
      print 'start: '+str(c['start'])
      print 'end: '+str(c['end'])
      print 'days available (month): ' + str(c['available'])
      print 'calendar: '+str(c['matrix'])


   def updateBrowserView(self):
      """
      Update the required UI elements for the user. All calendar changes should
      be made before hitting this function as to update the UI a little as
      possible.
      """
      window = mc.GetWindow(14001)
      config.SetValue('GameFilterBySeason', str(self.active_cal['season_year']))
      config.SetValue('games_season', self.active_cal['display'])
      config.SetValue('GameFilterByDate', self.getRequestDate())
      window.GetButton(1002).SetLabel(self.active_cal['display'])
      window.GetButton(1003).SetLabel(self.active_cal['calendar_title'])
      self.buildGuiCalendar()

   def setDefaultBrowserView(self):
      """"
      Sets the default (logged out) browser view to highlights only
      """

      self.config.Reset('221')
      self.config.Reset('222')
      self.config.Reset('224')
      self.config.Reset('225')
      self.config.SetValue('223', 'true')
      self.config.SetValue('GameFilterByTeam', '')
      self.config.SetValue('GameFilterByType', 'highlight')


mc.ShowDialogWait()

#init global data
user = userAccount()
browser = gameBrowser()
config = mc.GetApp().GetLocalConfig()
dialog = nhlDialog()

try:
   if user.isLoggedIn:
      browser.loadAvailableGameDates(user.username, user.password)
except: pass

mc.HideDialogWait()
