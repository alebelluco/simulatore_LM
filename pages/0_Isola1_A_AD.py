import streamlit as st
import simpy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly_express as px
import math
from des import des

st.set_page_config(page_title="Isola 1 AD", layout='wide')
my_cmap = plt.get_cmap("Reds")
st.title("Isola 1 A")
st.subheader(':red[Linea AD]', divider='grey')

layout_input = ['Isola','Macchina','Particolare','Cat_dati','Subcat_dati','Dato','Valore','Note']

tab_input, tab_risultati, tab_gantt = st.tabs(['Input','Risultati','Gantt'])

st.sidebar.header("Isola 1 A AD")
with tab_input:

    env = simpy.Environment()
    operatore1 = simpy.PriorityResource(env, capacity=1)
    operatore2 = simpy.PriorityResource(env, capacity=1)

    #if st.sidebar.toggle('Marcatrice disabbinata (marca tutto il possibile)'):
    #    raw_partenza = st.sidebar.number_input('Inserire WIP da marcare', step=1)
    #else:
    #   raw_partenza = 0

    raw = st.sidebar.number_input('Inserire la quantità da intestare', step=1)

    wip = {'raw':raw, 'raw2':150,'intestato':10000, 'finito':0 } # lavoro sul wip per fermare la intestatrice


    # Caricamento dati----------------------------------------------------------------------
    
    path = st.sidebar.file_uploader('Caricare il file di input')
    if not path:
        st.stop()
    db = pd.read_excel(path, 'input')
    db_utensili = pd.read_excel(path, 'db_utensili')

    isole = ['1AD']
    db = db[[any(isola in isoladb for isola in isole) for isoladb in db['Isola'].astype(str)]]
    db['Particolare'] = db['Particolare'].astype(str)

    db['key'] = db['Isola']+db['Macchina']+db['Particolare'].astype(str)+db['Versione'].astype(str)
    chiavi = []

    # SELEZIONE CODICI

    sx1, cx1, dx1 = st.columns([1,1,1])
    
    with sx1:
        codici_1 = db[(db.Macchina == 'DMG1')].Particolare.unique()
        codici_1 = np.append(codici_1, 'Macchina Spenta')
        pn1 = st.selectbox("Selezionare il codice per DMG1", options=codici_1)
        versioni1 = db[(db.Particolare == pn1) & (db.Macchina == 'DMG1')].Versione.astype(str).unique()
        ver1 = versioni1[0]
        if len(versioni1) != 1:
            st.warning('È presente più di una versione di ciclo')
            ver1 = st.selectbox('Selezionare la versione desiderata', options=versioni1, key=1)
        chiavi.append(f'1ADDMG1{pn1}{ver1}')

    with cx1: 
        codici_2 = db[(db.Macchina == 'DMG2') ].Particolare.unique()
        pn2 = st.selectbox("Selezionare il codice per DMG2", options=codici_2)
        versioni2 = db[(db.Particolare == pn2) & (db.Macchina == 'DMG2')].Versione.astype(str).unique()
        ver2 = versioni2[0]
        if len(versioni2) != 1:
            st.warning('È presente più di una versione di ciclo')
            ver2 = st.selectbox('Selezionare la versione desiderata', options=versioni2, key=2)
        chiavi.append(f'1ADDMG2{pn2}{ver2}')

    with dx1:   
        codici_3 = db[(db.Macchina == 'DMG3') ].Particolare.unique()
        pn3 = st.selectbox("Selezionare il codice per DMG3", options=codici_3)
        versioni3 = db[(db.Particolare == pn3) & (db.Macchina == 'DMG3')].Versione.astype(str).unique()
        ver3 = versioni3[0]
        if len(versioni3) != 1:
            st.warning('È presente più di una versione di ciclo')
            ver3 = st.selectbox('Selezionare la versione desiderata', options=versioni3, key=3)
        chiavi.append(f'1ADDMG3{pn3}{ver3}')

    sx2, cx2, dx2, dxx2 = st.columns([1,1,1,1])

    with sx2:
        codici_5 = db[(db.Macchina == 'Caorle')].Particolare.unique()
        pn5 = st.selectbox("Selezionare il codice per Caorle", options=codici_5)
        try:
            versioni5 = db[(db.Particolare == pn5) & (db.Macchina == 'Caorle')].Versione.astype(str).unique()
            ver5 = versioni5[0]
            if len(versioni5) != 1:
                st.warning('È presente più di una versione di ciclo')
                ver5 = st.selectbox('Selezionare la versione desiderata', options=versioni5, key=5)
        except:
            ver5=None
        chiavi.append(f'1ADCaorle{pn5}{ver5}')

    db_filtrato = db[[any(chiave in check for chiave in chiavi) for check in db.key]]
 

