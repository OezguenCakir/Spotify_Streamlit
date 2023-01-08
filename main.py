import os
import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import numpy as np
from PIL import Image
from urllib.request import urlopen
import requests
import base64
from io import BytesIO

def to_b64(url):
    return base64.b64encode(requests.get(url).content)

def df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name= 'Top Songs' + ranges)
    workbook = writer.book
    workbook.formats[0].set_font_name('Helvetica')
    workbook.formats[0].set_border(2)
    worksheet = writer.sheets['Top Songs' + ranges]
    worksheet.autofilter(0, 0, df.shape[0], df.shape[1]-1) # activate filter on column headers
    header_format = workbook.add_format({ # define header format
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#006E9D',
            'font_color': 'white',
            'border': 0,
            'font_name': 'Helvetica'
            })
    for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max(
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
                ) + 5  # adding more space
            worksheet.set_column(idx, idx, max_len)  # set column width
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format) # set header format
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data


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


SPOTIPY_CLIENT_ID =     os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI =  os.environ['SPOTIPY_REDIRECT_URI']


scope = 'ugc-image-upload user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-follow-modify user-follow-read user-read-playback-position user-top-read user-read-recently-played user-library-modify user-library-read user-read-email user-read-private'
#'user-top-read'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_path='cache.txt'))
user=sp.me().get('id')


st.title('🎵 Deine Spotify-Daten')
st.write('')

col1, col2 = st.columns([1,5])
col1.image( sp.me().get('images')[0].get('url'), width=75 )
col2.subheader('[' + sp.me().get('display_name') + '](' + sp.me().get('external_urls').get('spotify') + ') (' + sp.me().get('id') + ')')
col2.write('Follower: ' + str(sp.me().get('followers').get('total')))
col2.write('E-Mail: ' + str(sp.me().get('email')))


ranges = st.radio("Zeitbezug", ('Letzte 4 Wochen', 'Letzte 6 Monate', 'Ganzer Zeitraum'), horizontal=True)

if ranges == 'Letzte 4 Wochen':
    zeitbezug = 'short_term'
    image_b64 = to_b64('https://raw.githubusercontent.com/OezguenCakir/Spotify_Streamlit/main/pictures/top_tracks_4weeks.jpg')
elif ranges == 'Letzte 6 Monate':
    zeitbezug = 'medium_term'
    image_b64 = to_b64('https://raw.githubusercontent.com/OezguenCakir/Spotify_Streamlit/main/pictures/top_tracks_6months.jpg')
elif ranges == 'Ganzer Zeitraum':
    zeitbezug = 'long_term'
    image_b64 = to_b64('https://raw.githubusercontent.com/OezguenCakir/Spotify_Streamlit/main/pictures/top_tracks_alldata.jpg')

# Shows the top artists for a user
results = sp.current_user_top_artists(time_range=zeitbezug, limit=50)
df = pd.DataFrame(results['items'])





df.index = np.arange(1, len(df) + 1)
df['Name'] = df.name
df['Genres'] = df.genres
df['Popularität'] = df.popularity 

df2 = df[['Name', 'Genres', 'Popularität']]







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



st.header('Deine meistegehörtesten Lieder')


results_top_lieder = sp.current_user_top_tracks(time_range=zeitbezug, limit=50)
df_top_lieder = pd.DataFrame(results_top_lieder['items'])

df_top_lieder.index =           np.arange(1, len(df_top_lieder) + 1)
df_top_lieder['Dauer'] =        pd.to_datetime(df_top_lieder['duration_ms'], unit='ms').dt.strftime('%M:%S')
df_top_lieder['Album'] =        [d.get('name') for d in df_top_lieder.album]
df_top_lieder['Song'] =         df_top_lieder.name 
df_top_lieder['Explizit'] =     df_top_lieder.explicit
df_top_lieder['Popularität'] =  df_top_lieder.popularity
df_top_lieder['Album Cover'] =  [d.get('images')[1].get('url') for d in df_top_lieder.album]

new_list = []
for list in df_top_lieder.artists:
    new_list.append([nested_list['name'] for nested_list in list])

