from flask import Flask, request
import os

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
            <h2>Welcome to a little OWASP-TOP-10 Demo</h2>
            <h2>To execute a vulnerability, go to the site and enter '?payload=<your_payload_here>' to the url</h2>
            <nav>
            <a href='/os' >os</a>
            <a href='/sql_injection' >sql_injection</a>
            <a href='/xss_reflected' >xss_reflected</a>
            <a href='/xss_stored' >xss_stored</a>
            <a href='/ssti' >ssti</a>
            </nav>    
        </html>
        '''
    
@app.route('/sql-injection', methods=["GET"])
def sqli():
    try:
        injection = request.args.get('payload')
        return injection
    except:
        return default_response


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
