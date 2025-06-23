# Aggiornato 23/06/2024
# Class machine isola 2: per visualizzare sul gantt il carico-scarico è stato aggiunto l'operatore a log_macchina sull'inizio caricamento nella funzionee working
# Controlli turno multipli su isola 4-5 AM



import pandas as pd
import simpy
import math
import streamlit as st

def CQ(macchina, env, operatore, tcq, nome):
    while True:
        macchina.log.append('{:0.1f} | {} | Pezzo pronto per {}'.format(env.now, macchina.name, nome ))          
        yield env.timeout(0.1) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tcq) 
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now-tcq, macchina.name, nome, op ))
            macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now, macchina.name, nome, op ))
            
            macchina.link[operatore][0] += tcq

            #op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log_op.append('{:0.1f}_{} | cq_macchina {} | + {} minuti'.format(env.now,op, macchina.name, tcq ))
            macchina.sat.append(tcq)             
        break   

def CQ_T(macchina, env, operatore, tcq, offset, nome): #a differenza del controllo a frequenza, qui l'offset ritarda il controllo per non farlo cadere per forza ad inizio turno
    while True:
        macchina.log.append('{:0.1f} | {} | Pezzo pronto per {}'.format(env.now, macchina.name, nome ))          
        yield env.timeout(offset) # ritardo a partire da cambio turno
        macchina.link[operatore][0] += tcq
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tcq)
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now-tcq, macchina.name, nome, op ))
            #st.write('{:0.1f} | {} | Inizio {}'.format(env.now-tcq, macchina.name, nome ))
            #st.write(macchina.sat_op)
            macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now, macchina.name, nome, op ))
            
            macchina.link[operatore][0] += tcq
            #st.write(macchina.sat_op)                       
        break   

def CQ_T_macchina_funzionante(macchina, env, operatore, tcq, offset, nome): #a differenza del controllo a frequenza, qui l'offset ritarda il controllo per non farlo cadere per forza ad inizio turno
    while True:
        macchina.log.append('{:0.1f} | {} | Pezzo pronto per {}'.format(env.now, macchina.name, nome ))          
        yield env.timeout(offset) # ritardo a partire da cambio turno
        macchina.link[operatore][0] += tcq
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            # Qui c'è la modifica che simula il controllo a macchina funzionante: carica ugualmente la saturazione ma non ferma la macchina
            yield env.timeout(0)
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now, macchina.name, nome, op ))
            #st.write('{:0.1f} | {} | Inizio {}'.format(env.now-tcq, macchina.name, nome ))
            #st.write(macchina.sat_op)
            macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now + tcq, macchina.name, nome, op ))
            
            macchina.link[operatore][0] += tcq
            #st.write(macchina.sat_op)                       
        break   

def CQ_cassetto(macchina, env, operatore,robot, tcq, nome, tempo_robot):
    while True:
        macchina.log.append('{:0.1f} | {} | Pezzo pronto per {}'.format(env.now, macchina.name, nome ))          
        yield env.timeout(0.1) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with robot.request(priority=1) as req:
            yield req
            ripartenza = False
            with operatore.request(priority=1)as req1:
                yield req1 # blocco la risorsa
                #yield req
                #yield env.timeout(1)

                yield env.timeout(tempo_robot)
                robot.release(req)

                robot =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(robot)]
                macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now-tempo_robot, macchina.name, nome, robot ))
                macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now, macchina.name, nome, robot ))

                yield env.timeout(tcq)
                
                op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
                
                macchina.log.append('{:0.1f} | {} | Inizio {} | {}'.format(env.now-tcq-tempo_robot, macchina.name, nome, op ))
                macchina.log.append('{:0.1f} | {} | Fine {} | {}'.format(env.now, macchina.name, nome, op ))

                
                
                macchina.link[operatore][0] += tcq

                #op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
                macchina.log_op.append('{:0.1f}_{} | cq_macchina {} | + {} minuti'.format(env.now,op, macchina.name, tcq ))
                macchina.sat.append(tcq)             
        break   

def Correzione(macchina, env, operatore, tc_corr):
    while True:               
        yield env.timeout(0) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=1) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tc_corr) 
            #print('{} | correzione fatta'.format(env.now))
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-tc_corr, macchina.name, op))
            macchina.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, macchina.name, op))
            
            macchina.link[operatore][0] += tc_corr
        
        break

def Other(macchina, env, operatore, tc, attività):
    while True:               
        yield env.timeout(0) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tc) 
            op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            macchina.log.append('{:0.1f} | {} | inizio {} | {}'.format(env.now-tc, macchina.name, attività, op))
            macchina.log.append('{:0.1f} | {} | fine {} | {}'.format(env.now, macchina.name, attività, op))
            
            macchina.link[operatore][0] += tc
        break   

def upload(df):

    '''
    Output:
    [0] = dic_gen \n
    [1] = dic_cq \n
    [2] = dic_other \n
    [3]= dic_turno
    '''

    isola = df['Isola'].iloc[0]
    info = df[df.Cat_dati == 'generale']
    dic_gen = dict(zip(info.Dato,info.Valore))
    dic_gen['isola']=isola
    cq = df[df.Cat_dati=='cq']

    '''
 
    dic_cq = {}
    for controllo in cq.Subcat_dati.unique():
        subdf = df[df.Subcat_dati == controllo]
        periodo = subdf[subdf.Dato=='periodo'].Valore.iloc[0]
        durata = subdf[subdf.Dato=='durata'].Valore.iloc[0]
        op = subdf[subdf.Dato=='op'].Valore.iloc[0]
        dic_cq[controllo]={'periodo':periodo,'durata':durata,'op':op}   
'''
    dic_cq = {}
    n=0
    for controllo in cq.Subcat_dati.unique():
        subdf = df[df.Subcat_dati == controllo]
        periodo = subdf[subdf.Dato=='periodo'].Valore.iloc[0]
        durata = subdf[subdf.Dato=='durata'].Valore.iloc[0]
        op = subdf[subdf.Dato=='op'].Valore.iloc[0]
        if controllo == 'controllo_zeiss':
            try:
                durata_robot = subdf[subdf.Dato=='durata_robot'].Valore.iloc[0]
                dic_cq[n]={'task':controllo,'periodo':periodo,'durata':durata,'op':op,'durata_robot':durata_robot}
            except:
                st.warning("Attenzione: nel database manca il dato sulla durata dell'operazione del robot di deposito del pezzo nel cassetto")
                st.stop()              
            #st.write(durata_robot)
            
        else:
        #dic_cq[controllo]={'periodo':periodo,'durata':durata,'op':op}
            dic_cq[n]={'task':controllo,'periodo':periodo,'durata':durata,'op':op}
        n+=1
    other = df[df.Cat_dati=='other']
    dic_other = {}
    for oth in other.Subcat_dati.unique():
        subdf = df[df.Subcat_dati == oth]
        periodo = subdf[subdf.Dato=='periodo'].Valore.iloc[0]
        durata = subdf[subdf.Dato=='durata'].Valore.iloc[0]
        op = subdf[subdf.Dato=='op'].Valore.iloc[0]
        dic_other[oth]={'periodo':periodo,'durata':durata,'op':op}
        n+=1
    
    turno = df[df.Cat_dati=='turno']
    dic_turno  = {}
    n=0
    for t in turno.Subcat_dati.unique():
        subdf = df[df.Subcat_dati == t]
        durata = subdf[subdf.Dato=='durata'].Valore.iloc[0]
        op = subdf[subdf.Dato=='op'].Valore.iloc[0]
        dic_turno[n]={'task':t,'durata':durata,'op':op}
        n+=1


    return dic_gen, dic_cq, dic_other, dic_turno