df_top_lieder['Künstler'] = pd.Series(new_list).values
df_top_lieder.index = np.arange(1, len(df_top_lieder) + 1)


col1, col2, col3 = st.columns(3, gap='medium')

col1.image(df_top_lieder['Album Cover'][1], width=200, use_column_width=True)
col1.write('**1. ' + df_top_lieder['Song'][1] + '**' + '  \n' + str(df_top_lieder['Künstler'][1]).strip("'[]").replace("'",""))

col2.image(df_top_lieder['Album Cover'][2], width=200, use_column_width=True)
col2.write('**2. ' + df_top_lieder['Song'][2] + '**' + '  \n' + str(df_top_lieder['Künstler'][2]).strip("'[]").replace("'",""))

col3.image(df_top_lieder['Album Cover'][3], width=200, use_column_width=True)
col3.write('**3. ' + df_top_lieder['Song'][3] + '**' + '  \n' + str(df_top_lieder['Künstler'][3]).strip("'[]").replace("'",""))

df_top_lieder = df_top_lieder [['Song', 'Künstler', 'Album', 'Dauer', 'Explizit', 'Popularität' ]]
st.write(df_top_lieder)

col1, col2 = st.columns(2)

if col1.button(label='🎶 Erstelle Playlist'):
    playlist = sp.user_playlist_create(
        user=user,
        name="Deine Top-Songs - " + ranges
    )
    playlist_id = playlist["id"]
    sp.user_playlist_add_tracks(
        user=user,
        playlist_id=playlist_id,
        tracks=pd.DataFrame(results_top_lieder['items']).id
       )
    sp.user_playlist_change_details(
        user=user,
        playlist_id=playlist_id,
        description="Gloreich gebaut von Özgün Cakir. Besuche auch seine Webseite unter www.özgüncakir.de"
    )
    sp.playlist_upload_cover_image(
        playlist_id=playlist_id,
        image_b64=image_b64
    )
    col1.write('Playlist wurde erstellt :)')

col2.download_button(
    label='📥 Excel-Datei',
    data=df_to_excel(df_top_lieder),
    file_name= 'topsongs-' + ranges + '.xlsx'
    )

user_playlists =    sp.user_playlists(user, offset=0)
num_playlists =     str(user_playlists.get('total'))
df_playlists =      pd.DataFrame(user_playlists.get('items'))

st.header('Du hast ' + num_playlists + ' Playlists gespeichert')
df_playlists.index =        np.arange(1, len(df_playlists) + 1)
df_playlists['Lieder'] =    [d.get('total') for d in df_playlists['tracks']]
df_playlists['Besitzer'] =  [d.get('display_name') for d in df_playlists['owner']]
df_playlists['Link'] =      [d.get('spotify') for d in df_playlists['external_urls']]


col1, col2, col3 = st.columns(3, gap='medium')

cover_firstplaylist = resize_image(Image.open(urlopen(df_playlists['images'].str[0].iloc[-1].get('url'))), length= 10000)

col1.image(df_playlists.sort_values(by='Lieder', ascending=False)['images'].str[0].iloc[0].get('url'), width=200, use_column_width=True)
col1.write('Playlist mit meisten Liedern:  \n' + df_playlists.sort_values(by='Lieder', ascending=False)['name'].iloc[0])

col2.image(df_playlists['images'].str[0].iloc[0].get('url'), width=200, use_column_width=True)
col2.write('neueste Playlist:  \n' + df_playlists['name'].iloc[0])

col3.image(cover_firstplaylist, width=200, use_column_width=True)
col3.write('erste Playlist:  \n' + df_playlists['name'].iloc[-1])


df_playlists.drop(
    columns=['owner', 'external_urls', 'images', 'href', 'uri', 'tracks', 'snapshot_id', 'primary_color', 'type'],
    inplace=True)

df_playlists.rename(
    columns={"description": "Beschreibung", "name": "Name", "public":"Öffentlich", "collaborative":"Gemeinsam"},
    inplace=True)

