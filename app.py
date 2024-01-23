from flask import Flask, request
import os
import sqlite3

conn = sqlite3.connect('vulnerable_database.db')


conn.cursor().execute('drop table if exists users')
conn.cursor().execute('create table users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
conn.cursor().execute('insert into users (username,password) values ("test", "test")')

conn.commit()
conn.close()


app = Flask('app')

default_response = '''
<html>
<body>
<nav>
<a href='/os' >os</a>
<a href='/xss-reflected' >xss-reflected</a>
<a href='/xss-stored' >xss-stored</a>
<a href='/ssti' >ssti</a>
</nav>
<h2>Vulnerable Web-Application</h2>
<h2>tmp</h2>
<form onsubmit='send(event)'>
<input id='payload' placeholder='payload'>
</form>
<script>
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

stored_xss = ''


@app.route('/')
def index():
    print('t')
    return '''
        <html>
            <head>
            <style>
            ul {
                list-style-type: none;
                display: flex;
                flex-wrap: wrap;
            }
            li {
                margin-right: 3vw
            }
            </style>
            </head>
            
            <body>
            
            <nav>
            <ul>
            <li><a href='/os' >os</a></li>
            <li><a href='/sql_injection' >sql_injection</a></li>
            <li><a href='/xss_reflected' >xss_reflected</a></li>
            <li><a href='/xss_stored' >xss_stored</a></li>
            <li><a href='/ssti' >ssti</a></li>
            </ul>
            </nav>
            <h2>Welcome to a little OWASP-TOP-10 Demo</h2>
            <h2>To execute a vulnerability, go to the site and enter '?payload=<your_payload_here>' to the url</h2>
            </body>    
        </html>
        '''
    
@app.route('/sql-injection', methods=["GET"])
def sqli():
    try:
        payload = request.args.get('payload')
    except:
            return default_response
    queries = ['INSERT INTO users (username, password) VALUES ("test", {payload})', 'INSERT INTO users (username, password) VALUES ("test", "{payload}")', "INSERT INTO users (username, password) VALUES ('test', {payload})",  "INSERT INTO users (username, password) VALUES ('test', '{payload}')"]
    errors = []
    for query in queries:
        try:
            conn = sqlite3.connect('vulnerable_database.db')
            conn.cursor.execute(query)
            conn.commit()
            conn.close()
        except Exception as e:
            errors.append(str(e))
            conn.rollback()
            conn.close()
        # If theres a ; in the query, maybe a vulnerable app would
        # execute it as x queries, sqlite3 prevents that, therefore
        # i split it to x queries and execute them after each other
        if(query.__contains__(';')):
            sub_queries = query.split(';')
            for q in sub_queries:
                try:
                    conn = sqlite3.connect('vulnerable_database.db')
                    conn.cursor.execute(q)
                    conn.commit()
                    conn.close()
                except Exception as e:
                    errors.append(str(e))
                    conn.rollback()
                    conn.close()
    return default_response.replace('tmp', errors)
        


@app.route('/os', methods=['GET'])
def os_command():
    try:
        cmd = str(request.args.get('payload'))
        print(cmd)
        os.system(f'{cmd} > .tmp.txt')
        output = ''
        with open('.tmp.txt', 'r') as f:
            for line in f:
                # format it a bit so its readable
                # output += line.replace('\r','').replace('\n','').replace('\t','').replace(' ','')
                output += line
        return default_response.replace('tmp', f'Command {cmd} executed: <br> output: {output}')
    except:
        return default_response
    
@app.route('/xss_reflected', methods=['GET'])
def xss_reflected():
    print('test')
    try:
        payload = request.args.get('payload')
        return default_response.replace('tmp', payload)
    except:
        return default_response

@app.route('/xss_stored', methods=['GET'])
def xss_stored():
    try:
        global stored_xss
        stored_xss = request.args.get('payload')
        return default_response.replace('tmp', 'The Payload has been stored, accesable on http://127.0.0.1:5000/stored.html')
    except:
        return default_response
    
@app.route('/stored', methods=['GET'])
def stored():
    try:    
        return default_response.replace('tmp', stored_xss)
    except:
        return default_response

@app.route('/ssti', methods=['GET'])
def ssti():
    try:
        return default_response.replace('tmp', str(eval(request.args.get('payload'))))
    except:
        return default_response




app.run('0.0.0.0', 5000, debug=True)
