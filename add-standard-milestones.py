# vim: ts=4 :
import getpass
import json
from restkit import Resource, BasicAuth, Connection, request
from socketpool import ConnectionPool

# Color sequence from ColorBrewer http://colorbrewer2.org/
# Diverging 6 color BrBG scheme

DEFAULT_MILESTONES = (
#			('title', 'open|closed', 'desc', 'YYYY-MM-DDTHH:MM:SSZ'),
			('test-milestone', 'open', 'testing the script', '2014-01-28T00:00:00Z'),
			('no-due-date', 'open', 'testing the script', ''),
		     )

pool = ConnectionPool(factory=Connection)
serverurl="https://api.github.com"

msg = "This script will create the default milestones %s in your specified " \
      "repository if they do not yet exist." % (', '.join(lab[0] for lab in DEFAULT_MILESTONES))
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

resource = Resource('https://api.github.com/repos/%s/milestones' % repo, pool=pool)
headers = {'Content-Type' : 'application/json' }
headers['Authorization'] = 'token %s' % token
response = resource.get(headers = headers)
milestones = json.loads(response.body_string())
milestone_names = [n['title'] for n in milestones]

print "milestone_names: "
for m in milestone_names:
	print m


for dm,state,desc,due in DEFAULT_MILESTONES:
    print "dm is " + dm
     
    payload = {"title": dm, "state": state, "description": desc, "due_on": due}
    headers = {'Content-Type' : 'application/x-www-form-urlencoded' }
    headers['Authorization'] = 'token %s' % token


    if dm not in milestone_names:
        print "Adding %s" % dm
        resource = Resource('https://api.github.com/repos/%s/labels' % repo, pool=pool)
        response = resource.post(payload=json.dumps(payload), headers=headers)
    else:
        print "Updating colors for %s" % dm
        plan = 'https://api.github.com/repos/%s/labels/%s' % (repo, dm)
	print "The plan is " + plan
        resource = Resource('https://api.github.com/repos/%s/labels/%s' % (repo, dm), pool=pool)
        response = resource.request('PATCH', payload=json.dumps(payload), headers=headers)
