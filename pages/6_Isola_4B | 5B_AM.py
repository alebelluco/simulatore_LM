import streamlit as st
import simpy
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly_express as px
import math
from des import des
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# IMPOSTAZIONI PAGINA
# ============================================================================================================================== | Impostazioni pagina
st.set_page_config(page_title="Isola 1 AM", layout='wide')
my_cmap = plt.get_cmap("Reds")


sx_title, dx_title = st.columns([15,1])

with sx_title:
    st.title("Isole 4B - 5B AM")
    st.subheader(':red[Linea AM]', divider='grey')

with dx_title:
    st.image('https://github.com/alebelluco/DES_AB/blob/main/Immagini_DES/Ducati_red_logo.png?raw=True')


tab_input, tab_risultati, tab_gantt = st.tabs(['Input','Risultati','Gantt'])

# CARICAMENTO DATI
# ============================================================================================================================== | Caricamento dati e inizializzazione
st.sidebar.header("Isola 4B - 5B AM")
layout_input = ['Isola','Macchina','Particolare','Cat_dati','Subcat_dati','Dato','Valore','Note']

with tab_input:

    env = simpy.Environment()
    operatore1 = simpy.PriorityResource(env, capacity=1)
    operatore2 = simpy.PriorityResource(env, capacity=1)

    wip = {'raw':100000, 'lavorato_Grobe':1, 'lavorato_Tornio':1, 'lavorato_Fresatrice':1, 'Finito':0 } 

    path = st.sidebar.file_uploader('Caricare il file di input')
    if not path:
        st.stop()
    db = pd.read_excel(path, 'input')
    db_utensili = pd.read_excel(path, 'db_utensili')

    n_codici_zeiss = st.sidebar.number_input('N° codici in seconda rettifica', step=1)

