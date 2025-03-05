import streamlit as st
import dhlab.text as dh
import dhlab.ngram as ng
import dhlab.api.dhlab_api as api

import datetime

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance


import altair as alt
from io import BytesIO

from urllib.parse import urlencode



@st.cache_data(show_spinner=False)
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    # output = BytesIO()
    # writer = pd.ExcelWriter(output, engine='openpyxl')
    # df.to_excel(writer, index=True, sheet_name='Sheet1')
    # worksheet = writer.sheets['Sheet1']
    # writer.save()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data
    
@st.cache_data(show_spinner=False)
def get_ngram(words=None,
    from_year=None,
    to_year=None,
    doctype=None,
    lang='nob',
             mode = 'relative'):
    
    #a = #ng.Ngram(words, from_year=from_year, to_year=to_year, doctype=doctype, lang=lang, mode = mode).ngram
    if 'bok' in doctype:
        corpus = 'bok'
    else:
        corpus = 'avis'
        
    a = ng.nb_ngram.nb_ngram(' ,'.join(words),
             corpus = corpus,
             smooth = 1,
             years = (from_year, to_year),
             mode = mode,
            lang = lang)
    a.index = pd.to_datetime(a.index, format='%Y')
    return a




def make_nb_query(name, mediatype, start_date, end_date):
    return f"https://www.nb.no/search?mediatype={mediatype}&" + urlencode({'q': f'"{name}"', 'fromDate': f"{start_date}", 'toDate': f"{end_date}"})


st.set_page_config(page_title="N-gram", layout="wide")


schemes = ['accent',
 'category10',
 'category20',
 'category20b',
 'category20c',
 'dark2',
 'paired',
 'pastel1',
 'pastel2',
 'set1',
 'set2',
 'set3',
 'tableau10',
 'tableau20',
 'blues',
 'greens',
 'oranges',
 'reds',
 'purples',
 'greys',
 'viridis',
 'magma',
 'inferno',
 'plasma',
 'bluegreen',
 'bluepurple',
 'greenblue',
 'orangered',
 'purplebluegreen',
 'purpleblue',
 'purplered',
 'redpurple',
 'yellowgreenblue',
 'yellowgreen',
 'yelloworangebrown',
 'yelloworangered',
 'blueorange',
 'brownbluegreen',
 'purplegreen',
 'pinkyellowgreen',
 'purpleorange',
 'redblue',
 'redgrey',
 'redyellowblue',
 'redyellowgreen',
 'spectral']


if 'smooth' not in st.session_state:
    st.session_state['smooth'] = 4

if 'years' not in st.session_state:
    st.session_state['years'] = (1954, datetime.date.today().year)


cola,_,_,colb = st.columns([1,1,1,1])
with colb:    
    im = Image.open("DHlab_logo_web_en_black.png").convert('RGBA')
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(.4)
    im.putalpha(alpha)
    st.image(im, width = 300)
    #[![A mushroom-head robot](/assets/images/codey.jpg 'Codey the Codecademy mascot')](https://codecademy.com)

with cola:
    st.markdown('### NB N-gram')
    
   

st.markdown("---")




cola0, cola1, cola2, cola3 = st.columns([4,1,1,1])
with cola0:
    text = st.text_input("Ord og fraser", "")
    words = [x.strip() for x in text.split(',')]

with cola1:
    korpus = st.selectbox("Korpus", options = ['avis', 'bok'], help="Velg mellom bøker og aviser")
    if korpus == 'avis':
        mediatype = 'aviser'
    else:
        mediatype = 'bøker'
        
with cola2:
    if korpus != 'avis':
        lang = st.selectbox("Språk-kode", options = ['nob','nno', 'sme', 'fkv'], help = "Sett ISO språk-kode for å velge språk eller målform")
    else:
        lang = st.selectbox("Språk-kode", options = [], help = "Sett ISO språk-kode for å velge språk eller målform")
        lang = None
        
with cola3:
    kumulativ = False
    kohort = False
    mode = st.selectbox("Frekvenstype", ['relativ', 'abslutt', 'kumulativ', 'kohort'], help = "Vis kurven med relative tall, absolutt frekvens (sett glatting til minimum) eller kumulativ frekvens. Alternativet kohort benyttes når det er flere ord, og viser det innbyrdes forhold mellom ordene.")
    if mode == 'kumulativ':
        kumulativ = True
        mode = 'absolutt'
    if mode == 'kohort':
        kohort = True
        mode = 'absolutt'

    