def att_robot(macchina, env, operatore, tempo):
    while True:               
        yield env.timeout(0) #ritardo la chiamata in moodo da far prima caricare la macchina, il ritardo deve essere >= al tempo di carico scarico
        with operatore.request(priority=2) as req: 
            yield req # blocco la risorsa
            yield env.timeout(tempo) 

            # Ad ora non viene visualizzato niente sul gantt, nè sulla saturazione 


            #op =  list(macchina.link_op.keys())[list(macchina.link_op.values()).index(operatore)]
            #macchina.log.append('{:0.1f} | {} | inizio {} | {}'.format(env.now-tc, macchina.name, attività, op))
            #macchina.log.append('{:0.1f} | {} | fine {} | {}'.format(env.now, macchina.name, attività, op))
            
            #macchina.link[operatore][0] += tc
        break   

class Machine(object):
    
    def __init__(self, env, name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,                               
                ):
        
        self.env = env
        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'operatore1':operatore1,
                      'operatore2':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        self.op_cambio_ut = self.link_op[op_cambio_ut]

        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None

        self.op_sap  = self.link_op[op_sap]
        self.op_in = self.link_op[op_in]
        self.op_out = self.link_op[op_out]

        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []


    def working(self): 
        while True:           
            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs+0.11)  # x2 perchè lo spostamento dura uguale ----------------------modifica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico'.format(self.env.now-self.cs, self.name))  
                    self.link[self.op_conduttore][0] += self.cs + 0.11 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now,op, self.name, self.cs ))
                    self.sat.append(self.cs)

                
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += self.batch 

            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq1, self.tempo_ciclo_cq1, 'controllo qualità_1'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if self.turno_now > self.turno:
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                #self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                if self.count_utensile == self.periodo_cu:    
                    with self.op_cambio_ut.request(priority=1) as req: 
                        yield req # blocco la risorsa
                        yield self.env.timeout(self.t_cambio_ut)
                        self.log.append('{:0.1f}  | {} | pezzo °{} | Inizio cambio utensile'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile))
                        self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                        self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                    self.count_utensile = 0

class Machine_isola_2(object):

    # chiama la funzione CQ_T_macchina_funzionante anzichè CQ_T

    def __init__(self, env, name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,                               
                ):
        
        self.env = env
        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'operatore1':operatore1,
                      'operatore2':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        try:
            self.op_cambio_ut = self.link_op[op_cambio_ut]
        except:
            self.op_cambio_ut = None


        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None
        #----------------------------------------------------
        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None
        #----------------------------------------------------
        try:
            self.op_in = self.link_op[op_in]
            self.op_out = self.link_op[op_out]
        except:
            self.op_in = None
            self.op_out = None


        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []


    def working(self): 
        while True:           
            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs+0.11)  # x2 perchè lo spostamento dura uguale ----------------------modifica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs + 0.11 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now,op, self.name, self.cs))
                    self.sat.append(self.cs)

                
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += self.batch 


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq1, self.tempo_ciclo_cq1, 'controllo qualità_Zeiss'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if self.turno_now > self.turno:
                self.env.process(CQ_T_macchina_funzionante(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                #self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                op_ut =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
                if self.count_utensile == self.periodo_cu:    
                    with self.op_cambio_ut.request(priority=1) as req: 
                        yield req # blocco la risorsa
                        yield self.env.timeout(self.t_cambio_ut)
                        self.log.append('{:0.1f}  | {} | Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name,op_ut))
                        self.log.append('{:0.1f}  | {} | Fine cambio utensile | {}'.format(self.env.now, self.name,op_ut))   
                        self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                    self.count_utensile = 0

class Machine_wip(object):
    # Isola 3AD
    # Non presente la parte sul controllo 1 a turno

    def __init__(self, env,
                 # ------------ argomenti che differenziano Machine_wip da Machine
                 # Questa configurazione serve quando si hanno macchine in serie con wip intermedio
                 wip,
                 part_in,
                 part_out,
                 #-------------
                 name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,                               
                ):
        
        self.env = env

        self.wip = wip
        self.part_in = part_in
        self.part_out = part_out

        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'operatore1':operatore1,
                      'operatore2':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        self.op_cambio_ut = self.link_op[op_cambio_ut]

        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None

        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None

        self.op_in = self.link_op[op_in]

        try:
            self.op_out = self.link_op[op_out]
        except:
            self.op_out = None

        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []


    def working(self): 
        while True:
            while not self.wip[self.part_in] >= self.batch: # se non c'è WIP aspetto
                yield self.env.timeout(0.01)     

            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs+0.15)  # x2 perchè lo spostamento dura uguale ----------------------modifica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico'.format(self.env.now-self.cs-0.15, self.name))  
                    self.link[self.op_conduttore][0] += self.cs + 0.12 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now-0.15,op, self.name, self.cs ))
                    self.sat.append(self.cs)


                
            yield self.env.timeout(self.tc-0.15)  #lavoro un pezzo  

            self.parts_made += self.batch 

            self.wip[self.part_in] -= self.batch
            self.wip[self.part_out] += self.batch


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq1, self.tempo_ciclo_cq1, 'controllo qualità_1'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if (self.turno_now > self.turno) and (self.tempo_ct1):
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            if self.count_utensile == self.periodo_cu:
                if self.name == 'Tornio Boehringer': 
                    with (self.op_cambio_ut.request(priority=1) and self.op_conduttore.request(priority=0)) as req: # impegno uomo + macchina
                        yield req # blocco la risorsa
                        yield self.env.timeout(self.t_cambio_ut)
                        self.log.append('{:0.1f}  | {} | pezzo °{} | Inizio cambio utensile'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile))
                        self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                        self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                    self.count_utensile = 0
                else:
                    with self.op_cambio_ut.request(priority=1) as req: # impegno solamente l'uomo

                        yield req # blocco la risorsa
                        yield self.env.timeout(self.t_cambio_ut)
                        self.log.append('{:0.1f}  | {} | pezzo °{} | Inizio cambio utensile'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile))
                        self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                        self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                    self.count_utensile = 0