df_playlists = df_playlists[['Name', 'Besitzer', 'Öffentlich', 'Gemeinsam', 'Lieder', 'Beschreibung', 'Link']]
st.write(df_playlists)




num_saved_songs = sp.current_user_saved_tracks().get('total')

num_limit_steps= int( num_saved_songs / 50.0 )

st.header('Du hast ' + str(num_saved_songs) + ' als Lieblingssongs markiert')


st.header('Deine Geräte')

df_devices = pd.DataFrame(sp.devices()['devices'])
df_devices.index = np.arange(1, len(df_devices) + 1)
st.write(df_devices)


# PODCASTS
st.header('Du hast ' + str(sp.current_user_saved_shows(limit=50)['total']) + ' Podcasts gespeichert')
df_shows = pd.DataFrame(sp.current_user_saved_shows(limit=50)['items'])

df_shows['Hinzugefügt am'] =    df_shows['added_at']
df_shows['Name'] =              [d.get('name') for d in df_shows['show']]
df_shows['Herausgeber'] =       [d.get('publisher') for d in df_shows['show']]
df_shows['Episoden'] =          [d.get('total_episodes') for d in df_shows['show']]
df_shows['Sprache'] =           [d.get('languages') for d in df_shows['show']]
df_shows['Beschreibung'] =      [d.get('description') for d in df_shows['show']]
df_shows['Explizit'] =          [d.get('explicit') for d in df_shows['show']]
df_shows['Extern gehosted'] =   [d.get('is_externally_hosted') for d in df_shows['show']]


col1, col2, col3 = st.columns(3)
col1.image([d.get('images') for d in df_shows['show']][0][1].get('url'), width=200, use_column_width=True)
col1.write('als letztes hinzugefügt:  \n' + df_shows['Name'].iloc[0])

col2.image([d.get('images') for d in df_shows['show']][-1][1].get('url'), width=200, use_column_width=True)
col2.write('als erstes hinzugefügt:  \n' + df_shows['Name'].iloc[-1])

col3.image(df_shows.sort_values(by='Episoden', ascending=False)['show'].iloc[0].get('images')[1].get('url'), width=200, use_column_width=True)
col3.write('meiste Episoden:  \n' + df_shows.sort_values(by='Episoden', ascending=False)['Name'].iloc[0])

df_shows.index = np.arange(1, len(df_shows) + 1)
df_shows.drop(columns=['added_at', 'show'], inplace=True)

st.write(df_shows)


# ZULETZT GESPIELT
st.header('Zuletzt gespielt')
df_currently_played = pd.DataFrame(sp.current_user_recently_played()['items'])

df_currently_played['Datum'] =          df_currently_played['played_at']
df_currently_played['Song'] =           [d.get('name') for d in df_currently_played['track']]
df_currently_played['Künstler'] =       [d.get('artists') for d in df_currently_played['track']]
df_currently_played['Album'] =          [d.get('album').get('name') for d in df_currently_played['track']]
df_currently_played['Popularität'] =    [d.get('popularity') for d in df_currently_played['track']]
df_currently_played['Dauer'] =          pd.to_datetime([d.get('duration_ms') for d in df_currently_played['track']], unit='ms').strftime('%M:%S')
df_currently_played['Explizit'] =       [d.get('explicit') for d in df_currently_played['track']]
df_currently_played['Typ'] =            [d.get('type') for d in df_currently_played['track']]

new_list = []
for list in df_currently_played['track']:
    new_list.append([nested_list['name'] for nested_list in list['artists']])

df_currently_played['Künstler'] = pd.Series(new_list).values

#[d.get('duration_ms') for d in df_currently_played['track']]
df_currently_played.index = np.arange(1, len(df_currently_played) + 1)

df_currently_played.drop(columns=['track', 'played_at', 'context'], inplace=True)


st.write(df_currently_played)



st.subheader('Folgst du mir?')

if sp.current_user_following_users(ids=['napoleonuncle'])[0]:
    st.success('Ja, sehr schön!')
else:
    st.error('Nein, aber du kannst es noch nachholen :)')

