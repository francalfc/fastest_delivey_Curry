# ================================================================
# Bibliotecas
# =================================================================
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
    
    '''
        Essa função é responsável por fazer a limpeza dos dados
        1 - Irá remover as colunas que tem os espaços
        2 - Irá apagar as linhas que tem os valor nulos (NaN)
        3 - Conversão de algumas coluanas categóricas para numericas
        4 -  Criação de uma nova coluna ['distance'] que mostra a distância média do restaurante para o cliente
    '''   
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
    return df

def avg_std_time_taken (df):
    df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure() 
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time']))) 
    fig.update_layout(autosize=True, barmode='group')
    st.plotly_chart( fig )
    return fig

def avg_std_city_road_traffic(df):
    df_aux = (df.loc[:, ['Time_taken(min)', 'City','Road_traffic_density' ]].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['mean_time', 'std_time']
    st.dataframe(df_aux)
    return df_aux

def avg_std_city_traffic_graph (df):
    df_aux = ( df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .agg( {'Time_taken(min)': ['mean', 'std']} ) )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                                  color='std_time', color_continuous_scale='RdBu',
                                  color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                                  color='std_time', color_continuous_scale='RdBu',
                                  color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    st.plotly_chart(fig)
    return fig

def avg_distance_city(df):
    avg_distance = df.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()
    fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
    st.plotly_chart(fig)
    return fig
#---------------------------------Início do código lógico------------------------
st.set_page_config(page_title='Company_view', page_icon=':food:', layout='wide', initial_sidebar_state='collapsed')
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


#=============================================
#  Barra lateral
#=============================================

image = Image.open('logo.png')
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Ifast Fodd Delivery')
st.sidebar.markdown('___')
st.sidebar.header('Select deadline date')
date_slider = st.sidebar.slider('select the date', value=pd.datetime(2022, 4 ,13), format=('DD/MM/YYYY'),
                    min_value=pd.datetime(2022, 2, 11), max_value=pd.datetime(2022, 4, 6))
st.sidebar.markdown('___')
multiselect = st.sidebar.multiselect('what conditions of transit',['Low', 'Medium', 'High', 'Jam'], 
                       default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown('___')
traffic_option = st.sidebar.multiselect('What Weather Condition', ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
                                                                  'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
                                       default=['conditions Sunny', 'conditions Stormy'])
st.sidebar.markdown('___')
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtro de data
linha_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linha_selecionadas, :]

#Filtro do trânsito
linhas_selecionadas = df['Road_traffic_density'].isin(multiselect)
df = df.loc[linhas_selecionadas, :]

#Filtro condição climática
linhas_selecionadas = df['Weatherconditions'].isin(traffic_option)
df = df.loc[linhas_selecionadas, :]


#=============================================
#  Layout Dashboard
#=============================================

st.header('Restaurant View')
tab1, tab2, tab3 = st.tabs(['Overview', '-', '-'])

with tab1: 
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            df_unico = len (df['Delivery_person_ID'].unique())
            st.metric('QTD. Entregadores', df_unico)
        with col2:
            distance = np.round (df['distance'].mean(),2)
            st.metric('Distancia Média', distance)
        with col3:
            df_aux = df.loc[df['Festival'] == 'Yes', ['Time_taken(min)', 'Festival']].groupby('Festival').mean().reset_index()
            temp_mean = np.round (df_aux.iloc[0,1], 2)
            st.metric('Tempo médio c/Festival', temp_mean)
        with col4:
            df_aux = df.loc[df['Festival'] == 'Yes', ['Time_taken(min)', 'Festival']].groupby('Festival').std().reset_index()
            temp_std = np.round (df_aux.iloc[0,1], 2)
            st.metric('Desvio Padrão c/ Festival', temp_std)
        with col5:
            df_aux = df.loc[df['Festival'] == 'No', ['Time_taken(min)', 'Festival']].groupby('Festival').mean().reset_index()
            temp_med = np.round (df_aux.iloc[0,1], 2)
            st.metric('Tempo médio s/ Festival', temp_med)
        with col6:
            df_aux = df.loc[df['Festival'] == 'No', ['Time_taken(min)', 'Festival']].groupby('Festival').std().reset_index()
            temp_med = np.round (df_aux.iloc[0,1], 2)
            st.metric('Desvio Padrão s/ Festival', temp_med)
    st.markdown('___')
    
    with st.container():
        col1, col2 = st.columns((2,1))
        with col1:
            st.markdown('col1')
            fig = avg_std_time_taken(df) #Chamando a função
            
        with col2:
            st.markdown('col2')
            df_aux = avg_std_city_road_traffic(df) # Chamando a função
           
        st.markdown('___')
    
    with st.container():
        col1, col2 = st.columns((2,2))
        with col1:
            st.markdown('col1')
            fig = avg_std_city_traffic_graph(df) # Chamando a função
            
        with col2:
            st.markdown('col2')
            fig = avg_distance_city(df)
            
