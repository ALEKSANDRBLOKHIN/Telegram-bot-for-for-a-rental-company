import mysql.connector

from config import  db_config


def get_items_from_db(price=None, rooms=None, place=None, index=0, active=None):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM rent1"
    conditions = []
    params = []

    if price is not None:
        conditions.append("price <= %s")
        params.append(price)
    if rooms is not None:
        conditions.append("rooms = %s")
        params.append(rooms)
    if place is not None:
        conditions.append("inparis = %s")
        params.append(place)
    if active is not None:
        conditions.append("active = %s")
        params.append(active)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)


    query += " LIMIT 1 OFFSET %s"
    params.append(index)

    
    cursor.execute(query, params)
    items = cursor.fetchall()

    cursor.close()
    connection.close()
    return items
