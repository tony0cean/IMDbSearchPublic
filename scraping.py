import pandas as pd
import requests

def scrape_movies(search, titleType = None, userRatingMin = None, sortArg = "user_rating,des", genre = None, releaseDateMin = None, releaseDateMax = None):

	# Base URL fürs erstes Scraping
	base_url = "https://imdb8.p.rapidapi.com/title/v2/find"

	#querystring = {"title": search,"titleType": titleType,"limit":"20","sortArg":"moviemeter,asc"}
	# Übergabe der Variablen an die Anfrage
	querystring = {"title": search ,"titleType": titleType,"userRatingMin": userRatingMin,"limit":"20","sortArg": sortArg,"genre": genre,"releaseDateMin": releaseDateMin,"releaseDateMax": None}

	# mein API Key
	headers = {
		"X-RapidAPI-Key": "YOUR API KEY",
		"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
	}
	# Get Anfrage an die API
	response = requests.get(base_url, headers=headers, params=querystring)

	# Alles in Dict packen
	if response.status_code == 200:
		api_response = response.json()
		data_list = api_response.get('results', [])
		#print(data_list)

		# Diverse get funktionen, um Informationen aus der json zu ziehen
		def _find_id(entry):
			return entry.get('id', '').split('/')[-2]

		def _find_title(entry):
			return entry.get('title', '')

		def _find_type(entry):
			return entry.get('titleType', '') 

		def _find_image(entry):
			image_info = entry.get('image', {})
			return image_info.get('url', '')

		def _find_year(entry):
				return entry.get('year', '')

		def _find_actors(entry):
			actors = []
			principals = entry.get('principals', [])
			for actor in principals:
				if actor['category'] == 'actor':
					actors.append(actor['name'])
			return ', '.join(actors)
		# Dictionary definieren
		infos = {
			'id': [],
			'titles': [],
			'type': [],
			'image_url': [],
			'year': [],
			'stars': []
		}
		# Alle infos werden in dieses Dictionary verpackt
		for entry in data_list:
			infos['id'].append(_find_id(entry))
			infos['titles'].append(_find_title(entry))
			infos['type'].append(_find_type(entry))
			infos['image_url'].append(_find_image(entry))
			infos['year'].append(_find_year(entry))
			infos['stars'].append(_find_actors(entry))

		# Dict in Dataframe umwandeln

		df = pd.DataFrame(infos)

		#print(f"##################IDs:{infos['id']}")
		#print(df['id'])

		
	else:
		# Falls keine response kommt
		print(f"Failed to get API data. Status code: {response.status_code}")

	# ratings abfragen, dann in df packen, dann dfs concaten

	# Zweite API Anfrage
	ratings_data = []

	for i in range(len(df)):
		# Andere API, die aber selben unique Key der Filme nutzt, also wird der in die Url zur Anfrage eingebaut
		url = f"https://moviesdatabase.p.rapidapi.com/titles/{df.loc[i, 'id']}/ratings"
		# Same same
		headers = {
			"X-RapidAPI-Key": "YOUR API KEY",
			"X-RapidAPI-Host": "moviesdatabase.p.rapidapi.com"
		}
		# Same same
		response = requests.get(url, headers=headers)
		response_data = response.json()
		
		# Je nachdem, ob es Ratings gibt oder nicht, werden sie appendet oder nicht
		# War wichtig, da in den Datenbanken auch upcoming movies wie Avatar 5 aus 2030 liegen
		if response_data.get("results") is not None:
			ratings_data.append({
				"averageRating": response_data["results"]["averageRating"],
				"numVotes": response_data["results"]["numVotes"]
			})
		else:
			ratings_data.append({
				"averageRating": None,
				"numVotes": None
			})

	
	ratings_df = pd.DataFrame(ratings_data)

	# Dritte API Anfrage für die Genres
	scraped_genres = []

	# Selbes Spiel wie bei den Ratings mit der ID
	for i in range(len(df)):
		url = "https://imdb8.p.rapidapi.com/title/get-genres"
		querystring = {"tconst": {df.loc[i, 'id']}}
		headers = {
			"X-RapidAPI-Key": "YOUR API KEY",
			"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
		}
		response = requests.get(url, headers=headers, params=querystring)
		genres = response.json()
		# Hier einziger Unterschied, dass ich alle Genres als ein String in einer dp.df Spalte wollte, aber eine Liste mit Genres von der API bekommen habe
		scraped_genres.append(', '.join(genres)) 

	# hier als Spalte in ein df eingefügt
	genres_df = pd.DataFrame(scraped_genres, columns=["genre"])
	#print(f"##################Genre DF:{genres_df}")


	
	# Und hier alle Dataframes zusammenführen
	scraped_data = pd.concat([df, ratings_df, genres_df], axis=1)

	#scraped_data.dropna(inplace=True)
    
	'''
	#Hier die Actors noch aufteilen, und in numerische werte umwandeln, falls ML noch gemacht wird
	df = pd.concat([df, df['stars'].str.split(', ', expand=True)], axis=1, )
    df.rename(columns={0: "Actor_1", 1: "Actor_2"}, inplace = True)
    df['Actor_1'] = pd.factorize(df['Actor_1'])[0]
    df['Actor_2'] = pd.factorize(df['Actor_2'])[0]
	'''
	
	return scraped_data

