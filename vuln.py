from flask import Flask, jsonify, request, render_template, make_response # For Front/Back End
import sqlite3 # for SQL-Injection
import os # for OS-Injection
import time # for time based Python
import base64 # to encode all traffic in b64
import requests # for ssrf



def sanitize(ui):
	ui = str(ui)
	#if(len(ui) > 40): print("to long"); return True
	# Only really Important are {} and ;
	# the rest is to prevent exploitation
	badstring = "!@#$%^&*+={|<>};:'"
	badstring += '"'
	for char in ui:
		if char in badstring:
			print(f"bad character {char}")
			return True
	return False


# Setup

verbose = False
log = True

conn = sqlite3.connect('vulnerable-database.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS users')
c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT, password TEXT, description TEXT, website TEXT)')
c.execute('INSERT INTO users (username, password, description, website) VALUES ("test", "test", "test", "http://test.test.test")')

conn.commit()
conn.close()


app = Flask('vuln')
def getDB():
    return sqlite3.connect('vulnerable-database.db')

def closeDB(conn):
    conn.commit()
    conn.close()

arr = ['xss-reflected', 'xss-stored', 'sql-injection', 'os-injection', 'python-injection', 'ssti', 'time-based']

default = '''
<html>
<head>
<style>
    body {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }

    ul {
      list-style-type: none;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      padding: 0;
    }

    li {
      margin-right: 20px; /* Adjust as needed */
    }

    div {
      margin: 0 auto;
      width: 70vw; /* Adjust as needed */
      text-align: center;
    }
  </style>
  <title>Vulnerable Web Application</title>
</head>
<body>
<nav>
  <ul>
    <button onclick="window.location.href = '/f'">Actual</button>
    <li><a href='/xss-reflected'>xss-reflected</a></li>
    <li><a href='/xss-stored'>xss-stored</a></li>
    <li><a href='/sql-injection'>sql-injection</a></li>
    <li><a href='/os-injection'>os-injection</a></li>
    <li><a href='/python-injection'>python-injection</a></li>
    <li><a href='/ssti'>Server-side template injection</a></li>
    <li><a href='/path_traversal'>path-traversal</a></li>
    <li><a href='/ssrf'>Server-Side request forgery</a></li>
  </ul>
</nav>
<section id='section'>
<div>
<h2> Vulnerable Web-Application </h2>
</div>
</section>
<form onsubmit=send(event)>
<input id='payload' placeholder='payload'>
</form>
<h2> Output </h2>
<h2> tmp </h2>
<script>
let div = document.createElement('div')
let h1 = document.createElement('h1')
let name = window.location.href.split('/')[3]
if(name.includes('?')) {
    h1.innerHTML = name.split('?')[0]
} else {
    h1.innerHTML = name
}

div.appendChild(h1)
document.getElementById('section').appendChild(div)
function send(event) {
    event.preventDefault();
    let payload = document.getElementById('payload').value;
    if(window.location.href.includes('?')) {
        let str = window.location.href.split('?')[0] + `?payload=${btoa(payload)}`
        window.location.href = str
    } else {window.location.href = window.location.href+`?payload=${btoa(payload)}`}
    
}
</script>
</body>
</html>

'''
default_f = '''
<html>
<head>
<style>
    body {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }

    ul {
      list-style-type: none;
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      padding: 0;
    }

    li {
      margin-right: 20px; /* Adjust as needed */
    }

    div {
      margin: 0 auto;
      width: 70vw; /* Adjust as needed */
      text-align: center;
    }
    button {
        background-color: blue;
        color: white;
        border: 1px solid;
    }
  </style>
  <title>Vulnerable Web Application</title>
</head>
<body>
<nav>
  <ul>
  <button onclick="window.location.href = '/'">Obvious</button>
    <li><a href='/xss-reflected'>xss-reflected</a></li>
    <li><a href='/xss-stored'>xss-stored</a></li>
    <li><a href='/sql-injection'>sql-injection</a></li>
    <li><a href='/os-injection'>os-injection</a></li>
    <li><a href='/python-injection'>python-injection</a></li>
    <li><a href='/ssti'>ssti</a></li>
    <li><a href='/path_traversal'>path-traversal</a></li>
  </ul>
</nav>
<section id='section'>
<div>
<h2> Vulnerable Web-Application </h2>
</div>
</section>
<h3>Register for the Application</h3>
<form onSubmit="send(event)">
<div style="margin-top:3vh"><label>Username:        </label>   <input id=user placeholder='Username'></div> <br>
<div style="margin-top:3vh"><label>Password:        </label>   <input id=pass placeholder='Password'></div> <br>
<div style="margin-top:3vh"><label>Website :        </label>   <input id=webpage placeholder='Website'> </div> <br>
<div style="margin-top:3vh"><label>Description :    </label>   <input id=desc placeholder='Website'> </div> <br>
<button type=submit>submit</button>
</form>
<h2> Output </h2>
<h2> tmp </h2>
<script>
let div = document.createElement('div')
let h1 = document.createElement('h1')
let name = window.location.href.split('/')[3]
if(name.includes('?')) {
    h1.innerHTML = name.split('?')[0]
} else {
    h1.innerHTML = name
}

div.appendChild(h1)
document.getElementById('section').appendChild(div)
function send(event) {
    event.preventDefault();
    if(window.location.href.includes('?')) {
        let str = window.location.href.split('?')[0] + `?user=${btoa(document.getElementById('user').value)}&pass=${btoa(document.getElementById('pass').value)}&website=${btoa(document.getElementById('webpage').value)}&desc=${btoa(document.getElementById('desc').value)}`
        alert(str)
        window.location.href = str
    } else {window.location.href = window.location.href+`?user=${btoa(document.getElementById('user').value)}&pass=${btoa(document.getElementById('pass').value)}&website=${btoa(document.getElementById('webpage').value)}&desc=${btoa(document.getElementById('desc').value)}`}
    
}
</script>
</body>
</html>

'''