class Machine_robot(object):
    # Isola 3AD
    # Non presente la parte sul controllo 1 a turno

    def __init__(self, env,
                 # ------------ argomenti che differenziano Machine_wip da Machine
                 # Questa configurazione serve quando si hanno macchine in serie con wip intermedio
                 wip,
                 part_in,
                 part_out,
                 #-------------
                 name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,
                 robot_zeiss = None,
                 robot_btw = 0                               
                ):
        
        self.env = env

        self.wip = wip
        self.part_in = part_in
        self.part_out = part_out

        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'robot':operatore1,
                      'operatore1':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]

        try:
            self.op_cambio_ut = self.link_op[op_cambio_ut]
        except:
            self.op_cambio_ut = None

        try:
            self.op_cq1 = self.link_op[op_cq1]
        except:
            self.op_cq1 = None

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None
        #----------------------------------------------------
        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None
        #----------------------------------------------------
        try:
            self.op_in = self.link_op[op_in]
        except:
            self.op_in = None
        #----------------------------------------------------
        try:
            self.op_out = self.link_op[op_out]
        except:
            self.op_out = None


        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3
        try:
            self.robot_zeiss = robot_zeiss
        except:
            self.robot_zeiss = None


        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []

        self.robot_between = robot_btw


    def working(self): 
        while True:
            while not self.wip[self.part_in] >= self.batch: # se non c'è WIP aspetto
                yield self.env.timeout(0.01)     

            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs + self.robot_between)  #difica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs-self.robot_between, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs + 0.13 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now - self.robot_between,op, self.name, self.cs ))
                    self.sat.append(self.cs)

            #self.env.process(att_robot(self, self.env, self.op_conduttore, 30)) #NON VA BENE
                
            yield self.env.timeout(self.tc - self.robot_between)  #lavoro un pezzo  

            self.parts_made += self.batch 

            self.wip[self.part_in] -= self.batch
            self.wip[self.part_out] += self.batch


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch

            self.sap_count += self.batch  
            self.part_in_count += self.batch
            self.part_out_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            #self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc-self.robot_between, self.name,op)) 
            self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc, self.name,op)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ_cassetto(self, self.env, self.op_cq1,self.op_conduttore, self.tempo_ciclo_cq1, 'controllo qualità_1',self.robot_zeiss))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            if self.part_out_count==self.periodo_part_out:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Scambio interfalde'))
                self.part_out_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if (self.turno_now > self.turno) and (self.tempo_ct1):
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))

            op_cu =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                if self.count_utensile == self.periodo_cu:
                    if self.name == 'Tornio Boehringer': 
                        with self.op_cambio_ut.request(priority=1) as req: #and self.op_conduttore.request(priority=0)) as req: # impegno uomo + macchina
                            yield req # blocco la risorsa
                            with self.op_conduttore.request(priority=0) as req1:
                                yield req1
                                yield self.env.timeout(self.t_cambio_ut)

                                self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}' .format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile, op_cu))
                                #st.write('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {} ' .format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile, op_cu))
                                self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                                self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                            self.count_utensile = 0
                    else:
                        with self.op_cambio_ut.request(priority=1) as req: # impegno solamente l'uomo
                            yield req # blocco la risorsa
                            yield self.env.timeout(self.t_cambio_ut)
                            self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile,op_cu ))
                            self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                            self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                        self.count_utensile = 0

class Machine_robot_call(object): #la prima macchina che finisce chiama il robot, non c'è condizione di Wip
    # Isola 3AD
    # Non presente la parte sul controllo 1 a turno

    def __init__(self, env,
                 # ------------ argomenti che differenziano Machine_wip da Machine
                 # Questa configurazione serve quando si hanno macchine in serie con wip intermedio
                 
                 
                 #-------------
                 name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,
                 robot_zeiss = None,
                 robot_btw = 0                               
                ):
        
        self.env = env

        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'robot2':operatore1,
                      'operatore1':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]

        try:
            self.op_cambio_ut = self.link_op[op_cambio_ut]
        except:
            self.op_cambio_ut = None

        try:
            self.op_cq1 = self.link_op[op_cq1]
        except:
            self.op_cq1 = None

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None
        #----------------------------------------------------
        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None
        #----------------------------------------------------
        try:
            self.op_in = self.link_op[op_in]
        except:
            self.op_in = None
        #----------------------------------------------------
        try:
            self.op_out = self.link_op[op_out]
        except:
            self.op_out = None


        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3
        try:
            self.robot_zeiss = robot_zeiss
        except:
            self.robot_zeiss = None


        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []

        self.robot_between = robot_btw


    def working(self): 
        while True:
            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs + self.robot_between)  #difica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs-self.robot_between, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs + 0.13 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now - self.robot_between,op, self.name, self.cs ))
                    self.sat.append(self.cs)

            #self.env.process(att_robot(self, self.env, self.op_conduttore, 30)) #NON VA BENE
                
            yield self.env.timeout(self.tc - self.robot_between)  #lavoro un pezzo  

            self.parts_made += self.batch 


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch

            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            #self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc-self.robot_between, self.name,op)) 
            self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc, self.name,op)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ_cassetto(self, self.env, self.op_cq1,self.op_conduttore, self.tempo_ciclo_cq1, 'controllo qualità_1',self.robot_zeiss))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            if self.part_out_count==self.periodo_part_out:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Scambio interfalde'))
                self.part_out_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if (self.turno_now > self.turno) and (self.tempo_ct1):
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            op_cu =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                if self.count_utensile == self.periodo_cu:
                    if self.name == 'Tornio Boehringer': 
                        with (self.op_cambio_ut.request(priority=1) & self.op_conduttore.request(priority=0)) as req: # impegno uomo + macchina
                            yield req # blocco la risorsa
                            yield self.env.timeout(self.t_cambio_ut)
                            self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile,op_cu))
                            self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                            self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                        self.count_utensile = 0
                    else:
                        with self.op_cambio_ut.request(priority=1) as req: # impegno solamente l'uomo

                            yield req # blocco la risorsa
                            yield self.env.timeout(self.t_cambio_ut)
                            self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile, op_cu))
                            self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                            self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                        self.count_utensile = 0