ngram = get_ngram(
    words=words, 
    from_year = st.session_state['years'][0], 
    to_year = st.session_state['years'][1], 
    doctype = korpus, 
    lang = lang, 
    mode=mode
)

start_date = pd.Timestamp(f"{str(st.session_state['years'][0])}-01-01").strftime('%Y%m%d')
end_date = pd.Timestamp(f"{str(st.session_state['years'][1])}-12-31").strftime('%Y%m%d')

if kumulativ:
    chart = ngram.cumsum()
    
elif kohort:
    chart = (ngram.transpose()/ngram.sum(axis=1)).transpose().rolling(window = st.session_state['smooth'], win_type='triang').mean()
    
else:
    chart = ngram.rolling(window = st.session_state['smooth'], win_type='triang').mean()

    
## ---- draw ngram chart



#df = ngram(allword, mid_date, sammenlign, title = avisnavn)

df_for_print = chart.reset_index().rename(columns = {'index':'Dato', '0':'Token'})


# konverter til altair long form

df_alt = df_for_print.melt('Dato', var_name='Token', value_name='Frekvens')

## Kode merket med ## er for å legge til tooltip på grafen - fungerer ikke så bra

df_alt['url'] = df_alt['Token'].apply(lambda x:make_nb_query(x, mediatype, start_date, end_date))

ngram_chart = alt.Chart(df_alt, height=500).mark_line().encode(
    x=alt.X('Dato:T', axis=alt.Axis(titleFontSize=16, labelFontSize=16, labelAngle=-45)),  # Customize X-axis
    y=alt.Y('Frekvens:Q', axis=alt.Axis(titleFontSize=16, labelFontSize=16)),  # Customize Y-axis
    color=alt.Color('Token', scale=alt.Scale(scheme=st.session_state.get('theme', 'tableau20'))),
    href='url',
    tooltip=['Token', 'Dato', 'Frekvens']
).configure_mark(
    opacity=st.session_state.get('alpha', 0.9),
    strokeWidth=st.session_state.get('width', 5.0)
).configure_legend(
    gradientLength=400,
    gradientThickness=10,
    symbolSize=300,
    titleFontSize=20,
    labelFontSize=20
)


ngram_chart['usermeta'] = {
    "embedOptions": {
        'loader': {'target': '_blank'}
    }
}

st.altair_chart(ngram_chart, theme=None, use_container_width=True)
    


## --- params ----

colb1, colb2 = st.columns(2)
with colb1:
    smooth = st.slider("Glatting", min_value=1, max_value = 10, value=st.session_state['smooth'], key='smooth', help="Angir hvordan kurven jevnes ut - uten effekt for kumulativ graf")
    
with colb2:
    years = st.slider('Periode', 1810, datetime.date.today().year, st.session_state['years'], key="years", help = "Start- og sluttår for kurven")

    
st.markdown("---")


    
st.session_state.update()



colf, col2, col_theme, col_alpha, col_width = st.columns([3,3,2,2,2])
with colf:
    filnavn = st.text_input("Last ned data i excelformat", f"ngram_{start_date}_{end_date}.xlsx", help="Filen blir sannsynligvis liggende i nedlastningsmappen - endre gjerne på filnavnet, men behold .xlsx")

if st.download_button(f'Klikk for å laste ned til {filnavn}', to_excel(chart), filnavn, help = "Åpnes i Excel eller tilsvarende"):
    pass

with col_theme:
    theme = st.selectbox("Angi farger", schemes, index=schemes.index('tableau20'), key='theme', help="Palettene er beskrevet her: https://vega.github.io/vega/docs/schemes/#reference")
with col_alpha:
    alpha = st.number_input("Gjennomsiktighet", min_value= 0.1, max_value=1.0, value = st.session_state.get('alpha', 0.9), step=0.1, key='alpha', help="Jo mindre verdi jo mer gjennomsiktig")
with col_width:
    width = st.number_input("Linjetykkelse", min_value = 0.5, max_value=30.0, value = st.session_state.get('width',3.0), step=1.0, key='width', help="Linjene justeres i enheter på 0.5")


#st.markdown("""[DH ved Nasjonalbiblioteket](https://nb.no/dh-lab)""")

