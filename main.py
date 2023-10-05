import streamlit as st
from scraping import scrape_movies
from database import store_data, check_movie_in_database
import datetime
import time

# Reiner Check, um verschiedene Runs zu unterscheiden
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print(f"###### NEW RUN ##### {current_time}")

# Initialisierung des Session States, um dort Informationen zu speichern, die später in der Subpage für Ratings genutzt werden
st.session_state.selected_movies = {}

# Definition der Visualisierungsfunktion, die auf der main Page Titel, Bilder etc. der Filme anzeigt
# Es werden eine der drei Spalten, die row (sqlite3), die Größe für die Bilder und die Höhe für die Zeile übergeben

def visualization(movie_col, row, image_height, row_height):
    # Darstellung aller Werte aus der row
    movie_col.markdown(f"**ID:** {row[0]}")
    movie_col.markdown(f"**Titel:** {row[1]}")
    movie_col.markdown(f"**Year:** {row[4]}")
    movie_col.markdown(f"**Rating:** {row[-3]}")
    movie_col.markdown(f"**Genre:** {row[-1]}")
    # Überprüfung, ob es ein Bild gibt
    if row[3]:
        image_html = f'<img src="{row[3]}" alt="{row[1]}" style="height:{image_height}px; display: block; margin: 0 auto;">'
        row_style = f"height: {row_height}px; margin-bottom: 20px; overflow: hidden;"
        movie_col.markdown(
            f'<div style="{row_style}">'
            f"{image_html}"
            f"</div>",
            unsafe_allow_html=True,
        )

    # Überprüfung, ob der Eintrag schon in der Session State ist, wenn nicht, wird er hinzugefügt
    if row[0] not in st.session_state.selected_movies:
        st.session_state.selected_movies[row[0]] = (row[1], row[3])

# Bild und Zeilenhöhe für die Visualisierungsfunktion
image_height = 200
row_height = 300

# Streamlit Page Set Up
st.set_page_config(layout='wide')

# Header zu IMDb mit Link
st.header("[IMDd Movie & TV Series Data](https://www.imdb.com/)")

# Definition von drei Streamlit Spalten
col1, col2, col3 = st.columns(3)

# Title für die Sidebar
st.sidebar.title("Search")

# Definition diverser Variablen, die über Textinput und Selectboxen zu vermitteln sind
search = st.sidebar.text_input("What are you looking for?")

titleType = st.sidebar.selectbox("Title type", ["All", "Movies", "tvSeries"])

genre = st.sidebar.selectbox("Genre", ["All", "comedy", "horror", "romance", "thriller", "sci-fi", "drama", "action", "adventure", "animation", "biography", "crime", "documentary", "family","fantasy", "film-noir", "game-show", "history", "music", "musical","mystery", "news", "reality-tv", "sport", "talk-show", "war", "western"])

userRatingMin = st.sidebar.selectbox("Minimum rating", [0.0 ,6.0, 7.0, 8.0, 9.0])

releaseDateMin = st.sidebar.number_input("Minimum Release Year", value=1900, min_value=1900)
releaseDateMax = st.sidebar.number_input("Maximum Release Year", value=datetime.date.today().year)

# Hauptfunktion, die beginnt, wenn der Button gedrückt wird

if st.sidebar.button('Start search'):
    
    # Überprüfung, ob Ergebnisse, die den Kriterien entsprechen, bereits in der Datenbank sind
    movie_rows = check_movie_in_database(search, titleType, userRatingMin, genre, releaseDateMin, releaseDateMax)
    #movie_rows = False
    # Wenn die movie_rows returned wurden aus dem Database Check
    if movie_rows:
        num_columns = 3
        rows_per_column = (len(movie_rows) + num_columns - 1) // num_columns
        for i, row in enumerate(movie_rows):
            #print(row)
            #print("#####Database")
            col = i % num_columns
            if col == 0:
                movie_col = col1
            elif col == 1:
                movie_col = col2
            else:
                movie_col = col3
            # Visualisierungsfunktion wird ausgeführt
            visualization(movie_col, row, image_height, row_height)
            
    # Wenn keine movie_rows returned wurden aus dem Database Check
    else:
        # Data wird nach angegebenen Kriterien gescraped
        scraped_data = scrape_movies(search, titleType, userRatingMin, genre, releaseDateMin, releaseDateMax)
        # Data wird gestored in der Datenbank
        store_data(scraped_data)
        # Es wird wird wieder gecheckt, ob die Daten in der Datenbank sind
        movie_rows = check_movie_in_database(search, titleType, userRatingMin, genre, releaseDateMin, releaseDateMax)
        # Falls ja, werden sie visualisiert
        if movie_rows:
            num_columns = 3
            for i, row in enumerate(movie_rows):
                col = i % num_columns
                if col == 0:
                    movie_col = col1
                elif col == 1:
                    movie_col = col2
                else:
                    movie_col = col3
                visualization(movie_col, row, image_height, row_height)
        # Falls sie immer noch nicht in der Datenbank sind (z.B. weil es keinen Film mit dem Namen gibt)
        else:
            st.title("No results found!")

    

    