class Machine_robot_call_singola(object): #la prima macchina che finisce chiama il robot, non c'è condizione di Wip
    # Isola 3AD
    # Non presente la parte sul controllo 1 a turno

    def __init__(self, env,
                 # ------------ argomenti che differenziano Machine_wip da Machine
                 # Questa configurazione serve quando si hanno macchine in serie con wip intermedio
                 
                 
                 #-------------
                 name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,
                 robot_zeiss = None,
                 robot_btw = 0                               
                ):
        
        self.env = env

        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'robot3':operatore1,
                      'operatore1':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]

        try:
            self.op_cambio_ut = self.link_op[op_cambio_ut]
        except:
            self.op_cambio_ut = None

        try:
            self.op_cq1 = self.link_op[op_cq1]
        except:
            self.op_cq1 = None

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None
        #----------------------------------------------------
        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None
        #----------------------------------------------------
        try:
            self.op_in = self.link_op[op_in]
        except:
            self.op_in = None
        #----------------------------------------------------
        try:
            self.op_out = self.link_op[op_out]
        except:
            self.op_out = None


        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3
        try:
            self.robot_zeiss = robot_zeiss
        except:
            self.robot_zeiss = None


        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []

        self.robot_between = robot_btw


    def working(self): 
        while True:
            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs + self.robot_between)  #difica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs-self.robot_between, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs + 0.13 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now - self.robot_between,op, self.name, self.cs ))
                    self.sat.append(self.cs)

            #self.env.process(att_robot(self, self.env, self.op_conduttore, 30)) #NON VA BENE
                
            yield self.env.timeout(self.tc - self.robot_between)  #lavoro un pezzo  

            self.parts_made += self.batch 


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch

            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            #self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc-self.robot_between, self.name,op)) 
            self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc, self.name,op)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ_cassetto(self, self.env, self.op_cq1,self.op_conduttore, self.tempo_ciclo_cq1, 'controllo qualità_1',self.robot_zeiss))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            if self.part_out_count==self.periodo_part_out:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Scambio interfalde'))
                self.part_out_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if (self.turno_now > self.turno) and (self.tempo_ct1):
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            op_cu =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                if self.count_utensile == self.periodo_cu:
                    if self.name == 'Tornio Boehringer': 
                        with (self.op_cambio_ut.request(priority=1) & self.op_conduttore.request(priority=0)) as req: # impegno uomo + macchina
                            yield req # blocco la risorsa
                            yield self.env.timeout(self.t_cambio_ut)
                            self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile,op_cu))
                            self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                            self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                        self.count_utensile = 0
                    else:
                        with self.op_cambio_ut.request(priority=1) as req: # impegno solamente l'uomo

                            yield req # blocco la risorsa
                            yield self.env.timeout(self.t_cambio_ut)
                            self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile, op_cu))
                            self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                            self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                        self.count_utensile = 0

