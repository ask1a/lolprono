import sqlite3
"""Script à modifier suivant la situation, et à executer dans le venv du serveur
> cd lolprono
> source venv/bin/activate
> python
"""
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
        return None


def update_developer_salary(conn):
    try:
        cursor = conn.cursor()
        sql_update_query = """UPDATE game SET game_datetime = "2024-05-03 09:00:00"  
        WHERE team_1 = 'Fnatic' and team_2 = 'Top Esport' and game_datetime like "2024-05-03%"
        """
        cursor.execute(sql_update_query)
        conn.commit()
        print("Enregistrement mis à jour avec succès !")
    except sqlite3.Error as error:
        print("Échec de la mise à jour de la table SQLite :", error)
    finally:
        if conn:
            conn.close()
            print("La connexion SQLite est fermée.")

database_file = "../instance/db.sqlite"
connection = create_connection(database_file)
if connection:
    update_developer_salary(connection)


