import mc
import nhl
import sys
import cgi
import tracker

args = False
myTracker = tracker.Tracker()

mc.ShowDialogOk('NHL Gamecenter', 'We are currently experiencing technical difficulties that may affect playback quality of NHL games. We are working hard, together with the NHL, to resolve these issues. -Boxee');

if sys.argv[1]:
   args = cgi.parse_qs(sys.argv[1])
   if args['title']:
      myTracker.trackEvent("Feed", "Launch", args['title'][0])
else:
   myTracker.trackView("launch")

if not nhl.config.GetValue('firstLaunch'):
   nhl.config.SetValue('firstLaunch', 'true')
   nhl.config.SetValue('hidescores', 'true')

nhl.config.Reset('GameFilterByTeam')
nhl.browser.setDefaultBrowserView()
nhl.launch(args)