class Machine_isola_Zeiss(object):

    # chiama la funzione CQ_T_macchina_funzionante anzichè CQ_T

    def __init__(self, env, name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,
                 n_codici = 0                               
                ):
        
        self.env = env
        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.n_codici = n_codici

        self.link_op={'operatore1':operatore1,
                      'operatore2':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        try:
            self.op_cambio_ut = self.link_op[op_cambio_ut]
        except:
            self.op_cambio_ut = None


        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None
        #----------------------------------------------------
        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None
        #----------------------------------------------------
        try:
            self.op_in = self.link_op[op_in]
            self.op_out = self.link_op[op_out]
        except:
            self.op_in = None
            self.op_out = None


        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []

    def working(self): 
        while True:
            adjustment = 0           
            with self.op_conduttore.request(priority=0) as req:
                    yield req
                    yield self.env.timeout(0)
                    yield self.env.timeout(self.cs)  # x2 perchè lo spostamento dura uguale ----------------------modifica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs + 0.11 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now,op, self.name, self.cs))
                    self.sat.append(self.cs)

                
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += self.batch 


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare
                #self.log.append('{:0.1f} | {} | start | {}'.format(self.env.now, self.name, op ))
                #yield self.env.timeout(self.tempo_ciclo_cq1)
                #adjustment = self.tempo_ciclo_cq1 #adjustment serve per mettere nel corretto ordine questa task ed inizio-fine del pezzo precedente
                #self.log.append('{:0.1f} | {} | end | {}'.format(self.env.now, self.name, op ))
                self.env.process(CQ_T(self, self.env, self.op_cq1, self.tempo_ciclo_cq1,0, 'controllo qualità_Zeiss'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if self.turno_now > self.turno:
                #self.env.process(CQ_T_macchina_funzionante(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.log.append('{:0.1f} | {} | start | {}'.format(self.env.now, self.name, op ))
                yield self.env.timeout(self.tempo_ct1 * self.n_codici) #self.n_codici è il numero di codici lavorati in isola che passano x la zeiss (n°seconde rettifiche x la isola 5AM)
                adjustment = self.tempo_ct1 * self.n_codici #adjustment serve per mettere nel corretto ordine questa task ed inizio-fine del pezzo precedente
                self.log.append('{:0.1f} | {} | end | {}'.format(self.env.now, self.name, op ))
                
                self.turno = self.turno_now 
                #self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now-adjustment, self.name, self.parts_made))
            
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                op_ut =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
                if self.count_utensile == self.periodo_cu:
                    try:    
                        with self.op_cambio_ut.request(priority=1) as req: 
                            yield req # blocco la risorsa
                            yield self.env.timeout(self.t_cambio_ut)
                            self.log.append('{:0.1f}  | {} | Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name,op_ut))
                            self.log.append('{:0.1f}  | {} | Fine cambio utensile | {}'.format(self.env.now, self.name,op_ut))   
                            self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                        self.count_utensile = 0
                    except:
                        st.write('Cambio utensile zeiss')
                        st.stop()
class Machine_isola_Zeiss2(object):

    # chiama la funzione CQ_T_macchina_funzionante anzichè CQ_T

    def __init__(self, env, name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,
                 n_codici = 0                               
                ):
        
        self.env = env
        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.n_codici = n_codici

        self.link_op={'operatore1':operatore1,
                      'operatore2':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        try:
            self.op_cambio_ut = self.link_op[op_cambio_ut]
        except:
            self.op_cambio_ut = None


        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None
        #----------------------------------------------------
        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None
        #----------------------------------------------------
        try:
            self.op_in = self.link_op[op_in]
            self.op_out = self.link_op[op_out]
        except:
            self.op_in = None
            self.op_out = None


        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []

    def working(self): 
        while True:
            adjustment = 0           
            with self.op_conduttore.request(priority=0) as req:
                    yield req
                    yield self.env.timeout(0)
                    #yield self.env.timeout(self.cs+0.11)  # x2 perchè lo spostamento dura uguale ----------------------modifica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    #self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs  #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    
                    #self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now,op, self.name, self.cs))
                    self.sat.append(self.cs)

                
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += self.batch 


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare
                #self.log.append('{:0.1f} | {} | start | {}'.format(self.env.now, self.name, op ))
                #yield self.env.timeout(self.tempo_ciclo_cq1)
                #adjustment = self.tempo_ciclo_cq1 #adjustment serve per mettere nel corretto ordine questa task ed inizio-fine del pezzo precedente
                #self.log.append('{:0.1f} | {} | end | {}'.format(self.env.now, self.name, op ))
                self.env.process(CQ_T(self, self.env, self.op_cq1, self.tempo_ciclo_cq1,0, 'controllo qualità_Zeiss'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if self.turno_now > self.turno:
                #self.env.process(CQ_T_macchina_funzionante(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.log.append('{:0.1f} | {} | start | {}'.format(self.env.now, self.name, op ))
                yield self.env.timeout(self.tempo_ct1 * self.n_codici) #self.n_codici è il numero di codici lavorati in isola che passano x la zeiss (n°seconde rettifiche x la isola 5AM)
                adjustment = self.tempo_ct1 * self.n_codici #adjustment serve per mettere nel corretto ordine questa task ed inizio-fine del pezzo precedente
                self.log.append('{:0.1f} | {} | end | {}'.format(self.env.now, self.name, op ))
                
                self.turno = self.turno_now 
                #self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now-adjustment, self.name, self.parts_made))
            
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                op_ut =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
                if self.count_utensile == self.periodo_cu:
                    try:    
                        with self.op_cambio_ut.request(priority=1) as req: 
                            yield req # blocco la risorsa
                            yield self.env.timeout(self.t_cambio_ut)
                            self.log.append('{:0.1f}  | {} | Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name,op_ut))
                            self.log.append('{:0.1f}  | {} | Fine cambio utensile | {}'.format(self.env.now, self.name,op_ut))   
                            self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                        self.count_utensile = 0
                    except:
                        st.write('Cambio utensile zeiss')
                        st.stop()


class Machine_robot_Zeiss3AM(object):
    # Isola 3AD
    # Non presente la parte sul controllo 1 a turno

    def __init__(self, env,
                 # ------------ argomenti che differenziano Machine_wip da Machine
                 # Questa configurazione serve quando si hanno macchine in serie con wip intermedio
                 wip,
                 part_in,
                 part_out,
                 #-------------
                 name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,
                 robot_zeiss = None,
                 robot_btw = 0                               
                ):
        
        self.env = env

        self.wip = wip
        self.part_in = part_in
        self.part_out = part_out

        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'robot':operatore1,
                      'operatore1':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]

        try:
            self.op_cambio_ut = self.link_op[op_cambio_ut]
        except:
            self.op_cambio_ut = None

        try:
            self.op_cq1 = self.link_op[op_cq1]
        except:
            self.op_cq1 = None

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None
        #----------------------------------------------------
        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None
        #----------------------------------------------------
        try:
            self.op_in = self.link_op[op_in]
        except:
            self.op_in = None
        #----------------------------------------------------
        try:
            self.op_out = self.link_op[op_out]
        except:
            self.op_out = None


        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3
        try:
            self.robot_zeiss = robot_zeiss
        except:
            self.robot_zeiss = None


        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []

        self.robot_between = robot_btw


    def working(self): 
        while True:
            while not self.wip[self.part_in] >= self.batch: # se non c'è WIP aspetto
                yield self.env.timeout(0.01)     

            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs + self.robot_between)  #difica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs-self.robot_between, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs + 0.13 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    self.log.append('{:0.1f} | {} | Fine carico-scarico | {}'.format(self.env.now-self.robot_between, self.name,op))  
                    #self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now - self.robot_between,op, self.name, self.cs ))
                    
                    self.sat.append(self.cs)

            #self.env.process(att_robot(self, self.env, self.op_conduttore, 30)) #NON VA BENE
                
            #yield self.env.timeout(self.tc - self.robot_between)  #lavoro un pezzo  
            yield self.env.timeout(self.tc)

            self.parts_made += self.batch 
            self.wip[self.part_in] -= self.batch
            self.wip[self.part_out] += self.batch

            #self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc-self.robot_between, self.name,op)) 
            self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc-self.robot_between, self.name,op)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))  



            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch

            self.sap_count += self.batch  
            self.part_in_count += self.batch
            self.part_out_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
   
            with self.op_conduttore.request(priority=0) as req:
                yield req                  
                yield self.env.timeout(30)  #difica: self.cs + self.spostamento (che non esiste ad oggi negli input)
   
                op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                self.log.append('{:0.1f} | {} | Inizio carico-scarico2 | {}'.format(self.env.now - 30, self.name,op))  
                self.link[self.op_conduttore][0] += self.cs + 0.13 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                #self.tempo += self.cs
                #self.log_op.append('{:0.1f} | saturazione  )
                
                #self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina2 {} | + {} minuti'.format(self.env.now,op, self.name, self.cs ))
                self.log.append('{:0.1f} | {} | Fine carico-scarico2 | {}'.format(self.env.now, self.name,op))  
                self.sat.append(self.cs)





            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ_cassetto(self, self.env, self.op_cq1,self.op_conduttore, self.tempo_ciclo_cq1, 'controllo qualità_1',self.robot_zeiss))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            if self.part_out_count==self.periodo_part_out:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Scambio interfalde'))
                self.part_out_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if (self.turno_now > self.turno) and (self.tempo_ct1):
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            #self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))

            op_cu =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                if self.count_utensile == self.periodo_cu:
                    if self.name == 'Tornio Boehringer': 
                        with self.op_cambio_ut.request(priority=1) as req: #and self.op_conduttore.request(priority=0)) as req: # impegno uomo + macchina
                            yield req # blocco la risorsa
                            with self.op_conduttore.request(priority=0) as req1:
                                yield req1
                                yield self.env.timeout(self.t_cambio_ut)

                                self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}' .format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile, op_cu))
                                #st.write('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {} ' .format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile, op_cu))
                                self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                                self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                            self.count_utensile = 0
                    else:
                        with self.op_cambio_ut.request(priority=1) as req: # impegno solamente l'uomo
                            yield req # blocco la risorsa
                            yield self.env.timeout(self.t_cambio_ut)
                            self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile,op_cu ))
                            self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                            self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                        self.count_utensile = 0