# VISUALIZZAZIONE DATI ======================================================================

    st.subheader('Dataframe configurazione', divider='red')
    
    def highlight(s):
        if s.Dato=='tempo_ciclo':
            return ['background-color: #700008']*len(s)
        
        elif s.Cat_dati=='cq':
            return ['background-color: #26272F']*len(s)
        else:
            return ['background-color: #0E1116']*len(s)

    for isola in isole:
        db_f = db_filtrato[db_filtrato.Isola == isola]
        st.subheader(f'Isola {isola}', divider='grey')
        st.dataframe(db_f[layout_input].style.apply(highlight, axis=1),width=2500)


    db_utensili['totale'] = db_utensili['sostituzione'] + db_utensili['con_corr']


 #CREAZIONE DIZIONARIO DELLE MACCHINE

    macchine = []
    n=0
    for mac in db_filtrato.Macchina.unique():
        db_lavoro = db_filtrato[db_filtrato.Macchina == mac]   
        d1=des.upload(db_lavoro)[0]
        d2=des.upload(db_lavoro)[1]
        d3=des.upload(db_lavoro)[2]
        d4=des.upload(db_lavoro)[3]

        elemento={
            'Nome':mac,
            'Generale':d1,
            'Cq':d2,
            'Other':d3,
            'Turno':d4,
            'Particolare':db_lavoro['Particolare'].iloc[0]
            }
        
        macchine.append(elemento)

    # creazione istanza della classe Machine
    machines = []
    k=0
    for mac in macchine:
            isola, part_in, part_out, name_machine, part,tempo_ciclo, cs, batch, cond, c_ut,freq_eq, t_eq, list_controlli, list_turno, durata_cor, periodo_cor, op_corr,durata_SAP, periodo_SAP, op_sap,durata_part_in, periodo_part_in, op_in,durata_part_out, periodo_part_out, op_out, robot_zeiss, robot_btw = des.carica_info_macchina(mac, db_utensili)
            macchina = des.Machine_wip(env,
                            wip,
                            part_in, 
                            part_out,
                            name_machine,
                            part,
                            tempo_ciclo,
                            cs,
                            batch,
                            cond,
                            c_ut,
                            k*10, freq_eq, t_eq, 
                            operatore1,operatore2,
                            0, list_controlli[0][0], list_controlli[0][1], list_controlli[0][2],
                            k,list_controlli[1][0], list_controlli[1][1], list_controlli[1][2],
                            k,list_controlli[2][0], list_controlli[2][1], list_controlli[2][2],
                            k,list_controlli[3][0], list_controlli[3][1], list_controlli[3][2],
                            k,list_controlli[4][0], list_controlli[4][1], list_controlli[4][2],
                            k,list_turno[0][0], list_turno[0][1],
                            k*4, list_turno[1][0], list_turno[1][1],
                            k*4, list_turno[2][0], list_turno[2][1],
                            durata_cor, periodo_cor, op_corr,
                            durata_SAP, periodo_SAP, op_sap,
                            durata_part_in, periodo_part_in, op_in,
                            durata_part_out, periodo_part_out, op_out)
        
            machines.append(macchina)

    if t_eq != 0:
                st.write("Il cambio utensile sulla macchina {} dell'isola {} richiede {:0.2f} minuti ogni {} pezzi".format(name_machine,isola,t_eq,freq_eq))
    k+=1        

    #---------------------------------------------------------------------------------------

prodotti_finiti = st.sidebar.number_input('Macchine con output proodotto finito', step=1)