with open('default.html','w') as d:
    d.write(default)

with open('default-f.html','w') as d:
    d.write(default_f)


xss_stored_value = ''

def log_data(d):
    with open('log.txt','a') as log_file:
        log_file.write(d)


@app.route('/')
def index():
    return default.replace('tmp', 'Hello there, this is a little demonstration of a vulnerable Application, to showcase some vulnerabilities.')

@app.route('/f')
def indexf():
    return default.replace("'>", "-f'>")

@app.route('/os-injection')
def os_injection():
    try:
        #print(base64.b64decode(request.args.get('payload')).decode('utf-8'))
        payload = base64.b64decode(request.args.get('payload')).decode('utf-8')
        if(log): 
            l = f'Using payload: {payload} on /os-injection'
            log_data(l)
            print(l)
        print(payload)
        os.system(f'{payload} > .output.txt')
        output = ''
        with open('.output.txt', 'r') as f:
            for line in f:
                output += line.replace('\r', '') # .replace('\n','')
        return default.replace('tmp', output)
    except:
        return default.replace('tmp', 'OS-Injection (or OS-Command-Injection) is a vulnerability that means that an malicious user can execute Operating System commands, this means they have control over the server, usually not root yet. From this point on they can try to escalate priviledges and exploit other servers.')

@app.route('/os-injection-f')
def os_injectionf():
    try:
        #print(base64.b64decode(request.args.get('payload')).decode('utf-8'))
        print('getting the values from the form')
        try:
            user, password, webpage, desc = base64.b64decode(request.args.get('user')).decode('utf-8'), base64.b64decode(request.args.get('pass')).decode('utf-8'), base64.b64decode(request.args.get('website')).decode('utf-8'), base64.b64decode(request.args.get('desc')).decode('utf-8')
            if(user == None or password == None or webpage == None or desc == None):
                return default_f.replace('tmp', 'Invalid data provided')
            if(user == '' or password == '' or webpage == '' or desc == ''):
                return default_f.replace('tmp', 'Invalid data provided')
        except:
            print('not all values were present')
            print(password)
        payload = webpage
        print(user, password, webpage, desc)
        conn = sqlite3.connect('vulnerable-database.db')
        try:
            if not (sanitize(user) and sanitize(password) and sanitize(desc)):
                print('values clean')
                cursor = conn.cursor()
                print(f'INSERT INTO users (username, password, description) VALUES ("{user}", "{password}","{desc}")')
                cursor.execute(f'INSERT INTO users (username, password, description) VALUES ("{user}", "{password}","{desc}")')
                conn.commit()
                conn.close()
        except Exception as e:
            print(e)
            conn.close()
            
        if(log): 
            l = f'Using payload: {payload} on /os-injection-f'
            log_data(l)
            print(l)
        os.system(f'ping -n 1 {payload} > .output.txt')
        output = os.popen(f'ping -n 1 {payload}').read()
        print(output)
        html = default_f.replace('tmp', f'<script>localStorage.setItem("key", "{user + ";" + password}");</script>tmp').replace('tmp', output)
        resp = make_response(html)
        resp.set_cookie('key', user + ";" + password)
        return resp
    except:
        return default_f.replace('SITE', 'os-injection-f')
    
