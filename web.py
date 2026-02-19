from bottle import route, run, static_file, request, template, TEMPLATE_PATH, response, redirect
from datetime import datetime
import json
import socket
import re   
import os 
import sys

base_path = os.getenv('APPDATA') 
storage = os.path.join(base_path, "Private_Chat_App")
if not os.path.exists(storage):
    os.makedirs(storage)  

        
if not os.path.exists(os.path.join(storage, 'resources')):
    os.makedirs(os.path.join(storage, 'resources'))
    os.makedirs(os.path.join(storage, 'uploads'))
    with open(os.path.join(storage, 'resources', 'acc.db'), 'x') as f:
        pass

#User Credentials
secret_key = 'jb_web_private_key'
TEMPLATE_PATH.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), './web/'))


uids = []
users = []
mnums = []
uids_users = {}
seed = 1000
shared_dict={}

def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))

@route('/')
def index():
    user_code = request.get_cookie('ugr_cd', secret=secret_key)
    if not user_code or not user_code in uids:
        return template('./account/login.html', error_message=None)
    return template('index.html', user_name=users[uids.index(user_code)])
@route('/sign-up')    
def sign_up():
    return template('./account/sign_up.html', error_message=None)
@route('/login')
def sign_up():
    return template('./account/login.html', error_message=None)

@route('/<file:path>')
def resources(file):
    return static_file(file, root=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'web/'))

@route('/login', method='POST')
def login():
    if request.forms['mobile'] not in mnums:
        return template('./account/login.html', error_message='Invalid username or password')
    id = mnums.index(request.forms['mobile'])
    if request.forms['username'] == users[id]:
        response.set_cookie('ugr_cd', uids[id], secret=secret_key, maxage=2592000)
        response.set_cookie('usr_id', uids[id], maxage=2592000) # 30days
        response.set_cookie('usr_name', users[id], maxage=2592000)
    return redirect("/")

@route('/sign-up', method='POST')
def create_account():
    if request.forms['mobile'] in mnums:
        return template('./account/sign_up.html', error_message='The mobile number is already registered. Please try other one')
    if not has_numbers(request.forms['mobile']):
        return template('./account/sign_up.html', error_message='Only numbers can be accepted. Please try other one')
    if bool(re.search('[;,?/<>%^*()-+]', request.forms['username'])):
        return template('./account/sign_up.html', error_message='User name can\'t contain ;,?/<>%^*()-+. Please try other one')
            
    global seed
    seed+=1
    users.append(str(request.forms['username']).strip())
    mnums.append(request.forms['mobile'])
    uids.append(str(seed))
    uids_users[str(seed)] = str(request.forms['username']).strip()
    response.set_cookie('ugr_cd', str(seed), secret=secret_key, maxage=2592000)
    response.set_cookie('usr_id', str(seed), maxage=2592000)
    response.set_cookie('usr_name', request.forms['username'], maxage=2592000)
    with open(os.path.join(storage,'resources', 'acc.db'), 'a') as f:
        f.write(f"{request.forms['username']}={request.forms['mobile']}={seed};")
    shared_dict['uids'] = uids
    shared_dict['uids_users'] = uids_users
    return redirect('/')
        
        
@route('/file_upload', method='POST')
def file_upload():
    upload = request.files
    files = []
    for key, value in dict(upload).items():
        value.filename = f"{str(datetime.now()).replace(':', '-')}_{value.filename}"
        files.append(value.filename)
        value.save(os.path.join(storage,'uploads/')) # appends upload.filename automatically
        # name, ext = os.path.splitext(value.filename)

        # save_path = get_save_path_for_category(category)
    return json.dumps(files)

@route('/get', method='GET')
def get_file():
    return static_file(request.query.file, root=os.path.join(storage,'uploads/'))

## seting user acct info up
with open(os.path.join(storage,'resources', 'acc.db'), 'r') as f:
    data = f.read()
    if data:
        accts = [x.split('=') for x in data.split(';')[:-1]]
        for user, pas, seed in accts:
            users.append(user)
            mnums.append(pas)
            uids.append(seed)
            uids_users[seed] = user
            seed = int(seed)
