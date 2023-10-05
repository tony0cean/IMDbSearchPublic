from scraping import scrape_movies
import sqlite3


def store_data(scraped_data):

    # Verbindung zur Datenbank wird hergestellt
    conn = sqlite3.connect('movies.db')

    # Iteriert über mein gescraptes Dataframe (iterrows wie enumerate for pd dfs) und packt die daten in die jeweiligen Spalten der SQL tabelle
    for _, row in scraped_data.iterrows():
        conn.execute('''
            INSERT OR REPLACE INTO movies (id, titles, type, image_url, year, stars, averageRating, numVotes, genre)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row['id'], row['titles'], row['type'], row['image_url'], row['year'], row['stars'], row['averageRating'], row['numVotes'], row['genre']))

    # Änderungen bestätigen
    conn.commit()
    # Verbindung schließen
    conn.close()

def check_movie_in_database(search, titleType = None, userRatingMin = None, genre = None, releaseDateMin = None, releaseDateMax = None):

    # Verbindung zur Datenbank wird hergestellt
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    # Sollte es die Tabelle nicht geben, erstellen
    c.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id TEXT PRIMARY KEY,
            titles TEXT,
            type TEXT,
            image_url TEXT,
            year INTEGER,
            stars TEXT,
            averageRating REAL,
            numVotes INTEGER,
            genre TEXT
        )
    ''')

    # Same same
    conn.commit()
    conn.close()

    # Same same
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()

    #print("Querying for movie:", movie_name)
    #print(type(movie_name))

    # Je nach Übergabe von Kriterien aus der main wird die query zusammengebaut
    
    query = "SELECT * FROM movies WHERE UPPER(titles) LIKE ?"

    if titleType != "All":
        query += " AND type = ?"

    query += " AND image_url IS NOT NULL AND averageRating IS NOT NULL AND averageRating >= ?"

    if genre != "All":
        query += " AND genre LIKE ?"

    if titleType == "All":
        if genre == "All":
            cursor.execute(query, ('%' + search.upper() + '%', userRatingMin))
        else:
            cursor.execute(query, ('%' + search.upper() + '%', userRatingMin, '%' + genre + '%'))
    else:
        if genre == "All":
            cursor.execute(query, ('%' + search.upper() + '%', titleType, userRatingMin))
        else:
            cursor.execute(query, ('%' + search.upper() + '%', titleType, userRatingMin, '%' + genre + '%'))

    rows = cursor.fetchall()




    #print("Fetched rows:", rows)
    
    cursor.close()
    conn.close()

    return rows