@app.route('/profile')
def profile():
    try:
        username, password = request.cookies.get('key').split(';',1)
        print(username, password)
        if(username == None or username == '' or password == None or password == ''):
            print('b')
            int('B')
    except:
        try:
            username, password = request.args.get('key').split(';', 1)
        except:
            return default_f.replace('tmp', 'something went wrong, please try again')
            
    try:
        if not (sanitize(username) or sanitize(password)):
            print(f'select * from users where username = "{username}" and password = "{password}"')
            data = execute_sql(f'select * from users where username = "{username}" and password = "{password}"')
            data = data[0]
            print(data[0])
            username, password, description = data[1],data[2],data[3]
            data = str(data)
            print(data)
            return f'<html><body><h2>Hello {username}<h2><p>{description}</p></body></html>'
        
    except:
        return default_f
    return default_f


@app.route('/xss-reflected')
def xss_reflected():
    try:
        payload = base64.b64decode(request.args.get('payload')).decode('utf-8')
        if(log): 
            l = f'Using payload: {payload} on /xss-reflected'
            log_data(l)
            print(l)
        return default.replace('tmp', payload)
    except:
        return default.replace('tmp', 'XSS is a vulnerability which allows a malicious user to change a website, which is mosten used to hijack sessions from users by extracting their cookies. Reflected means, that a parameter in the url or a specific header is causing this issue.')

@app.route('/xss-stored')
def xss_stored():
    global xss_stored_value
    try:
        payload = base64.b64decode(request.args.get('payload')).decode('utf-8')
        xss_stored_value = payload
        if(log): 
            l = f'Using payload: {payload} on /xss-stored'
            log_data(l)
            print(l)
        return default.replace('tmp', '<a href="/xss-stored-trigger"> trigger <a/>')
    except:
        return default.replace('tmp', 'Stored-XSS is a vulnerability which allows a malicious user to change a website, which is mosten used to hijack sessions from users by extracting their cookies. Stored means, that the change is permanent and every visitor is a victim')

@app.route('/xss-stored-trigger')
def xss_stored_trigger():
    return default.replace('tmp', xss_stored_value).replace("<input id='payload' placeholder='payload'>", "<a href='/xss-stored'>back to stored</a>")

@app.route('/ssti')
def ssti():
    try:
        payload = base64.b64decode(request.args.get('payload')).decode('utf-8')
        if(log): 
            l = f'Using payload: {payload} on /ssti'
            log_data(l)
            print(l)
        ssti = f'payload: {payload}' + payload
        try:
            ssti = render_template('payload' + payload)
        except Exception as e:
            print(e)
        return default.replace('tmp', ssti)
    except:
        return default.replace('tmp', 'ServerSide Template Injection is a vulnerability that a malicious user can send requests from the server, which can lead to pivoting or information disclosure, if it doesn\'t reveal information its less bad, but still maybe a vulnerability')

        s = ''
