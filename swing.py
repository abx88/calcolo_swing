#!/usr/bin/env python
# coding: utf-8

# In[2]:


import datetime as dt
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# In[3]:
st.set_page_config(
    page_title="Analisi Swing",
    layout="wide")


st.title("Analisi swing")

uploaded_file = st.file_uploader("Carica un file CSV")

if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, delimiter = ",")
        
        #df['date_time']= df['<DATE>'] + ' ' + df['<TIME>']
        #df.drop(['<DATE>','<TIME>','<TICKVOL>','<SPREAD>'], axis=1,inplace=True)
        
        df['date_time']= df['Date'] + ' ' + df['Time']
        df.drop(['Date','Time','Volume'], axis=1,inplace=True)
        
        df.set_index('date_time', inplace=True)
        df.index = pd.to_datetime(df.index)#occorre per convertire in datetime la data
        df['midprice'] = (df.High+df.Low)/2
        



        inizio_serie=str(df.index.min())
        fine_serie=str(df.index.max())
        
        st.sidebar.title("Gestione serie storica")
        st.sidebar.text("INIZIO SERIE "+inizio_serie)
        st.sidebar.text("FINE SERIE "+fine_serie)

        inizio = st.sidebar.date_input("inizio periodo", df.index.min()) 
        fine = st.sidebar.date_input("fine periodo", df.index.max()) 
        
        
        df = df[inizio:fine]
        st.subheader("tabella dati + grafico strumento")
       
        st.dataframe(df, use_container_width=True)        
        
        calcolo_swing = st.button("calcolo swing")
        sogliaperc = st.number_input("soglia swing (0.01=1%)", value= 0.01, step=0.01)




        if calcolo_swing:
            st.subheader("riepilogo swing")
            col3, col4 = st. columns(2)

            #loop indice    
            indicenum=[]
            i = 0
            n = len(df)
            while i < n:
                indicenum.append(i)
                i += 1

            df['data2']=df.index     
            df['indice']=indicenum
            df.set_index('indice',inplace=True)
            df['indice2']=df.index

        #inizializzazione loop
            swing_hilo=[0]
            data_hilo=[0]
            i = 3
            n = len(df)
            if df[(df.index==1)].midprice.sum()<df[(df.index==2)].midprice.sum():
                minimo=df[(df.index==1)].midprice.sum()
                massimo=df[(df.index==2)].midprice.sum()
                pmax=df[(df.midprice==massimo)].indice2.sum()
                pmin=df[(df.midprice==minimo)].indice2.sum()
            elif df[(df.index==1)].midprice.sum()>df[(df.index==2)].midprice.sum():
                minimo=df[(df.index==2)].midprice.sum()
                massimo=df[(df.index==1)].midprice.sum()
                pmin=df[(df.midprice==massimo)].indice2.sum()
                pmax=df[(df.midprice==minimo)].indice2.sum()
            else:
                minimo=df[(df.index==1)].midprice.sum()
                massimo=df[(df.index==2)].midprice.sum()
                pmin=1
                pmax=2

        #loop individuazione max e min relativi
            while i < n:
                valoreindice=df[(df.index==i)].Open.sum()
                soglia=sogliaperc*valoreindice
                if pmax>pmin:#massimi crescenti 
                    if df[(df.index==i)].midprice.sum()>=massimo:
                        swing_hilo.pop()
                        data_hilo.pop()
                        massimo=df[(df.index==i)].midprice.sum()
                        swing_hilo.append(massimo)
                        data_hilo.append(df[(df.index==i)].data2.min())
                        pmax=i
                    elif df[(df.index==i)].midprice.sum()<massimo-soglia:
                        minimo=df[(df.index==i)].midprice.sum()
                        swing_hilo.append(minimo)
                        data_hilo.append(df[(df.index==i)].data2.min())
                        pmin=i
                elif pmax<pmin:#minimi decrescenti
                    if df[(df.index==i)].midprice.sum()<=minimo:
                        minimoold=minimo
                        swing_hilo.pop()
                        data_hilo.pop()
                        minimo=df[(df.index==i)].midprice.sum()
                        swing_hilo.append(minimo)
                        data_hilo.append(df[(df.index==i)].data2.min())
                        pmin=i
                    elif df[(df.index==i)].midprice.sum()>minimo+soglia:
                        massimo=df[(df.index==i)].midprice.sum()
                        swing_hilo.append(massimo)
                        data_hilo.append(df[(df.index==i)].data2.min())
                        pmax=i
                i += 1

           
         #creazione df dei soli swing        
            swing_HILO=pd.DataFrame(swing_hilo)
            swing_HILO.columns=[('maxmin')]
            swing_HILO['data']=data_hilo
            differenze=[0]
            i=1
            n=len(swing_HILO)
            while i < n:
                differenza=(swing_HILO[(swing_HILO.index==i)].maxmin.sum())-(swing_HILO[(swing_HILO.index==i-1)].maxmin.sum())
                differenze.append(differenza)
                i+=1

            swing_HILO['differenze']=differenze
            swing_HILO['differenze_perc']=(swing_HILO.differenze/swing_HILO.maxmin)*100
            swing_HILO.set_index('data', inplace=True)
            swing_HILO.index = pd.to_datetime(swing_HILO.index)#occorre per convertire in datetime la data
            



            col3.dataframe(swing_HILO, use_container_width = True)

            swing = px.scatter(swing_HILO,x=swing_HILO.index, y=swing_HILO.differenze)
            swing.update_xaxes(
                        title_text = "ampiezza swing maggiori di "+str(sogliaperc*100)+'%',
                        title_font = {"size": 15},
                        title_standoff = 10)
            col4.plotly_chart(swing,use_container_width=True )
            
            df.set_index('data2', inplace=True)
            df.index = pd.to_datetime(df.index)#occorre per convertire in datetime la data
            
            swing_zigzag = go.Figure()
            swing_zigzag.add_trace(go.Scatter(
                mode = "lines",
                y = df.Close,
                x = df.index,
                name="indice"))
            swing_zigzag.add_trace(go.Scatter(
                mode = "lines+markers",
                y = swing_HILO.maxmin,
                x = swing_HILO.index,
                name="zigzag",
                connectgaps=True))

            swing_zigzag.update_layout(
                    title={
                        'text': 'swing',
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'})

            st.plotly_chart(swing_zigzag,use_container_width=True)
            
            min_value = int(swing_HILO.differenze.min())
            max_value = int(swing_HILO.differenze.max())
            
            st.subheader('distribuzione swing maggiori di '+str(sogliaperc*100)+'%')
            swingdistr=px.histogram(swing_HILO, x=swing_HILO.differenze,histnorm='probability', nbins = 20)
            swingdistr.update_xaxes(
                        title_text = "distribuzione swing maggiori di "+str(sogliaperc*100)+'%',
                        title_font = {"size": 15},
                        title_standoff = 10,
                        )
            st.plotly_chart(swingdistr,use_container_width=True )
            
            
            min_value_perc = int(swing_HILO.differenze_perc.min())
            max_value_perc = int(swing_HILO.differenze_perc.max())
            
            st.subheader('distribuzione swing maggiori di '+str(sogliaperc*100)+'% (valori percentuali)')
            swingdistr=px.histogram(swing_HILO, x=swing_HILO.differenze_perc,histnorm='probability',nbins = 20)
            swingdistr.update_xaxes(
                        title_text = "distribuzione swing maggiori di "+str(sogliaperc*100)+'% (valori percentuali)',
                        title_font = {"size": 15},
                        title_standoff = 10,
                        tickvals=list(range(int(min_value_perc), int(max_value_perc) + 1)), 
                        ticktext=list(range(int(min_value_perc), int(max_value_perc) + 1)) )
            st.plotly_chart(swingdistr,use_container_width=True )
            
            
            swingdescrLong=pd.DataFrame(swing_HILO[(swing_HILO.differenze>0)].differenze.describe(
                [0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.99]))
            swing_HILO['val_abs'] = swing_HILO.differenze.abs()
            swingdescrShort=pd.DataFrame(swing_HILO[(swing_HILO.differenze<0)].val_abs.describe(
                [0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.99]))
            
            swingdescrLongPerc=pd.DataFrame(swing_HILO[(swing_HILO.differenze>0)].differenze_perc.describe(
                [0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.99]))
            swing_HILO['val_abs_perc'] = swing_HILO.differenze_perc.abs()
            swingdescrShortPerc=pd.DataFrame(swing_HILO[(swing_HILO.differenze<0)].val_abs_perc.describe(
                [0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.99]))
            
            col5, col6 = st.columns(2)
            col5.subheader('valori statistici swing Long maggiori di '+str(sogliaperc*100)+'%')
            col5.table(swingdescrLong.iloc[1:3])
            col6.subheader('valori statistici swing Short maggiori di '+str(sogliaperc*100)+'%')
            col6.table(swingdescrShort.iloc[1:3])
            col5.subheader('valori statistici swing Long maggiori di '+str(sogliaperc*100)+'% (valori percentuali)')
            col5.table(swingdescrLongPerc.iloc[1:3])
            col6.subheader('valori statistici swing Short maggiori di '+str(sogliaperc*100)+'% (valori percentuali)')
            col6.table(swingdescrShortPerc.iloc[1:3])
            
            
            col5.subheader("distribuzione cumulativa swing Long maggiori di "+str(sogliaperc*100)+'%')
            swingdistrcumLong=go.Figure(data=[go.Histogram(x=(swing_HILO[(swing_HILO.differenze>0)].differenze),
                                                       histnorm='probability density', cumulative_enabled=True)])

            swingdistrcumLong.update_xaxes(
                        title_text = "distribuzione cumulativa swing Long maggiori di "+str(sogliaperc*100)+'%',
                        title_font = {"size": 15},
                        title_standoff = 10)
            col5.plotly_chart(swingdistrcumLong,use_container_width=False)
            
            col6.subheader("distribuzione cumulativa swing Short maggiori di "+str(sogliaperc*100)+'%')
            swingdistrcumShort=go.Figure(data=[go.Histogram(x=swing_HILO[(swing_HILO.differenze<0)].val_abs,
                                                       histnorm='probability density', cumulative_enabled=True)])

            swingdistrcumShort.update_xaxes(
                        title_text = "distribuzione cumulativa swing Short maggiori di "+str(sogliaperc*100)+'%',
                        title_font = {"size": 15},
                        title_standoff = 10)
            
            col6.plotly_chart(swingdistrcumShort,use_container_width=False)
            
            col5.subheader("distribuzione cumulativa swing Long maggiori di "+str(sogliaperc*100)+'% (valori percentuali)')
            swingdistrcumLong=go.Figure(data=[go.Histogram(x=(swing_HILO[(swing_HILO.differenze>0)].differenze_perc),
                                                       histnorm='probability density', cumulative_enabled=True)])

            swingdistrcumLong.update_xaxes(
                        title_text = "distribuzione cumulativa swing Long maggiori di "+str(sogliaperc*100)+'% (valori perc)',
                        title_font = {"size": 15},
                        title_standoff = 10)
                      
            col5.plotly_chart(swingdistrcumLong,use_container_width=False)
            
            col6.subheader("distribuzione cumulativa swing Short maggiori di "+str(sogliaperc*100)+'% (valori percentuali)')
            swingdistrcumShort=go.Figure(data=[go.Histogram(x=swing_HILO[(swing_HILO.differenze<0)].val_abs_perc,
                                                       histnorm='probability density', cumulative_enabled=True)])

            swingdistrcumShort.update_xaxes(
                        title_text = "distribuzione cumulativa swing Short maggiori di "+str(sogliaperc*100)+'% (valori perc)',
                        title_font = {"size": 15},
                        title_standoff = 10)
            
            col6.plotly_chart(swingdistrcumShort,use_container_width=False)
            

            col5.subheader('percentili swing Long maggiori di '+str(sogliaperc*100)+'%')
            col5.table(swingdescrLong.iloc[4:17])
            col6.subheader('percentili swing Short maggiori di '+str(sogliaperc*100)+'%')
            col6.table(swingdescrShort.iloc[4:17])
            
            col5.subheader('percentili swing Long maggiori di '+str(sogliaperc*100)+'% (valori percentuali)')
            col5.table(swingdescrLongPerc.iloc[4:17])
            col6.subheader('percentili swing Short maggiori di '+str(sogliaperc*100)+'% (valori percentuali)')
            col6.table(swingdescrShortPerc.iloc[4:17])



                                       
                                       
                                       
                                        

                                                 
                                                 
                                                 
                                                 