with tab_risultati:

    st.subheader('Simulazione', divider='red')

    turni = st.number_input('Digitare la durata della simulazione [turni]',step=1)

    if not turni:
        st.stop()
    st.divider()

    if turni != 0:
        stop=turni*440
        env.run(until=stop)

        sx_sat, dx_sat = st.columns([1,3])

        with sx_sat:

            for macchina in machines:
                #st.write('Macchina: {} | Codice: {} | Output per turno: {:0.0f} | Ta_isola5: {:0.2f} | Ta_isola4: {:0.2f} '.format(macchina.name, macchina.part, macchina.parts_made/turni, (turni*450)/macchina.parts_made/(3), (turni*450)/macchina.parts_made/(2)))
                st.write(':red[Macchina: {}]'.format(macchina.name))
                st.write('Codice: _{}_   | Output per turno: :red[{:0.0f}] | Ta:{:0.2f} '.format(macchina.part, macchina.parts_made/turni, 450/(macchina.parts_made/turni)/prodotti_finiti))#-------------

        with dx_sat:
            st.subheader('Gantt')
            placeholder = st.empty()

        saturazione_1 = 0
        saturazione_2 = 0

#*** saturazione operatore
        

        for machine in machines:
            
            try:
                saturazione_1 += machine.link[machine.link_op['operatore1']][0]/(4.5*turni)
        
            except:
                saturazione_1 += 0        
            try:
                saturazione_2 += machine.link[machine.link_op['operatore2']][0]/(4.5*turni)
            except:
                saturazione_2 += 0

        st.divider()

        st.subheader('Saturazione OP1: {:0.2f}%'.format(saturazione_1))
        
        if saturazione_2 != 0:
            st.subheader('Saturazione OP2: {:0.2f}%'.format(saturazione_2))

        st.divider()

# Costruzione dataframe per Gantt-------------------------------------------------------------------------------------------------------------------------------------------


    incluso = ['Controllo','controllo','CONTROLLO',
            'Trasporto','trasporto','TRASPORTO',
            #'Correzione','correzione','CORREZIONE',
            'Prelievo','prelievo','PRELIEVO',
            'Sap','SAP','sap']

    escluso = ['Pronto','pronto','PRONTO',
            'Correzione','correzione','CORREZIONE',
            ]

    filtro_fine = ['Fine','fine','FINE']

    # ciclo su n macchine-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    log_macchine = []
    log_operatori = []

    prog = 1
    for macchina in machines:
        frame = pd.DataFrame([item.split("|", 3) for item in macchina.log])
        frame = frame.rename(columns={0:"Minuto",1:"Macchina",2:"Descrizione", 3:"Part"})   
        frame.Minuto = frame.Minuto.astype(float)

        # macchine

        frame_prod = frame[(frame['Descrizione'] == ' Inizio carico-scarico ') | (frame['Descrizione'] == ' Avvio macchina ') | (frame['Descrizione'] == ' Fine ciclo ')]
        frame_prod['Durata'] = frame_prod.Minuto.shift(-1) - frame_prod.Minuto
        frame_prod = frame_prod.replace({' Inizio carico-scarico ':'Carico-Scarico', ' Avvio macchina ':'Machining', ' Fine ciclo ':'Attesa operatore'})
        frame_prod['C{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Carico-Scarico',frame_prod.Durata,0)
        frame_prod['M{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Machining',frame_prod.Durata,0)
        frame_prod['A{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Attesa operatore',frame_prod.Durata,0)

        # operatori
        try:
            frame_op = frame[[(any(check in desc for check in incluso) and (all(check not in desc for check in escluso))) for desc in frame.Descrizione]]
            frame_op['Durata'] = frame_op.Minuto.shift(-1) - frame_op.Minuto
            frame_op = frame_op[[(all(check not in desc for check in filtro_fine)) for desc in frame_op.Descrizione]]
            frame_op['Descrizione'] = frame_op['Descrizione'].str[8:]
            frame_op['Macchina'] = macchina.name
            frame_op['operatore1'] = np.where(frame_op.Part == ' operatore1', frame_op.Durata, 0)
            frame_op['operatore2'] = np.where(frame_op.Part == ' operatore2', frame_op.Durata, 0)
            frame_op['Label'] = frame_op.Macchina + " | " + frame_op.Descrizione 
            
            log_operatori.append(frame_op)

        except:
            pass
        
        log_macchine.append(frame_prod)
        
        prog += 1

    #st.write(log_operatori)