@app.route('/python-injection')
def python_injection():
    try:
        payload = base64.b64decode(request.args.get('payload')).decode('utf-8')
        if(log): 
            l = f'Using payload: {payload} on /python-injection'
            log_data(l)
            print(l)
        # execute via eval for simply execute the payload (Blind)
        print(f'Payload: {payload} on Python-Injection')
        try:
            s = eval(payload)
        except:
            if(verbose): print(f'Error: s = eval(payload)')
        # execute python3 -c 'payload' > file to get the output
        try:
            print(f"python3 -c '{payload}' > .output.txt")
            os.system(f"python3 -c '{payload}' > .output.txt")
            output = ''
            with open('.output.txt', 'r') as out:
                for line in out:
                    output += line   
            # Not beautiful solution, but works on windows and linux
            input()
            os.system('rm .output.txt')
            os.system('del .output.txt')
        except:
            if(verbose): print(f"Error: os.system(f\"python3 -c '{payload}' > .output.txt\")")
        print(output)
        return default.replace('Output', 'Output (You can\'t use singlequotes and there may be some issues)').replace('tmp', output)
    except:
        return default.replace('Output', 'Output (You can\'t use singlequotes)').replace('tmp', '(Python-)Code Injection allows an malicious user to run (Python-)Code on a vulnerable server, which oftentimes leads to Remote Code Execution (RCE) and full compromise.')




def execute_sql(query):
    conn = getDB()
    c = conn.cursor()
    c.execute(query)
    data = ''
    try:
        data = c.fetchall()
    except:
        conn.commit()
    conn.close()
    if(data != ''): return data
    else: return None



@app.route('/sql-injection', methods=["GET"])
def sqli():
    return_value = ''
    try:
        payload = base64.b64decode(request.args.get('payload')).decode('utf-8')
        if(log): 
            l = f'Using payload: {payload} on /sql-injection'
            log_data(l)
            print(l)
        if(payload == None):
            return default
    except:
            return default.replace('tmp', 'SQL-Injection is an vulnerability where a malicious user can exploit a SQL-Query by submitting an specific Value for example as username. The issue is that its possible to break out of the query')
    try:
        try:
            print(f"Query: SELECT * FROM users WHERE id = '{payload}'")
            data = execute_sql(f"SELECT * FROM users WHERE id = '{payload}'")
            data = str(data)
            print(data, type(data))
        except Exception as e:
            data = f'Error: {e}'
        try:
            # username', 'passwort') OR 1=1 -- 
            print(f"Query: INSERT INTO users (username, password, biography) VALUES ('{payload}', 'Injection', 'new user')")
            tmp = execute_sql(f"INSERT INTO users (username, password, biography) VALUES ('{payload}','Injection', 'new user')")
            if(tmp == []):
                conn.commit()
                tmp = execute_sql('SELECT * FROM users order by id desc')
                data += str(tmp)
                print(data, type(data))
            else:
                print('there was some weird stuff going on in the query')

        except Exception as e:
            data += f'Error: {e}'
        return default.replace('tmp', 'data:' + str(data)), 200
        queries = ['SELECT * FROM users WHERE username = "payload"', 'INSERT INTO users (username) VALUES ("payload")']
        for query in queries:
            query = query.replace('payload', payload)
            data = execute_sql(query)
            if(data != None):
                print(data)
        return default.replace('tmp', f'results: {data}')
    except:
        return default.replace('tmp', 'Test'), 500
    


@app.route('/path_traversal')
def path_traversal():
    try:
        payload = base64.b64decode(request.args.get('payload')).decode('utf-8')
        if(log): 
            l = f'Using payload: {payload} on /path_traversal'
            log_data(l)
            print(l)
        content = ''
        with open(payload, 'r') as file:
            for line in file:
                content += line
        return default.replace('tmp', content)
    except:
        return default.replace('tmp', 'Path-traversal, sometimes also called LFI (Local File Inclusion) is an vulnerability that allows a malicious user to extract files from the target system')
    
@app.route('/ssrf')
def ssrf():
    try:
        payload = base64.b64decode(request.args.get('payload')).decode('utf-8')
        if(log): 
            l = f'Using payload: {payload} on /ssrf'
            log_data(l)
            print(l)
        resp = requests.get(payload)
        return default.replace('tmp', resp.content)
    except:
        return default.replace('tmp', 'SSRF, or ServerSide Request Forgery is an vulnerability that allows a malicious user to send (for example) HTTP-Request from the Server, therefore perhaps gaining access to content that shouldn\'t be available')    

    
# run the app
app.run('0.0.0.0', 5000, debug=True)
