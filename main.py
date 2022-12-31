import os
import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
from PIL import Image
from urllib.request import urlopen


SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI = os.environ['SPOTIPY_REDIRECT_URI']


scope = 'user-top-read'


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))



st.title('🎵 Deine Spotify-Daten')
st.write('')

col1, col2 = st.columns([1,5])
col2.subheader('[' + sp.me().get('display_name') + '](' + sp.me().get('external_urls').get('spotify') + ') (' + sp.me().get('id') + ')')
col2.write('Follower: ' + str(sp.me().get('followers').get('total')))
col1.image( sp.me().get('images')[0].get('url'), width=75 )

st.write('')

ranges = st.radio("Zeitbezug", ('Letzte 4 Wochen', 'Letzte 6 Monate', 'Alle Daten'), horizontal=True)

if ranges == 'Letzte 4 Wochen':
    zeitbezug = 'short_term'
elif ranges == 'Letzte 6 Monate':
    zeitbezug = 'medium_term'
elif ranges == 'Alle Daten':
    zeitbezug = 'long_term'

# Shows the top artists for a user
results = sp.current_user_top_artists(time_range=zeitbezug, limit=50)
df = pd.DataFrame(results['items'])

results_top_lieder = sp.current_user_top_tracks(time_range=zeitbezug, limit=50)
df_top_lieder = pd.DataFrame(results_top_lieder['items'])



df.index = np.arange(1, len(df) + 1)
df['Name'] = df.name
df['Genres'] = df.genres
df['Popularität'] = df.popularity 

df2 = df[['Name', 'Genres', 'Popularität']]





def pic_of_artist(name):
    artist = sp.search(q='artist:' + name, type='artist')['artists']['items'][0]['images'][0]['url']
    return artist

def resize_image(image: Image, length: int) -> Image:
    if image.size[1] == image.size[0]:
        return image
    elif image.size[1] > image.size[0]:
        # Hochkant-Bild
        required_loss = image.size[1] - image.size[0]
        resized_image = image.crop(
            box=(
                0, 
                required_loss / 2, 
                image.size[0], 
                image.size[1] - required_loss / 2))
        return resized_image
    elif image.size[0] > image.size[1]:
        # Breit-Bild
        required_loss = image.size[0] - image.size[1]
        resized_image = image.crop(
            box=(
                required_loss / 2, 
                0,
                image.size[0] - required_loss / 2, 
                image.size[1]))
        return resized_image



st.header('Deine Lieblingskünstler')


col1, col2, col3 = st.columns([1,1,1], gap="medium")

col1.subheader('1. ' + df['Name'][1])
img = Image.open(urlopen(pic_of_artist(df['Name'][1])))
col1.image(
    resize_image(image= img, length= 10000),
    width=200,
    use_column_width=True
)

col2.subheader('2. ' + df['Name'][2])
img = Image.open(urlopen(pic_of_artist(df['Name'][2])))
col2.image(
    img,
    width=200,
    use_column_width=True
)

col3.subheader('3. ' + df['Name'][3])
img = Image.open(urlopen(pic_of_artist(df['Name'][3])))
col3.image(
    resize_image(image= img, length= 10000),
    width=200,
    use_column_width=True
)



st.dataframe(df2)



for x in range(1,4):
    st.subheader(str(x) + '. ' + df['Name'][x])
    img = Image.open(urlopen(pic_of_artist(df['Name'][x])))
    st.image( resize_image(image= img, length= 10000), width=100 )

    st.write('**Popularität des Künstlers**')
    st.progress(int(df['Popularität'][df.Name == df['Name'][x]].values[0]))

    st.write('**Aktuell beliebteste Lieder**')
    results_artist_top_tracks = sp.artist_top_tracks(df['uri'][df.Name == df['Name'][x]].values[0])
    for x in range(1,6):
        track = results_artist_top_tracks['tracks'][x-1]
        col1, col2 = st.columns([3,1])
        col1.write(str(x) + '. ' + track['name'])
        col2.image(track['album']['images'][0]['url'], width=30)
        #col3.audio( track['preview_url'], format="audio/wav" )
    


st.subheader('Deine meistegehörtesten Lieder')


df_top_lieder.index = np.arange(1, len(df_top_lieder) + 1)
df_top_lieder['Dauer'] = pd.to_datetime(df_top_lieder['duration_ms'], unit='ms').dt.strftime('%M:%S')
df_top_lieder['Album'] = [d.get('name') for d in df_top_lieder.album]
df_top_lieder['Song'] = df_top_lieder.name 
df_top_lieder['Explizit'] = df_top_lieder.explicit
df_top_lieder['Popularität'] = df_top_lieder.popularity 


new_list = []
for list in df_top_lieder.artists:
    new_list.append([nested_list['name'] for nested_list in list])

df_top_lieder['Künstler'] = pd.Series(new_list).values


df_full = df_top_lieder [[
    'Album',
    'Künstler',
    'available_markets',
    'disc_number',
    'duration_ms',
    'Dauer',
    'Explizit',
    'external_ids',
    'external_urls',
    'href',
    'id',
    'is_local',
    'name',
    'Popularität',
    'preview_url',
    'track_number',
    'type',
    'uri'
    ]]


df_top_lieder = df_top_lieder [[
    'Song',
    'Künstler',
    'Album',
    'Dauer',
    'Explizit',
    'Popularität',
    ]]

st.write(df_top_lieder)