with tab_gantt:
# costruzione Gantt macchine
    
    tempo = st.slider('Impostare intervallo gantt', 0, stop,(0, 100))
    st.divider()
    intervallo = tempo[1] - tempo[0]
    gantt_op = pd.concat([logs for logs in log_operatori] )
    gantt_macchine = pd.concat([logs for logs in log_macchine])

    # qui deve essere filtrato il dataframe in base alla scelta
    
    gantt_macchine = gantt_macchine[(gantt_macchine.Minuto > tempo[0]) & (gantt_macchine.Minuto < tempo[1]) ]
    gantt_macchine = gantt_macchine.reset_index(drop=True)
    gantt_op = gantt_op[(gantt_op.Minuto > tempo[0]) & (gantt_op.Minuto < tempo[1]) ]
    gantt_op = gantt_op.sort_values(by=['Part','Minuto'])    

    unique = gantt_macchine.Macchina.unique()

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(20,5))
    y_pos = np.arange(0,len(gantt_macchine), step=1)

    for i in range(len(unique)):
        
        colonna = f'M{i+1}' 
        #ax.barh(i*2, gantt_macchine.Minuto, color='black')
        #ax.barh(y_pos, gantt_macchine[colonna], left=gantt_macchine.Minuto, color=my_cmap(60*i))  
        ax.barh(i*2, gantt_macchine[colonna], left=gantt_macchine.Minuto, color=my_cmap(60*i))  
        ax.text(tempo[0]-15, i*2+0.1, unique[i], fontsize=12, color=my_cmap(60*i))

    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.grid('on', linewidth=0.2)
    ax.tick_params(right=False, left=False, axis='y', color='r', length=16,grid_color='none')
    ax.tick_params(axis='x', color='black', length=4, direction='in', width=4,labelcolor='w', grid_color='grey',labelsize=10)
    ax.tick_params(axis='y', color='black', length=4, direction='in', width=4,labelcolor='w')
    plt.xticks(np.arange(tempo[0],tempo[1],step=(intervallo/10)))
    plt.yticks(np.arange(0,len(unique)*2 ,step=100))
    plt.xlim(tempo[0]-20,tempo[1]+20)

    # costruzione Gantt operatori

    fig2, ax2 = plt.subplots(figsize=(20,7))
    y_pos2 = np.arange(0,len(gantt_op), step=1)
    operatori = ['operatore1','operatore2']
    colori = {'operatore1': 'w', 'operatore2': 'red'}

    for operatore in operatori:
        ax2.barh(y_pos2, gantt_op.Minuto, color='black')
        ax2.barh(y_pos2, gantt_op[operatore], left=gantt_op.Minuto, color=colori[operatore])

    gantt_op['x_pos'] = gantt_op['Minuto'] + gantt_op['Durata'] + 1
    for i in range(len(gantt_op)):
        x_pos = gantt_op.x_pos.iloc[i]
        ax2.text(x_pos, i, gantt_op.Label.iloc[i], fontsize=10, fontname='Avenir')#backgroundcolor='black')

    ax2.text(tempo[0]-15, 2, 'Operatore1', fontsize=12)
    ax2.text(tempo[0]-15, len(gantt_op)/2 + 2, 'Operatore2', color='red', fontsize=12)

    ax2.invert_yaxis()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(True)
    ax2.grid('on', linewidth=0.2)
    ax2.tick_params(right=False, left=False, axis='y', color='r', length=16,grid_color='none')
    ax2.tick_params(axis='x', color='black', length=4, direction='in', width=4,labelcolor='w', grid_color='grey',labelsize=10)
    ax2.tick_params(axis='y', color='black', length=4, direction='in', width=4,labelcolor='w')
    plt.xticks(np.arange(tempo[0],tempo[1],step=(intervallo/10)))
    plt.yticks(np.arange(0,len(gantt_op),step=20))
    plt.xlim(tempo[0]-20,tempo[1]+20)

    st.subheader('Gantt macchine')
    st.pyplot(fig)
    with placeholder:
        st.pyplot(fig)

    st.subheader('Gantt operatori')
    st.pyplot(fig2)
    
