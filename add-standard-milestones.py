import getpass
import json
from restkit import Resource, BasicAuth, Connection, request
from socketpool import ConnectionPool

DEFAULT_MILESTONES = (
#			('title', 'open|closed', 'desc', 'YYYY-MM-DDTHH:MM:SSZ'),
		     )

pool = ConnectionPool(factory=Connection)
serverurl="https://api.github.com"

msg = "This script will create the default milestones %s in your specified " \
      "repository if they do not yet exist.\nThe script should update existing milestones" \
      "but currently has trouble dealing with spaces in milestone fields (e.g., description)" % (', '.join(lab[0] for lab in DEFAULT_MILESTONES))
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
resource = Resource('https://api.github.com/orgs/lillyoi/repos', pool=pool)

resource = Resource('https://api.github.com/repos/%s/milestones' % repo, pool=pool)
headers = {'Content-Type' : 'application/json' }
headers['Authorization'] = 'token %s' % token
response = resource.get(headers = headers)
milestones = json.loads(response.body_string())
milestone_names = {t['title']: t['number'] for t in milestones}

for dm,state,desc,due in DEFAULT_MILESTONES:
     
    payload = {"title": dm, "state": state, "description": desc, "due_on": due}
    headers = {'Content-Type' : 'application/x-www-form-urlencoded' }
    headers['Authorization'] = 'token %s' % token


    if dm not in milestone_names:
        print "Adding %s" % dm
        resource = Resource('https://api.github.com/repos/%s/milestones' % repo, pool=pool)
        response = resource.post(payload=json.dumps(payload), headers=headers)
    else:
        print "Updating parameters for for %s" % dm
        resource = Resource('https://api.github.com/repos/%s/milestones/%s' % (repo, milestone_names[dm]), pool=pool)
        response = resource.request('PATCH', payload=json.dumps(payload), headers=headers)
