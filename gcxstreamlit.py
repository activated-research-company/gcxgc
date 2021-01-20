# This program was written by Andrew Jones
# for Activated Research Company (ARC).
# It is intended as a program for the quick visualization of comprehensive
# 2D GC (GCxGC) data.
# The program is covered under the MIT license and is completely free to use
# and open source

# GCxGC with Streamlit v1.0

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.title('GCxGC by [ARC] (https://www.activatedresearch.com/)')

st.write('This program will convert 1D GC data into a 2D GCxGC heatmap')

uploaded_file = st.sidebar.file_uploader('Upload your csv data file here or select an example from the drop down below')

option = st.sidebar.selectbox('Examples:', ('Select','Gasoline','Biodiesel'))

if uploaded_file is not None or option != 'Select':
    if option == 'Gasoline':
        uploaded_file = 'https://drive.google.com/uc?export=download&id=1_g2PcLUrXVmdMIZWoP-JahbYLHmmf-Hj'
    elif option == 'Biodiesel':
        uploaded_file = 'https://drive.google.com/uc?export=download&id=1WXJVY3hGcy21VZIfaaMP-rV8dgPSQP1y'

    df = pd.read_csv(uploaded_file,low_memory=False)
    dn = df.drop([0,1])
    dn = dn.to_numpy(dtype='float64')
    sig = dn[:,1]
    time = dn[:,0]

    numpoints = len(sig)
    st.sidebar.text('Found ' + str(numpoints) + ' data points')
    runtime = time[numpoints-1]
    st.sidebar.text('Runtime is ' + str(runtime) + ' minutes')
    rate = round(numpoints/runtime/60)
    st.sidebar.text('Acquisition rate is ' + str(rate) + ' Hz')

    if option == 'Select':
        modtime = st.sidebar.number_input('Enter modulation period in seconds')
        if not modtime:
            st.sidebar.warning('Please input the modulation period')
            st.stop()
        st.sidebar.success('Modulation time recorded')
    elif option == 'Gasoline':
        modtime = 3.0
    elif option == 'Biodiesel':
        modtime = 3.3

    ## Pad matrix so it can be resized
    xp = int(round(modtime*rate))
    yp = int(np.ceil(numpoints/xp))
    extralines = int((yp*xp)-numpoints)
    avg_sig = np.mean(sig[(numpoints-21) :])                  
    if extralines != 0:
        for i in range(extralines):
            sig = np.append(sig, avg_sig)
    
    data_2D = sig.reshape(yp,xp)#converts 1D signal into 2D with xp x yp dimensions
    data_2D = np.transpose(data_2D)
    st.sidebar.text('A ' + str(xp) + ' x ' + str(yp) + ' array was created')

    power = st.sidebar.slider('Select level of enhancement',1,100,10)
    colorscale_select = st.sidebar.selectbox('Colorscale',('rainbow', 'jet', 'inferno', 'thermal', 'portland','spectral', 'balance', 'edge', 'hsv'))
    scheck = st.sidebar.checkbox('Use smoothing?',value=True)
    if scheck:
        smoothing = 'best'
    else:
        smoothing = False

    data_2D_power = np.power(data_2D,1/(power))

###### Plotting, see https://plotly.com/python-api-reference/generated/plotly.graph_objects.Heatmap.html
    x_1D = np.arange(start=0,stop=runtime,step=runtime/len(data_2D[0,:]))
    y_2D = np.arange(start=0,stop=modtime,step=modtime/len(data_2D[:,0]))
    fig = go.Figure(data=go.Heatmap(x=x_1D,y=y_2D,z=data_2D_power, zsmooth=smoothing, colorscale=colorscale_select))
    fig.update_layout(title='2D heatmap:',xaxis_title='1D time (min)',yaxis_title='2D time (s)',hovermode="x unified")
    st.plotly_chart(fig)

    slicetime = st.number_input('Enter time (min) for extracted chromatogram',min_value=0.0,max_value=runtime,value=0.0)
    arrayslice = int(round(slicetime/runtime*len(data_2D[0,:])))
    fig2 = px.line(x=y_2D,y=data_2D[:,arrayslice],labels={'x':'2D time (s)', 'y':'FID signal (pA*s)'}, title='Extracted 2D chromatogram:')
    #fig2 = px.line(x=y_2D,y=[data_2D[:,(arrayslice-1)],data_2D[:,arrayslice],data_2D[:,(arrayslice+1)]],labels={'x':'2D time (s)', 'y':'FID signal (pA*s)'}, title='Extracted 2D chromatogram:')
    st.plotly_chart(fig2)
                
    fig3 = px.line(x=x_1D,y=np.sum(data_2D,axis=0),render_mode='svg',line_shape='spline',labels={'x':'1D time (min)', 'y':'FID signal (pA*s)'},title='Projected 1D chromatogram:')
    fig3.add_shape(type="line",x0=slicetime,y0=0,x1=slicetime,y1=max(np.sum(data_2D,axis=0)),line=dict(color="Red",width=1)) #add line to show where extracted chromatogram is
    st.plotly_chart(fig3)

else:
    st.write('')
    st.title("Step 1: upload your file (left) or select an example")
    st.write("Data files must have 3 rows of header data and then time and signal in the first two columns. Here is an example taken from an Agilent 7890 GC, by exporting the .ch file to a csv with MSD ChemStation:")
    #filelink = '<a href="https://github.com/activated-research-company/gcxgc/raw/main/Gasoline.CSV" download="Gasoline.csv">Download example csv file here</a>'
    #st.write(<a href=path>Download example</a>)
    st.write('Download example csv file with modulation time of 3.0 s [here] (https://drive.google.com/uc?export=download&id=1_g2PcLUrXVmdMIZWoP-JahbYLHmmf-Hj)',unsafe_allow_html=True)
    #st.image("https://www.activatedresearch.com/wp-content/uploads/2021/01/Example.png", use_column_width=True)
    
