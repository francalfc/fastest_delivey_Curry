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

def order_by_day(df):
    """
        Esta função irá plotar o gráfico de barra das colunas ID e Order_Date
    """
    df_aux = df.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig

def traffic_order_share(df):
    """
        Esta função irá plotar o gráfico de pizza da colunas ID e Road_Traffic_density
    """
    df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    fig = px.pie(df_aux, values='ID', names='Road_traffic_density')
    return fig

def order_volume_city_traffic(df): 
    """
        Esta função irá plotar o gráfico de Scatter das colunas City e Road_traffic e volume será pela coluna ID
    """
    df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    fig= px.scatter(df_aux, x='City', y='Road_traffic_density',size='ID', color='City')
    st.plotly_chart(fig, use_container_width=True)           
    return fig

def order_by_week(df):
    """
        Esta função irá plotar o gráfico de linha das colunas Week_of_year e ID
    """
    df_aux = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID', title='Quantidade de pedidos por semana')
    st.plotly_chart(fig, use_container_width=True)
    return fig

def delivery_per_week (df):
    """
        Esta função irá plotar o gráfico de linha das colunas week_of_year e order_by_week
    """
    df_aux1 = df.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux2 = df.loc[:,['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
    #Juntando as duas tabelas
    df_aux = pd.merge(df_aux1,df_aux2, how='inner')
    df_aux['order_by_week'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_year', y='order_by_week')
    st.plotly_chart(fig, use_container_width=True)
    return fig

def country_maps(df):
    """
        Esta função irá plotar o mapa das localidades dos restaurantes
    """
    df_aux = (df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                    .groupby(['City', 'Road_traffic_density'])).median().reset_index()

    map = folium.Map(zoom_start=1100)

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                       location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)

    folium_static(map, width=1024, height=600)
    return map


#--------------------------------------------------------------------------------
#---------------------------------Início do código lógico------------------------
st.set_page_config(page_title='Company_view', page_icon=':bird:', layout='wide', initial_sidebar_state='collapsed')
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

#=============================================================================
#         BARRA LATERAL
#=============================================================================
st.header('Marketplace - Visão Cliente')
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
st.sidebar.markdown('### Powered by Comnunidade DS')

#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df['Road_traffic_density'] .isin(traffic_option)
df = df.loc[linhas_selecionadas, :]

#=======================================================================
#  LAYOUT DO DASHBOARD
#=======================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    #Criando o container
    with st.container():
        # Order Metric
        st.header('Order by Day')
        fig = order_by_day(df) # Chamando a função
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.header ('Traffic Orde Share')
            fig = traffic_order_share(df) # Chamando a função
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header ('Comparison of order volume by city and type of traffic')
            fig = order_volume_city_traffic(df) # Chamando a função
with tab2:
    st.header('Order by Week')
    fig = order_by_week(df) # Chamando a função
    
    st.header('number of orders per delivery person per week')
    fig = delivery_per_week(df) # Chamando a função
    
    
    
with tab3:
    st.header('Country Maps')
    map = country_maps(df) # Chamando a função
    