class Machine_robot_3AM(object):
    # Isola 3AD
    # Non presente la parte sul controllo 1 a turno

    def __init__(self, env,
                 # ------------ argomenti che differenziano Machine_wip da Machine
                 # Questa configurazione serve quando si hanno macchine in serie con wip intermedio
                 wip,
                 part_in,
                 part_out,
                 #-------------
                 name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None,
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None,
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None,
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None,
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, # controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None,
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None,
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,
                 robot_zeiss = None,
                 robot_btw = 0                               
                ):
        
        self.env = env

        self.wip = wip
        self.part_in = part_in
        self.part_out = part_out

        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'robot':operatore1,
                      'operatore1':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]

        try:
            self.op_cambio_ut = self.link_op[op_cambio_ut]
        except:
            self.op_cambio_ut = None

        try:
            self.op_cq1 = self.link_op[op_cq1]
        except:
            self.op_cq1 = None

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]
        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None
        #----------------------------------------------------
        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None
        #----------------------------------------------------
        try:
            self.op_in = self.link_op[op_in]
        except:
            self.op_in = None
        #----------------------------------------------------
        try:
            self.op_out = self.link_op[op_out]
        except:
            self.op_out = None


        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3
        try:
            self.robot_zeiss = robot_zeiss
        except:
            self.robot_zeiss = None


        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []

        self.robot_between = robot_btw


    def working(self): 
        while True:
            while not self.wip[self.part_in] >= self.batch: # se non c'è WIP aspetto
                yield self.env.timeout(0.01)     

            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs + self.robot_between)  #difica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs-self.robot_between, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs + 0.13 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now - self.robot_between,op, self.name, self.cs ))
                    self.sat.append(self.cs)

            #self.env.process(att_robot(self, self.env, self.op_conduttore, 30)) #NON VA BENE
                
            yield self.env.timeout(self.tc - self.robot_between)  #lavoro un pezzo  

            self.parts_made += self.batch 

            self.wip[self.part_in] -= self.batch
            self.wip[self.part_out] += self.batch*0.1


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch

            self.sap_count += self.batch  
            self.part_in_count += self.batch
            self.part_out_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            #self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc-self.robot_between, self.name,op)) 
            self.log.append('{:0.1f} | {} | Avvio macchina | {} '.format(self.env.now-self.tc, self.name,op)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ_cassetto(self, self.env, self.op_cq1,self.op_conduttore, self.tempo_ciclo_cq1, 'controllo qualità_1',self.robot_zeiss))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            if self.part_out_count==self.periodo_part_out:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Scambio interfalde'))
                self.part_out_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if (self.turno_now > self.turno) and (self.tempo_ct1):
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                self.turno = self.turno_now 
                self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))

            op_cu =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                if self.count_utensile == self.periodo_cu:
                    if self.name == 'Tornio Boehringer': 
                        with self.op_cambio_ut.request(priority=1) as req: #and self.op_conduttore.request(priority=0)) as req: # impegno uomo + macchina
                            yield req # blocco la risorsa
                            with self.op_conduttore.request(priority=0) as req1:
                                yield req1
                                yield self.env.timeout(self.t_cambio_ut)

                                self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}' .format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile, op_cu))
                                #st.write('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {} ' .format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile, op_cu))
                                self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                                self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                            self.count_utensile = 0
                    else:
                        with self.op_cambio_ut.request(priority=1) as req: # impegno solamente l'uomo
                            yield req # blocco la risorsa
                            yield self.env.timeout(self.t_cambio_ut)
                            self.log.append('{:0.1f}  | {} | pezzo °{} - Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name, self.count_utensile,op_cu ))
                            self.log.append('{:0.1f}  | {} | Fine cambio utensile'.format(self.env.now, self.name))   
                            self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                        self.count_utensile = 0




class Machine_isola5AM(object):

    # chiama la funzione CQ_T_macchina_funzionante anzichè CQ_T

    def __init__(self, env, name,  part, tempo_ciclo, carico_scarico, #wip, part_in, part_out,
                 batch, 
                 op_conduttore,
                 op_cambio_ut,
                 off_cu, periodo_cu, t_cambio_ut, 
                 operatore1, operatore2,
                 offset_cq1 = 0, periodo_cq1 = 0, tempo_ciclo_cq1 = 0, op_cq1=None, name_cq1 = 'CF1', # controlli a frequenza
                 offset_cq2 = 0, periodo_cq2= 0, tempo_ciclo_cq2 = 0, op_cq2=None, name_cq2 = 'CF2',
                 offset_cq3 = 0, periodo_cq3 = 0, tempo_ciclo_cq3 = 0, op_cq3=None, name_cq3 = 'CF3',
                 offset_cq4 = 0, periodo_cq4 = 0, tempo_ciclo_cq4 = 0, op_cq4=None, name_cq4 = 'CF4',
                 offset_cq5 = 0, periodo_cq5 = 0, tempo_ciclo_cq5 = 0, op_cq5=None, name_cq5 = 'CF5',
                 offset_ct1 = 0, tempo_ct1 = 0, op_ct1=None, name_ct1 = 'CT1',# controlli 1/turno
                 offset_ct2 = 0, tempo_ct2 = 0, op_ct2=None, name_ct2 = 'CT2',
                 offset_ct3 = 0, tempo_ct3 = 0, op_ct3=None, name_ct3 = 'CT3',
                 tc_corr = 0, periodo_corr=0, op_corr=None,
                 tc_SAP = 0, periodo_SAP = 0, op_sap=None,
                 tc_part_in = 0, periodo_part_in = 0, op_in = None,
                 tc_part_out = 0, periodo_part_out = 0, op_out = None,                               
                ):
        
        self.env = env
        self.name = name
        self.part = part
        self.tc = tempo_ciclo
        self.cs = carico_scarico
        self.batch = batch
        self.off_cu = off_cu

        self.link_op={'operatore1':operatore1,
                      'operatore2':operatore2
                      }

        #operatori 
        self.op_conduttore = self.link_op[op_conduttore]
        try:
            self.op_cambio_ut = self.link_op[op_cambio_ut]
        except:
            self.op_cambio_ut = None


        self.op_cq1 = self.link_op[op_cq1]

        try:
            self.op_cq2 = self.link_op[op_cq2]
        except:
            self.op_cq2 = None
        #----------------------------------------------------
        try:
            self.op_cq3 = self.link_op[op_cq3]
        except:
            self.op_cq3 = None
        #----------------------------------------------------
        try:
            self.op_cq4 = self.link_op[op_cq4]
        except:
            self.op_cq4 = None
        #----------------------------------------------------    
        try:
            self.op_cq5 = self.link_op[op_cq5]
        except:
            self.op_cq5 = None
        #----------------------------------------------------
        try:
            self.op_ct1 =  self.link_op[op_ct1]
            #st.write('op ct1')
            #st.write(self.op_ct1)
            #st.write(self.link_op[op_ct1])
        except:
            self.op_ct1 = None
        #----------------------------------------------------      
        try:
            self.op_ct2 =  self.link_op[op_ct2]

        except:
            self.op_ct2 = None
        #----------------------------------------------------
        try:
            self.op_ct3 =  self.link_op[op_ct3]
        except:
            self.op_ct3 = None
        #----------------------------------------------------
        try:
            self.op_corr = self.link_op[op_corr]
        except:
            self.op_corr = None
        #----------------------------------------------------
        try:
            self.op_sap  = self.link_op[op_sap]
        except:
            self.op_sap  = None
        #----------------------------------------------------
        try:
            self.op_in = self.link_op[op_in]
            self.op_out = self.link_op[op_out]
        except:
            self.op_in = None
            self.op_out = None


        #saturazioni-----------------------------------------

        self.sat_op_conduttore = [0]
        self.sat_op_cambio_ut = [0]

        self.sat_op_cq1 = [0]
        self.sat_op_cq2 = [0]
        self.sat_op_cq3 = [0]
        self.sat_op_cq4 = [0]
        self.sat_op_cq5 = [0]

        self.sat_op_ct1 = [0]
        self.sat_op_ct2 = [0]
        self.sat_op_ct3 = [0]

        self.sat_op_corr = [0]
        self.sat_op_sap =  [0]
        self.sat_op_in = [0]
        self.sat_op_out = [0]

        # legami operatore - saturazione
        
        self.link = {self.op_conduttore : [0],
                self.op_cambio_ut : [0],
                self.op_cq1 : [0],
                self.op_cq2 : [0],
                self.op_cq3 : [0],
                self.op_cq4 : [0],
                self.op_cq5 : [0],
                self.op_ct1 : [0],
                self.op_ct2 : [0],
                self.op_ct3 : [0],
                self.op_corr : [0],
                self.op_sap : [0],
                self.op_in : [0],
                self.op_out : [0]}

        #tempi ciclo

        self.tc_corr = tc_corr
        self.periodo_corr = periodo_corr
        
        self.t_cambio_ut = t_cambio_ut
        self.periodo_cu = periodo_cu
        self.count_utensile = 0 + off_cu

        self.offset_ct1 = offset_ct1 # questi 3 offset servono per ritardare a piacere il contrllo 1T 
        self.offset_ct2 = offset_ct2 # e non farlo per forza al cambio turno
        self.offset_ct3 = offset_ct3

            
        self.log = []
        self.attese = []
        self.attesa_tot = 0
        self.pezzo_finito = 0
                       
        self.qc_count1 = 0 + offset_cq1
        self.qc_count2 = 0 + offset_cq2
        self.qc_count3 = 0 + offset_cq3
        self.qc_count4 = 0 + offset_cq4
        self.qc_count5 = 0 + offset_cq5

        
        self.sap_count = 4 # sfalsato
        self.part_in_count = 8 #sfalsato
        self.part_out_count = 8 #sfalsato
        
        self.corr_count = -1
        
        self.periodo_cq1 = periodo_cq1
        self.periodo_cq2 = periodo_cq2
        self.periodo_cq3 = periodo_cq3
        self.periodo_cq4 = periodo_cq4
        self.periodo_cq5 = periodo_cq5 # se non ho il controllo non viene mai incrementato il contatore e non si attiva mai la funzione

        self.name_cq1 = name_cq1
        self.name_cq2 = name_cq2
        self.name_cq3 = name_cq3
        self.name_cq4 = name_cq4
        self.name_cq5 = name_cq5

        self.name_ct1 = name_ct1
        self.name_ct2 = name_ct2
        self.name_ct3 = name_ct3

        self.periodo_SAP = periodo_SAP
        self.periodo_part_in = periodo_part_in
        self.periodo_part_out = periodo_part_out
                
        self.tempo_ciclo_cq1 = tempo_ciclo_cq1
        self.tempo_ciclo_cq2 = tempo_ciclo_cq2 
        self.tempo_ciclo_cq3 = tempo_ciclo_cq3
        self.tempo_ciclo_cq4 = tempo_ciclo_cq4 
        self.tempo_ciclo_cq5 = tempo_ciclo_cq5  
        self.tempo_ct1 = tempo_ct1
        self.tempo_ct2 = tempo_ct2
        self.tempo_ct3 = tempo_ct3

        self.tempo_ciclo_SAP = tc_SAP
        self.tc_part_in = tc_part_in
        self.tc_part_out = tc_part_out

        self.turno = 0  # il contatore turni serve per i controlli 1 a turno         
        self.turno_now = None

        #self.sat_op=0
        self.parts_made = 0        
        self.process = env.process(self.working()) #avvio l'istanza appena dopo averla creata
        
        self.log_op = []
        self.sat  = []


    def working(self): 
        while True:           
            with self.op_conduttore.request(priority=0) as req:
                    yield req                  
                    yield self.env.timeout(self.cs+0.11)  # x2 perchè lo spostamento dura uguale ----------------------modifica: self.cs + self.spostamento (che non esiste ad oggi negli input)
                    
                    op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_conduttore)]
                    self.log.append('{:0.1f} | {} | Inizio carico-scarico | {}'.format(self.env.now-self.cs, self.name,op))  
                    self.link[self.op_conduttore][0] += self.cs + 0.11 #* 2 # aumento la saturazione dell'operatore che esegue questa fase (il x2 è per considerare lo spostamento) 0.11 isola2
                    #self.tempo += self.cs
                    #self.log_op.append('{:0.1f} | saturazione  )
                    
                    self.log_op.append('{:0.1f}_{} | fine carico-scarico macchina {} | + {} minuti'.format(self.env.now,op, self.name, self.cs))
                    self.sat.append(self.cs)

                
            yield self.env.timeout(self.tc)  #lavoro un pezzo  

            self.parts_made += self.batch 


            if self.tempo_ciclo_cq1 is not None:
                self.qc_count1 += self.batch
            if self.tempo_ciclo_cq2 is not None:     
                self.qc_count2 += self.batch
            if self.tempo_ciclo_cq3 is not None:
                self.qc_count3 += self.batch
            if self.tempo_ciclo_cq4 is not None:
                self.qc_count4 += self.batch
            if self.tempo_ciclo_cq5 is not None:
                self.qc_count5 += self.batch


            self.sap_count += self.batch  
            self.part_in_count += self.batch
                       
            self.corr_count += self.batch
            self.count_utensile  += self.batch
            
            self.log.append('{:0.1f} | {} | Avvio macchina '.format(self.env.now-self.tc, self.name)) 
            #self.log.append('{} | {} | Fine ciclo '.format(env.now, self.name))
                 
            if self.qc_count1==self.periodo_cq1: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq1, self.tempo_ciclo_cq1, self.name_cq1))# 'controllo qualità_Zeiss'))
                self.qc_count1=0
            
            if self.qc_count2==self.periodo_cq2: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq2, self.tempo_ciclo_cq2, self.name_cq2))# 'controllo qualità_2'))
                self.qc_count2=0
            
            if self.qc_count3==self.periodo_cq3: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq3, self.tempo_ciclo_cq3, self.name_cq3))# 'controllo qualità_3'))
                self.qc_count3=0
            
            if self.qc_count4==self.periodo_cq4: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq4, self.tempo_ciclo_cq4, self.name_cq4))# 'controllo qualità_4'))
                self.qc_count4=0
            
            if self.qc_count5==self.periodo_cq5: #se è il pezzo da controllare                
                self.env.process(CQ(self, self.env, self.op_cq5, self.tempo_ciclo_cq5, self.name_cq5))# 'controllo qualità_5'))
                self.qc_count5=0
                                           
            if self.corr_count==self.periodo_corr:               
                self.env.process(Correzione(self, self.env, self.op_corr, self.tc_corr))#------questo è a macchina funzionante
                #with self.op_corr.request(priority=1) as req: 
                    #yield req # blocco la risorsa
                    #yield env.timeout(self.tc_corr) 

                    #op =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_corr)]
                    #self.log.append('{:0.1f} | {} | inizio correzione | {}'.format(env.now-self.tc_corr, macchina.name, op))
                    #self.log.append('{:0.1f} | {} | fine correzione | {}'.format(env.now, self.name, op))
            
                    #self.link[self.op_corr][0] += self.tc_corr

                self.corr_count=0
                                
            if self.sap_count==self.periodo_SAP:                 
                self.env.process(Other(self, self.env, self.op_sap, self.tempo_ciclo_SAP, 'avanzamento SAP'))
                self.sap_count=0
                
            if self.part_in_count==self.periodo_part_in:             
                self.env.process(Other(self, self.env, self.op_in, self.tc_part_in, 'Prelievo grezzi'))
                self.part_in_count=0

            self.turno_now = math.floor(self.env.now / 450)+1   

            if self.turno_now > self.turno:
                self.env.process(CQ_T(self, self.env, self.op_ct1, self.tempo_ct1, self.offset_ct1, self.name_ct1))# 'Controllo a turno_1')) # nella isola4-5  il controllo 1Tè come quello degli altri controlli a frequenza
                
                if self.op_ct2 != None:
                    self.env.process(CQ_T(self, self.env, self.op_ct2, self.tempo_ct2, self.offset_ct2, self.name_ct2))# 'Controllo a turno_2'))

                if self.op_ct2 != None:
                    self.env.process(CQ_T(self, self.env, self.op_ct3, self.tempo_ct3, self.offset_ct3, self.name_ct3))#'Controllo a turno_3'))

                
                self.turno = self.turno_now



                #self.link[self.op_ct1][0] += self.tempo_ct1 # aggiungo solo la  quota saturazione, non chiamo la funzione seno fa controllo che ferma le macchiine
                # devo mettere anche gli altri controlli, ma solo se esistono : condizione if qualcosa is not None -----------------------------------------
