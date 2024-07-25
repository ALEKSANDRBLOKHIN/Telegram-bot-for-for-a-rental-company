from flask import Flask, request, jsonify, render_template
import MySQLdb
from api import all_in
app = Flask(__name__)


db_config = {
    'host': 'fojvtycq53b2f2kx.chr7pe7iynqr.eu-west-1.rds.amazonaws.com',      
    'user': 'mlbmqsfjgpivuf5y',
    'password': 'jruz5y7a348ij090',
    'database': 'luv21woivqwwdee4' 
}


def get_db_connection():
    conn = MySQLdb.connect(
        host=db_config['host'],
        user=db_config['user'],
        passwd=db_config['password'],
        db=db_config['database']
    )
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, information, active FROM rent1 ORDER BY active DESC, id ASC;')
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index1.html', data=data)


@app.route('/add', methods=['POST'])
def add():
    information = request.form['information']
    price = request.form['price']
    status = request.form['status']
    inparis = 1 if 'inparis' in request.form else 0
    rooms = request.form['rooms']
    photo = request.form['photo']
    photos = all_in(photo)
    website = 1 if 'website' in request.form else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO rent1 (information, price, status, inparis, rooms, photo, website, active)
     VALUES (%s, %s, %s, %s, %s, %s, %s, 1)''',
                   (information, price, status, inparis, rooms, photos, website))
    conn.commit()
    cursor.close()
    conn.close()
    return index()


@app.route('/update_active', methods=['POST'])
def update_active():
    active_statuses = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    for id1, active in active_statuses.items():
        cursor.execute('UPDATE rent1 SET active = %s WHERE id = %s', (active, id1))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(success=True)



def dump():
    f = open("golden_triangle.sql", 'r', encoding="utf-8")
    conn = get_db_connection()
    cursor = conn.cursor()

    sql_commands = f.read().split(';')
    for command in sql_commands:
        if command.strip():
            cursor.execute(command)
            # Fetch all results to avoid 'Commands out of sync' error
            while cursor.nextset():
                cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()
    f.close()
    return 'Done'




if __name__ == '__main__':
    app.run(debug=True)
