import streamlit as st

st.set_page_config(
    page_title="DES",
    layout='wide'
)

st.sidebar.write("*Versione 1.0 | 18-04-2024*")

if st.sidebar.toggle('Più info'):
    st.sidebar.write(
        '''
:red[*Il tool di simulazione permette di calcolare:*]

- Output per turno da ogni macchina
- Tempo assegnato
- Saturazione operatori

:red[*Nella tab "Gantt" è visibile:*]

- Gantt collassato dei macchinari
- Gantt operatori

'''
    )

# HEADER---------------------------------------------------------------
sx,  cx, dx = st.columns([8,4,1])
with sx:
    st.title("Discrete Event Simulator")
    st.subheader(':red[Lavorazioni meccaniche]')
    
with dx:
    st.image('https://github.com/alebelluco/DES_AB/blob/main/Immagini_DES/Ducati_red_logo.png?raw=True')


if st.sidebar.toggle('Istruzioni'):
    with st.expander('Istruzioni generali'):
        st.write("Spiegazione utilizzo base dell'app")
    with st.expander('Preparazione file di input'):

        st.subheader('Esempio di compilazione file di input', divider ='red')

        st.write('Info macchina + attività in frequenza')
        
        st.image('https://github.com/alebelluco/DES_AB/blob/main/Immagini_DES/Ciclo_frequenza.png?raw=True')

        st.write('Tabella utensili')

        st.image('https://github.com/alebelluco/DES_AB/blob/main/Immagini_DES/Tab_utensili.png?raw=True')

    
    with st.expander('Impostazione parametri simulazione'):
        st.write('Argomento2')
    
    with st.expander('Lettura risultati'):
        st.write('Argomento3')

elif st.sidebar.toggle('Elenco modifiche'):
    st.write('09/05/2024 | Isola3AD | Inserita possibilità di scegliere se disabbinare la marcatrice')
    st.write('16/05/2024 | Isola2AD | Aggiunta visibilità del carico - scarico delle macchine sul gantt | la modifica impatta package des, Class Machine_isola2 ')
    st.write('28/05/2024 | Isola2AD | Corretto bug cambio utensile: le macchine dispari (1,3) avevano un offset che faceva partire il contatore da i*10 (non multiplo del batch = mai count_cu)')
    st.write('29/11/2024 | Isola1AD - Isola1AM - Isola  4-5 AM | caricamento dati da database unico, con scelta in APP ')
else:
    st.divider()
    sx1, cx1 = st.columns([1,8])
    with cx1:
        st.image('https://github.com/alebelluco/DES_AB/blob/main/Immagini_DES/des_lm.png?raw=True', width=1200)




