# vim: ts=4 :
import getpass
import json
from restkit import Resource, BasicAuth, Connection, request
from socketpool import ConnectionPool
from urllib import quote

# Color sequence from ColorBrewer http://colorbrewer2.org/
# Diverging 6 color BrBG scheme

DEFAULT_LABELS = (
                  ('0 - Backlog', 'CCCCCC'),
                  ('1 - Ready', 'CCCCCC'),
                  ('2 - Working', 'CCCCCC'),
                  ('3 - Done', 'CCCCCC'),
                  ('2014planning', 'd4c5f9'),
                  ('Needs Review', '009800'),
                  ('Security', 'e11d21'),
                  ('Upstream', 'f7c6c7'),
                  ('Usability', 'eb6420'),
                  ('bug', 'fc2929'),
                  ('enhancement', '84b6eb'),
                  ('Internationalization', 'fbca04'),
                  ('Research', 'bfe5bf'),
                  ('duplicate', 'CCCCCC'),
                  ('invalid', 'e6e6e6'),
                  ('question', 'cc317c'),
                  ('wontfix', 'ffffff'),
		 )

pool = ConnectionPool(factory=Connection)
serverurl="https://api.github.com"

msg = "This script will create the default labels %s in your specified " \
      "repository if they do not yet exist." % (', '.join(lab[0] for lab in DEFAULT_LABELS))
print msg

repo = raw_input("Repository: ")
usr = raw_input("Username: ")
pwd = getpass.getpass("Password: ")
# Add your username and password here, or prompt for them
auth=BasicAuth(usr, pwd)

# Use your basic auth to request a token
# This is just an example from http://developer.github.com/v3/
authreqdata = { "scopes": [ "repo" ], "note": "admin script" }
resource = Resource('https://api.github.com/authorizations',
    pool=pool, filters=[auth])
response = resource.post(headers={ "Content-Type": "application/json" },
    payload=json.dumps(authreqdata))
token = json.loads(response.body_string())['token']


#Once you have a token, you can pass that in the Authorization header
#You can store this in a cache and throw away the user/password
#This is just an example query.  See http://developer.github.com/v3/
#for more about the url structure

resource = Resource('https://api.github.com/user/repos', pool=pool)
resource = Resource('https://api.github.com/orgs/opentechinstitute/repos', pool=pool)

resource = Resource('https://api.github.com/repos/%s/labels' % repo, pool=pool)
headers = {'Content-Type' : 'application/json' }
headers['Authorization'] = 'token %s' % token
response = resource.get(headers = headers)
labels = json.loads(response.body_string())
label_names = [n['name'] for n in labels]

print "label_names: "
for l in label_names:
	print l


for dl,color in DEFAULT_LABELS:
    print "dl is " + dl
     
    payload = {"name": dl, "color": color}
    headers = {'Content-Type' : 'application/json' }
    headers['Authorization'] = 'token %s' % token

    print "Payload is " 
    for p in payload:
	print p

    if dl not in label_names:
        print "Adding %s" % dl
        resource = Resource('https://api.github.com/repos/%s/labels' % repo, pool=pool)
        response = resource.post(payload=json.dumps(payload), headers=headers)
    else:
        print "Updating colors for %s" % dl
        plan = 'https://api.github.com/repos/%s/labels/%s' % (repo, quote(dl))
	print "The plan is " + plan
        resource = Resource('https://api.github.com/repos/%s/labels/%s' % (repo, quote(dl)), pool=pool)
        response = resource.request('PATCH', payload=json.dumps(payload), headers=headers)
