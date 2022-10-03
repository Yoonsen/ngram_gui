import streamlit as st
import dhlab.text as dh
import dhlab.ngram as ng
import dhlab.api.dhlab_api as api

import datetime

import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

def get_ngram(words=None,
    from_year=None,
    to_year=None,
    doctype=None,
    lang='nob'):
    a = ng.Ngram(words, from_year, to_year, doctype, lang)
    return a.ngram



text = st.text_input("Ord og fraser", "")
words = [x.strip() for x in text.split(',')]

col1, col2,  col3 = st.columns(3)
with col1:
    korpus = st.selectbox("Korpus", options = ['avis', 'bok'])

    
with col2:
    lang = st.selectbox("Velg språk", options = ['nob','nno', 'sme'])

with col3:
    today = datetime.date.today()
    year = today.year
    years = st.slider(
    'Periode',
    1810, year, (1950, year))
    
ngram = get_ngram(words=words, from_year = years[0], to_year = years[1], doctype = korpus, lang = lang)

st.line_chart(ngram)