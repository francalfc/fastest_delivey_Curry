#=================================================================
#Bibliotecas
#=================================================================

import pandas as pd
import folium
import plotly.express as px
import streamlit as st
from PIL import Image
import plotly.graph_objects as go
from streamlit_folium import folium_static
from haversine import haversine
import numpy as np


# ================================================================
# Funções
# =================================================================
def clean_dados(df):
    
    """
        Essa função é responsável por fazer a limpeza dos dados
        1 - Irá remover as colunas que tem os espaços
        2 - Irá apagar as linhas que tem os valor nulos (NaN)
        3 - Conversão de algumas coluanas categóricas para numericas
        4 -  Criação de uma nova coluna ['distance'] que mostra a distância média do restaurante para o cliente
        5 - Criação da coluna [week_of_year]
    """
    #Limpeza dos dados
    #Eliminando os espaços vazios
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df['Delivery_person_Age'] = df['Delivery_person_Age'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
    df['Weatherconditions'] = df['Weatherconditions'].str.strip()
    df['Road_traffic_density'] = df['Road_traffic_density'].str.strip()
    df['Type_of_order'] = df['Type_of_order'].str.strip()
    df['Type_of_vehicle'] = df['Type_of_vehicle'].str.strip()
    df['Festival'] = df['Festival'].str.strip()
    df['City'] = df['City'].str.strip()

    # Eliminando as linhas que tem o conteu 'NaN'
    linhas_vazias = df['Delivery_person_Age'] != 'NaN'
    df = df.loc[linhas_vazias, :].copy()

    linhas_vazias = df['Road_traffic_density'] != 'NaN'
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['Festival'] != 'NaN'
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['City'] != 'NaN'
    df = df.loc[linhas_vazias, :]

    #Limpando a coluna Time Taken
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1])

    #convertendo as colunas
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # Resetando o index
    df = df.reset_index(drop=True)

    # Crianda a coluna da semana
    df['week_of_year'] = df['Order_Date'].dt.strftime( "%U" )
    # Criando a coluna da distancia
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df['distance'] = df.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude']) ),axis=1)
    return (df)

def avg_std_traffic(df):    
    df_aux = df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']})
    df_aux.columns = ['Ratings_mean','Rating_std']
    df_aux.reset_index()
    st.dataframe(df_aux)
    return df

def avg_std_weatherconditions(df):
    df_aux = df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})
    df_aux.columns = ['Ratings_mean', 'Ratings_std']
    df_aux.reset_index()
    st.dataframe(df_aux)
    return df

def top_delivery(df,top_asc):    
    df_aux = (df.loc[:, ['Delivery_person_ID','Time_taken(min)','City']]
                .groupby([ 'City','Delivery_person_ID'])
                .mean()
                .sort_values(['Time_taken(min)', 'City'], ascending=top_asc)
                .reset_index())
    df1 = df_aux.loc[df_aux['City'] == 'Urban'].head(10)
    df2 = df_aux.loc[df_aux['City'] == 'Metropolitian'].head(10)
    df3 = df_aux.loc[df_aux['City'] == 'Semi-Urban'].head(10)
    df_concat = pd.concat([df1, df2, df3]).reset_index(drop=True)
    st.dataframe(df_concat)
    return df_concat

#--------------------------------------------------------------------------------
#---------------------------------Início do código lógico------------------------
st.set_page_config(page_title='Company_view', page_icon=':car:', layout='wide', initial_sidebar_state='collapsed')
#-----------------------------
#Importação dos dados
#-----------------------------
#Leitura do arquivo
df1 = pd.read_csv('train.csv')
df = df1.copy()

#-----------------------------
#Dataframe limpo
#-----------------------------
df = clean_dados(df)

#===============================================
#BARRA LATERAL
#===============================================
st.header('Marketplace - Visão Entregadores')
imagem = Image.open("logo.png")
st.sidebar.image(imagem, width=120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""______""")
st.sidebar.markdown('Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?',
                   value=pd.datetime(2022, 4, 13),
                   min_value=pd.datetime(2022, 2, 11),
                   max_value=pd.datetime(2022, 4, 13),
                   format='DD-MM-YYYY')
st.sidebar.markdown("""______""")
traffic_option = st.sidebar.multiselect('Quais as condições do trânsito',
                        ['Low', 'Medium', 'High', 'Jam'],
                        default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""______""")
weather_condition = st.sidebar.multiselect('Quais as condições climáticas',
                                           ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
                                            'conditions Cloudy', 'conditions Fog', 'conditions Windy'], default=['conditions Sunny', 'conditions Stormy'])
st.sidebar.markdown("""______""")
st.sidebar.markdown('### Powered by Comnunidade DS')

#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df['Road_traffic_density'] .isin(traffic_option)
df = df.loc[linhas_selecionadas, :]

#Filtro condição climática
linhas_selecionadas = df['Weatherconditions'].isin(weather_condition)
df = df.loc[linhas_selecionadas,:]

#===========================================
#LAYOUT DASHBOARD
#===========================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial' , '-', '-'])
with tab1:
    st.container()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        df_max = df.loc[:, 'Delivery_person_Age'].max()
        col1.metric('Maior Idade', df_max)
    with col2:
        df_min = df.loc[:, 'Delivery_person_Age'].min()
        col2.metric('Menor Idade', df_min)
    with col3:
        df_better = df.loc[:, 'Vehicle_condition'].max()
        col3.metric('Melhor Condição Veículo', df_better)
    with col4:
        df_worse = df.loc[:, 'Vehicle_condition'].min()
        col4.metric('Pior condição Veículo', df_worse)
        
    st.markdown("""______""")
        
    st.container()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('Avaliação Média por entregador')
        avg_entregador = df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index()
        st.dataframe(avg_entregador)
        
    with col2:
        st.markdown('###### Avaliação média e desvio Padrão por tipo de tráfego')
        df = avg_std_traffic(df) # chamando a função
        
        
        st.markdown('###### Avaliação média e desvio Padrão por condição climática')
        df = avg_std_weatherconditions(df) #Chamando a função
        

        
    st.markdown("""______""")
    
    st.container()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('###### Top 10 entregadores mais lentos por cidade')
        df_concat = top_delivery(df, top_asc=False) # Chamando a função
        
    with col2:
        st.markdown('###### Top 10 entregadores mais rápidos por cidade')
        df_concat = top_delivery(df, top_asc=True) #Chamando a função
        
        