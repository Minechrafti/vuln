from flask import Flask, jsonify, request
import sqlite3
import os
import time


# Setup


app = Flask('vuln')

conn = sqlite3.connect('vulnerable-datbase.db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS users')
c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, username TEXT, password TEXT)')
c.execute('INSERT INTO users (username, password) VALUES ("test", "test")')

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
</head>
<body>
<nav>
  <ul>
    <li><a href='http://127.0.0.1:5000/xss-reflected'>xss-reflected</a></li>
    <li><a href='/xss-stored'>xss-stored</a></li>
    <li><a href='/sql-injection'>sql-injection</a></li>
    <li><a href='/os-injection'>os-injection</a></li>
    <li><a href='/python-injection'>python-injection</a></li>
    <li><a href='/ssti'>ssti</a></li>
    <li><a href='/time-based'>time-based</a></li>
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
        let str = window.location.href.split('?')[0] + `?payload=${payload}`
        window.location.href = str
    } else {window.location.href = window.location.href+`?payload=${payload}`}
    
}
</script>
</body>
</html>

'''

xss_stored_value = ''


@app.route('/')
def index():
    return default

@app.route('/os-injection')
def os_injection():
    try:
        payload = request.args.get('payload')
        os.system(f'{payload} > .output.txt')
        output = ''
        with open('.output.txt', 'r') as f:
            for line in f:
                output += line.replace('\r', '').replace('\n','')
        return default.replace('tmp', output)
    except:
        return default

@app.route('/xss-reflected')
def xss_reflected():
    try:
        payload = request.args.get('payload')
        print(payload)
        return default.replace('tmp', payload)
    except:
        return default

@app.route('/xss-stored')
def xss_stored():
    global xss_stored_value
    try:
        payload = request.args.get('payload')
        xss_stored_value = payload
        return default.replace('tmp', '<a href="/xss-stored-trigger"> trigger <a/>')
    except:
        return default

@app.route('/xss-stored-trigger')
def xss_stored_trigger():
    return default.replace('tmp', xss_stored_value).replace("<input id='payload' placeholder='payload'>", "<a href='/xss-stored'>back to stored</a>")

@app.route('/ssti')
def ssti():
    try:
        payload = request.args.get('payload')
        ssti = f'payload: {payload}'
        return default.replace('tmp', ssti)
    except:
        return default

@app.route('/python-injection')
def python_injection():
    try:
        payload = request.args.get('payload')
        s = eval(payload)
        return default.replace('tmp', s)
    except:
        return default





@app.route('/sql-injection', methods=["GET"])
def sqli():
    try:
        payload = request.args.get('payload')
        if(payload == None):
            return default
    except:
            return default
    queries = [f'SELECT * FROM users WHERE username={payload}', f'SELECT * FROM users WHERE username="{payload}"', f"SELECT * FROM users WHERE username={payload}",  f"SELECT * FROM users WHERE username='{payload}'"]
    errors = ''
    data = ''
    for query in queries:
        print(query)
        try:
            conn = sqlite3.connect('vulnerable_database.db')
            conn.cursor().execute(query)
            values = conn.cursor().fetchone()
            print(values)
            data += values[0]
            conn.close()
        except Exception as e:
            errors += str(e) + ';'
            conn.close()
        # If theres a ; in the query, maybe a vulnerable app would
        # execute it as x queries, sqlite3 prevents that, therefore
        # i split it to x queries and execute them after each other
        if(query.__contains__(';')):
            sub_queries = query.split(';')
            print(sub_queries)
            for q in sub_queries:
                try:
                    conn = sqlite3.connect('vulnerable_database.db')
                    conn.cursor().execute(q)
                    values = conn.cursor().fetchone()
                    print(values)
                    data += values[0]
                    conn.close()
                except Exception as e:
                    errors += (str(e)) + ';'
                    conn.close()
    return default.replace('tmp', f'results: {data} \n errors: {errors}')
    


@app.route('/timebased')
def timebased():
    cmd = request.args.get('payload')
    if(cmd.__contains__('sleep') and cmd.__contains__('20')):
        time.sleep(20)
    return 'waited 20 sec'

app.run('0.0.0.0', 5000, debug=True)
