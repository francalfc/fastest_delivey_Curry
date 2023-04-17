import streamlit as st
from PIL import Image


st.set_page_config(page_title='Home', page_icon=':bird:', layout='wide', initial_sidebar_state='collapsed')
image = Image.open('logo.png')
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Ifast Fodd Delivery')
st.sidebar.markdown('___')

st.write('# Curry Company Growth Dashboard')

st.markdown( 
    """
    Growth Dashobar foi construido para acompanhar as médias de crescimento dos Entregadore e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa
        - Visão Gerencial: Métricas gerais de comportamento
        - Visão tática: Indicadores semanais de crescimento
        - Visão geográfica: Insight de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores de semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @leonardo
    """)