#***controllo turno                
            self.log.append('{:0.1f} | {} | Fine ciclo | parts:{} '.format(self.env.now, self.name, self.parts_made))
            
            if self.t_cambio_ut != 0:
                #if self.count_utensile == self.periodo_cu:
                op_ut =  list(self.link_op.keys())[list(self.link_op.values()).index(self.op_cambio_ut)]
                if self.count_utensile == self.periodo_cu:    
                    with self.op_cambio_ut.request(priority=1) as req: 
                        yield req # blocco la risorsa
                        yield self.env.timeout(self.t_cambio_ut)
                        self.log.append('{:0.1f}  | {} | Inizio cambio utensile | {}'.format(self.env.now-self.t_cambio_ut, self.name,op_ut))
                        self.log.append('{:0.1f}  | {} | Fine cambio utensile | {}'.format(self.env.now, self.name,op_ut))   
                        self.link[self.op_cambio_ut][0] += self.t_cambio_ut
                    self.count_utensile = 0



def carica_info_macchina(mac, db_utensili):
    
    # recupero info cq
    controlli = mac['Cq']
    list_controlli = []
    for j in range(5):
        try:
            t = controlli[j]['durata']
            f = controlli[j]['periodo']
            o = controlli[j]['op']
            n = controlli[j]['task']

            list_controlli.append((f,t,o,n))
        except:
            list_controlli.append((None,None,None,None))

    # recupero info controlli 1 a turno 
        turno = mac['Turno']
        list_turno = []
        for j in range(3):
            try:
                turno_t = turno[j]['durata']
                ot = turno[j]['op']
                nome = turno[j]['task']
                list_turno.append((turno_t,ot,nome))
            except:
                list_turno.append((None,None,None))

        other = mac['Other']

    # recupero info correzione
        try:
            periodo_cor = other['Correzione']['periodo']
            durata_cor = other['Correzione']['durata']
            op_corr = other['Correzione']['op']
        except:
            periodo_cor = None
            durata_cor = None
            op_corr = None
            
    # recupero info SAP

        try:
            periodo_SAP = other['avanzamento SAP']['periodo']
            durata_SAP = other['avanzamento SAP']['durata']
            op_sap = other['avanzamento SAP']['op']
        except:
            periodo_SAP = None
            durata_SAP = None
            op_sap = None

    # recupero info part_in

        try:
            periodo_part_in = other['prelievo grezzi']['periodo']
            durata_part_in = other['prelievo grezzi']['durata']
            op_in = other['prelievo grezzi']['op']
        except:
            periodo_part_in = None
            durata_part_in = None
            op_in = None
            
    # recupero info part_out

        try:
            periodo_part_out = other['scambio interfalde']['periodo']
            durata_part_out = other['scambio interfalde']['durata']
            op_out = other['scambio interfalde']['op']

        except:
            try:
                periodo_part_out = other['trasporto pezzi a TT']['periodo']
                durata_part_out = other['trasporto pezzi a TT']['durata']
                op_out = other['trasporto pezzi a TT']['op']
            except:
                periodo_part_out = None
                durata_part_out = None
                op_out = None

    # info generali

        info = mac['Generale']
        try:
            part_in = info['input']
        except:
            part_in = None

        try:    
            part_out = info['output']
        except:
            part_out = None

        name_machine = mac['Nome']

        part = mac['Particolare']

        tempo_ciclo = info['tempo_ciclo']
        cs = info['carico_scarico']
        batch = info['batch']
        cond = info['conduzione']
        
        try:
            c_ut = info['cambio_ut']
        except:
            c_ut = None

        isola = info['isola']

        try:
            robot_btw = info['robot_dopo_avvio']
        except:
            robot_btw = None
        
        robot_zeiss = None
        for elemento in controlli:
            if controlli[elemento]['task'] == 'controllo_zeiss':
                robot_zeiss = controlli[elemento]['durata_robot']

    #--------------------qui poi va inserito il dataframe utensili

        df_ut = db_utensili[(db_utensili.isole == isola) & (db_utensili.macchina == name_machine) & (db_utensili.modello.astype(str) == part)]
        
        freq_test = df_ut.vita_ut.min()
        
        freq_eq = freq_test # si può mettere una condizione

        df_ut['new']=df_ut.totale * freq_eq/df_ut['vita_ut']
        t_eq = df_ut.new.sum()

    return isola, part_in, part_out, name_machine, part, tempo_ciclo, cs, batch, cond, c_ut,freq_eq, t_eq, list_controlli, list_turno, durata_cor, periodo_cor, op_corr,durata_SAP, periodo_SAP, op_sap,durata_part_in, periodo_part_in, op_in,durata_part_out, periodo_part_out, op_out, robot_zeiss, robot_btw
