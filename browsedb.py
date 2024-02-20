import sqlite3

while True:
    cmd = input('sql> ')
    if(cmd == 'exit' or cmd == 'quit'):
        exit()
    conn = sqlite3.connect('vulnerable-database.db')
    c = conn.cursor()
    try:
        c.execute(cmd)
        data = c.fetchall()
        if(data == []):
            conn.commit()
        else:
            print(data)
    except:
        conn.close()
