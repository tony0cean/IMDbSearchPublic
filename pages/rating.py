import requests
import streamlit as st
import pandas as pd
import plotly.express as px

def scrape_ratings(id):
    # WIeder API Anfrage, die mit der übergebenen ID Ratings abfragt in der Subpage
    url = "https://imdb8.p.rapidapi.com/title/get-ratings"
    querystring = {"tconst": id}  
    #print(f"query: {querystring}")

    headers = {
        "X-RapidAPI-Key": "YOUR API KEY",
        "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    api_response = response.json()
    #print(api_response)

    return api_response

def create_histograms(api_response, demographic):
    # Holt sich die ratings aus der json
    histograms = api_response.get('ratingsHistograms', {})
    data = []
    # sortiert die Daten, da sie nicht immer in derselben Reihenfolge in der json zurückkommen
    sorted_demographics = sorted(histograms.keys())

    # Wenn alle ausgewählt wird
    if demographic == 'All':
        for demographic in sorted_demographics:
            # Holt sich die Werte nach Demografie
            values = histograms.get(demographic, {})
            # Durchschnitt der Votes
            histogram = values.get('histogram', {})
            # Absolute Anzahl der Votes
            total_ratings = values.get('totalRatings', 0)
            
            # Packt alles in Data, berechnet noch percentage und Anzahl pro Voting Wert
            for rating, count in histogram.items():
                data.append({'Demographic': demographic, 'Rating': int(rating), 'Percentage': count / total_ratings * 100, 'Count': count})
    else:
        # Macht alles für oben, aber nur für die übergeben Demografie
        # Aged 30-44 bei Avatar Way of Water gut, weil ca. 100k votes
        values = histograms.get(demographic, {})
        histogram = values.get('histogram', {})
        total_ratings = values.get('totalRatings', 0)
        
        for rating, count in histogram.items():
            data.append({'Demographic': demographic, 'Rating': int(rating), 'Percentage': count / total_ratings * 100, 'Count': count})

    # Erstellt Daragrame
    df = pd.DataFrame(data)
    # Titel wird angepasst je nachdem was angezeigt wird hier ist ein bug
    title = f'Rating Distribution for All Demographics' if demographic == 'All' else f'Rating Distribution for {demographic}'
    # Plot wird erstellt
    fig = px.bar(df, x='Rating', y='Percentage', color='Demographic', barmode='group', title=title)

    # Hoveranzeige des Plots wird erstellt
    fig.update_traces(hovertemplate='%{y:.2f}%<br>Count: %{customdata[3]}', customdata=df[['Rating', 'Percentage', 'Demographic', 'Count']])    
    # Ticks erstellt
    fig.update_layout(
    xaxis = dict(
        tickmode = 'array',
        tickvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ))
    return fig

# Checkt, ob movies im Session State sind
if hasattr(st.session_state, "selected_movies"):
    # Selectbox für Demografien
    hist_demographic = st.sidebar.selectbox("Show demographic", ['All','Aged 18-29', 'Aged 30-44', 'Aged 45+', 'Aged under 18', 'Females', 'Females Aged 18-29', 'Females Aged 30-44', 'Females Aged 45+', 'Females Aged under 18', 'IMDb Staff', 'IMDb Users', 'Males', 'Males Aged 18-29', 'Males Aged 30-44', 'Males Aged 45+', 'Males Aged under 18', 'Non-US users', 'Top 1000 voters', 'US users'])
    # Spalten erstellen
    columns = st.columns([1, 2]) 
    # Erstellt Unique button, der die Movie ID enthält für jedes Film im Session State
    for movie_id in st.session_state.selected_movies:
        movie_data = st.session_state.selected_movies[movie_id]
        movie_title = movie_data[0]  
        button_key = f"{movie_id}"

        left_column, right_column = columns
        # Wenn button gedrückt wird
        if st.sidebar.button(movie_title, key=button_key):
            st.session_state.selected_movie_id = movie_id
            # Erscheint links Bild + Titel
            with left_column:
                st.write(f"**You selected:** {movie_title}")
                st.image(movie_data[1], width=200)
            # Und rechts das Rating, nachdem gescapred wurde
            with right_column:
                    api_response = scrape_ratings(button_key)
                    single_plot = create_histograms(api_response, hist_demographic)
                    st.plotly_chart(single_plot)
# Oder es ist nichts im Session State              
else:
    st.write("No movies selected.")