#-- subset del database : lo filtro sull isola
    isole = ['4BAM','5BAM']
    db = db[[any(isola in isoladb for isola in isole) for isoladb in db['Isola'].astype(str)]]
    db['Particolare'] = db['Particolare'].astype(str)

    db['key'] = db['Isola']+db['Macchina']+db['Particolare'].astype(str)+db['Versione'].astype(str)
    chiavi = []

    # ISOLA 4B ================================================================================= ISOLA 4B

    st.subheader('Isola 4B', divider='grey')
    st.subheader(':red[Junker]')

    sx1, cx1, dx1, dxx1 = st.columns([1,1,1,1])
    
    with sx1:
        codici_1 = db[(db.Isola == '4BAM') & (db.Macchina == 'Junker1') ].Particolare.unique()
        pn1 = st.selectbox("Selezionare il codice per Junker1", options=codici_1)
        chiavi.append(f'4BAMJunker1{pn1}')
    with cx1: 
        codici_2 = db[(db.Isola == '4BAM') & (db.Macchina == 'Junker2') ].Particolare.unique()
        pn2 = st.selectbox("Selezionare il codice per Junker2", options=codici_2)
        chiavi.append(f'4BAMJunker2{pn2}')
    with dx1:   
            codici_5 = db[(db.Isola == '4BAM') & (db.Macchina == 'Junker3') ].Particolare.unique()
            pn5 = st.selectbox("Selezionare il codice per Junker3", options=codici_5)
            chiavi.append(f'4BAMJunker3{pn5}')
    with dxx1:   
            codici_8 = list(db[(db.Isola == '4BAM') & (db.Macchina == 'Junker4') ].Particolare.unique())
            codici_8.append("Non pianificata")
            pn8 = st.selectbox("Selezionare il codice per Junker4", options=codici_8)
            if pn8 != "Non pianificata":
                chiavi.append(f'4BAMJunker4{pn8}')

    st.divider()
    st.subheader(':red[Cemb4 + Lasit1]')

    sx2, cx2, dx2, dxx2 = st.columns([1,1,1,1])

    with sx2:
        codici_3 = db[(db.Isola == '4BAM') & (db.Macchina == 'Cemb4') ].Particolare.unique()
        pn3 = st.selectbox("Selezionare il codice per Cemb4", options=codici_3)
        chiavi.append(f'4BAMCemb4{pn3}')

    with cx2:
        codici_4 = db[(db.Isola == '4BAM') & (db.Macchina == 'Lasit1') ].Particolare.unique()
        pn4 = st.selectbox("Selezionare il codice per Lasit1", options=codici_4)
        chiavi.append(f'4BAMLasit1{pn4}')

    st.divider()
    st.subheader(':red[Cemb5 + Lasit2]')
    sx3, cx3, dx3, dxx3 = st.columns([1,1,1,1])

    with sx3:   
        codici_6 = db[(db.Isola == '4BAM') & (db.Macchina == 'Cemb5') ].Particolare.unique()
        pn6 = st.selectbox("Selezionare il codice per Cemb5", options=codici_6)
        chiavi.append(f'4BAMJunker3{pn6}')

    with cx3:         
        codici_7 = db[(db.Isola == '4BAM') & (db.Macchina == 'Lasit2') ].Particolare.unique()
        pn7 = st.selectbox("Selezionare il codice per Lasit2", options=codici_7)
        chiavi.append(f'4BAMLasit2{pn7}')


    db_work1 = db[[any(chiave in check for chiave in chiavi) for check in db.key]]

    chiavi2 = []
    # ISOLA 5B ================================================================================= ISOLA 5B

    st.subheader('Isola 5B', divider='grey')
    st.subheader(':red[Isola di controllo finale Zeiss]')
    sx, cx, dx, dxx = st.columns([1,1,1,1])

    with sx:
        codici_88 = db[(db.Isola == '5BAM') & (db.Macchina == 'Zeiss') ].Particolare.unique()
        pn88 = st.selectbox("Selezionare il codice per Zeiss", options=codici_88)
        chiavi2.append(f'5BAMZeiss{pn88}')
    
    st.divider()

    db_work2 = db[[any(chiave in check for chiave in chiavi2) for check in db.key]]
    #db_work2 = db[(db['Isola']=='5BAM') & (db['Particolare']==pn)]


    # VISUALIZZAZIONE DATI ======================================================================

    db_filtrato = pd.concat([db_work1, db_work2])

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


    # CREAZIONE DIZIONARIO DELLE MACCHINE

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

    #st.write(macchine)

    machines = []
    k=0
    for mac in macchine:
        isola, part_in, part_out, name_machine, part,tempo_ciclo, cs, batch, cond, c_ut,freq_eq, t_eq, list_controlli, list_turno, durata_cor, periodo_cor, op_corr,durata_SAP, periodo_SAP, op_sap,durata_part_in, periodo_part_in, op_in,durata_part_out, periodo_part_out, op_out, robot_zeiss, robot_btw = des.carica_info_macchina(mac, db_utensili)
        if name_machine == 'Zeiss':
            macchina = des.Machine_isola_Zeiss(env,
                                name_machine,
                                part,
                                tempo_ciclo,
                                cs,
                                batch,
                                cond,
                                c_ut,
                                k*10, freq_eq, t_eq, 
                                operatore1 ,operatore2,
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
                                durata_part_out, periodo_part_out, op_out,
                                n_codici_zeiss)

            machines.append(macchina)

        else:  
            macchina = des.Machine_isola5AM(env,
                                name_machine,
                                part,
                                tempo_ciclo,
                                cs,
                                batch,
                                cond,
                                c_ut,
                                k*10, freq_eq, t_eq, 
                                operatore1 ,operatore2,
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
    
prodotti_finiti = st.sidebar.number_input('Macchine con output proodotto finito', step=1)
n_operatori = st.sidebar.number_input('Operatori', step=1)

with tab_risultati:

    st.subheader('Simulazione', divider='red')

    turni = st.number_input('Digitare la durata della simulazione [turni]',step=1)

    if not turni:
        st.stop()
    st.divider()

    if turni != 0:
        stop=turni*440
        try:
            env.run(until=stop)
        except Exception as e:
            st.write(e)

        for macchina in machines:
            #st.write('Macchina: {} | Codice: {} | Output per turno: {:0.0f} | Ta_isola5: {:0.2f} | Ta_isola4: {:0.2f} '.format(macchina.name, macchina.part, macchina.parts_made/turni, (turni*450)/macchina.parts_made/(3), (turni*450)/macchina.parts_made/(2)))
            st.write(':red[Macchina: {}]'.format(macchina.name))
            st.write('Codice: _{}_   | Output per turno: :red[{:0.0f}] | Ta:{:0.2f} '.format(macchina.part, macchina.parts_made/turni, n_operatori*450/(macchina.parts_made/turni)/prodotti_finiti))#-------------

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

    incluso = [
        'Controllo',
        'controllo',
        'CONTROLLO',
        'Trasporto',
        'trasporto',
        'TRASPORTO',
        'Prelievo',
        'prelievo',
        'PRELIEVO',
        'Sap',
        'SAP',
        'sap']

    incluso_cs = [
        'carico',
        'Avvio'
        ]
    #incluso_cs = []
    incluso_cu = [
        'utensile'
        ]

    escluso = [
            'Pronto',
            'pronto',
            'PRONTO',
            'Correzione',
            'correzione',
            'CORREZIONE'
            ]

    filtro_fine = ['Fine','fine','FINE']

    # ciclo su n macchine-----------------------------------------------------------------------------------------------------------------------------------------------------------------

    log_macchine = []
    log_operatori = []

    prog = 1
    for macchinario in machines:
        frame = pd.DataFrame([item.split("|", 3) for item in macchinario.log])
        frame = frame.rename(columns={0:"Minuto",1:"Macchina",2:"Descrizione", 3:"Part"})   
        frame.Minuto = frame.Minuto.astype(float)

        # macchine

        frame_prod = frame[(frame['Descrizione'] == ' Inizio carico-scarico ') | (frame['Descrizione'] == ' Avvio macchina ') | (frame['Descrizione'] == ' Fine ciclo ')]
        frame_prod['Durata'] = frame_prod.Minuto.shift(-1) - frame_prod.Minuto
        frame_prod = frame_prod[frame_prod.Descrizione !=' start ']
        frame_prod = frame_prod[frame_prod.Descrizione !=' end ']

        frame_prod = frame_prod.replace({' Inizio carico-scarico ':'Carico-Scarico', ' Avvio macchina ':'Machining', ' Fine ciclo ':'Attesa operatore'})
        frame_prod['C{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Carico-Scarico',frame_prod.Durata,0)
        frame_prod['M{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Machining',frame_prod.Durata,0)
        frame_prod['A{}'.format(prog)] = np.where(frame_prod['Descrizione']=='Attesa operatore',frame_prod.Durata,0)
        log_macchine.append(frame_prod)

        # operatori
        #st.write('frame',frame)
        try:
            frame_op = frame[[(any(check in desc for check in incluso) and (all(check not in desc for check in escluso))) for desc in frame.Descrizione]]
            frame_op['Durata'] = frame_op.Minuto.shift(-1) - frame_op.Minuto
            frame_op = frame_op[[(all(check not in desc for check in filtro_fine)) for desc in frame_op.Descrizione]]
            frame_op['Descrizione'] = frame_op['Descrizione'].str[8:]
            frame_op['Macchina'] = macchinario.name
            frame_op['operatore1'] = np.where(frame_op.Part == ' operatore1', frame_op.Durata, 0)
            frame_op['operatore2'] = np.where(frame_op.Part == ' operatore2', frame_op.Durata, 0)
            frame_op['Label'] = frame_op.Macchina + " | " + frame_op.Descrizione 
            log_operatori.append(frame_op)
            
        except:
            pass
        
         # carico-scarico
        try:
            frame_cs = frame[[(any(check in desc for check in incluso_cs) and (all(check not in desc for check in escluso))) for desc in frame.Descrizione]]
            frame_cs['Durata'] = frame_cs.Minuto.shift(-1) - frame_cs.Minuto
            
            frame_cs = frame_cs[[(all(check not in desc for check in filtro_fine)) for desc in frame_cs.Descrizione]]
            frame_cs['Descrizione'] = frame_cs['Descrizione'].str[8:]
            frame_cs['Macchina'] = macchinario.name
            
            frame_cs['operatore1'] = np.where(frame_cs.Part == ' operatore1', frame_cs.Durata, 0)
            frame_cs['operatore2'] = np.where(frame_cs.Part == ' operatore2', frame_cs.Durata, 0)
            frame_cs['Label'] = frame_cs.Macchina + " | " + frame_cs.Descrizione 
            frame_cs = frame_cs[(frame_cs.operatore1!=0)|(frame_cs.operatore2!=0)]

            log_operatori.append(frame_cs)

        except Exception  as e:
            #st.write(e)
            pass
        
    
        # cambio utensile
        try:
            frame_cu = frame[[(any(check in desc for check in incluso_cu) and (all(check not in desc for check in escluso))) for desc in frame.Descrizione]]
            frame_cu['Durata'] = frame_cu.Minuto.shift(-1) - frame_cu.Minuto
            #frame_cu = frame_cs[[(all(check not in desc for check in filtro_fine)) for desc in frame_cs.Descrizione]]

            frame_cu['Descrizione'] = 'Cambio_utensile'
            frame_cu['Macchina'] = macchinario.name
            
            frame_cu['operatore1'] = np.where(frame_cu.Part == ' operatore1', frame_cu.Durata, 0)
            frame_cu['operatore2'] = np.where(frame_cu.Part == ' operatore2', frame_cu.Durata, 0)
            frame_cu['Label'] = frame_cu.Macchina + " | " + frame_cu.Descrizione 
            frame_cu = frame_cu[(frame_cu.operatore1!=0)|(frame_cu.operatore2!=0)]
            log_operatori.append(frame_cu)

        except Exception  as e:
            st.write(e)

        prog += 1
    #st.write(machines[0].log)
    #st.write(log_operatori)
    #st.write(frame_prod)
    #st.write(log_operatori)

with tab_gantt:
# costruzione Gantt macchine
    
    tempo = st.slider('Impostare intervallo gantt', 0, stop,(0, 100))
    st.divider()
    intervallo = tempo[1] - tempo[0]
    gantt_op = pd.concat([logs for logs in log_operatori] )
    gantt_op = gantt_op[gantt_op.Durata != 0] #per togliere righe dummy
    gantt_macchine = pd.concat([logs for logs in log_macchine])

# stampe di controllo

# --------------------------------------------

    # qui deve essere filtrato il dataframe in base alla scelta
    gantt_macchine = gantt_macchine[(gantt_macchine.Minuto >= tempo[0]) & (gantt_macchine.Minuto <= tempo[1]) ]
    gantt_macchine = gantt_macchine.reset_index(drop=True)
    gantt_op = gantt_op[(gantt_op.Minuto > tempo[0]) & (gantt_op.Minuto < tempo[1]) ]
    gantt_op = gantt_op.sort_values(by=['Part','Minuto'])    
    unique = gantt_macchine.Macchina.unique()


    test_gantt = gantt_macchine[gantt_macchine.Descrizione == 'Machining']
    nomi_macchine = [macchina['Nome'] for macchina in macchine]
    dict_color = {}

    for i in range(len(nomi_macchine)):
        dict_color[nomi_macchine[i]]=str(my_cmap((i+1)*30))

    selected = st.multiselect('Selezionare macchine | nessuna macchina selezionata = Tutte le macchine', options=nomi_macchine)
    if selected == []:
        selected = nomi_macchine

    test_gantt['Macchina'] = [macchina.replace(' ','') for macchina in test_gantt.Macchina]
    test_gantt = test_gantt[[any(macc in check for macc in selected) for check in test_gantt.Macchina]]
    fig3 = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,  # condividi l'asse X
    vertical_spacing=0.05,
    row_heights=[0.98, 0.02] 
   )

    fig3.add_trace(
        go.Bar(
            y=test_gantt['Macchina'],
            x=test_gantt['Durata'],
            base=test_gantt['Minuto'],
            orientation='h',
            #marker_color = [('rgba' + dict_color[macc]) for macc in test_gantt.Macchina]
            marker_color='pink'
        )
    )
    fig3.update_yaxes(autorange="reversed")
    fig3.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor='gray')


    colori = {'operatore1': 'rgba'+ str(my_cmap(20)), 'operatore2': 'rgba'+str(my_cmap(60))}
    g_op = gantt_op.copy().reset_index()
    g_op['Part']=[op.replace(' ','') for op in g_op.Part]
    #g_op = g_op[[any(macc in check for macc in selected) for check in g_op.Macchina]]
    #g_op

    fig4 = go.Figure()

    fig3.add_trace(
        go.Bar(
            y=g_op.index,
            x=g_op['Durata'],
            base=g_op['Minuto'],
            orientation='h',
            marker_color = [colori[op] for op in g_op.Part],
            text=g_op.Label
            
        )
    )
    fig3.update_yaxes(autorange="reversed")
    fig3.update_xaxes(showgrid=True, gridwidth=0.2, gridcolor='gray', showticklabels=True)
    fig3.update_layout(
        height=1500
    )

    st.plotly_chart(fig3)
    st.divider()
    st.subheader('Dettaglio attività operatori')
    st.dataframe(gantt_op.drop(columns=['operatore1','operatore2','Label']).rename(columns={'Part':'Operatore'}))

