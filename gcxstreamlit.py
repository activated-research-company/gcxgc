import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.title('GCxGC by ARC')

st.write('This program will convert 1D GC data into a 2D GCxGC heatmap')

uploaded_file = st.sidebar.file_uploader('Upload your GCxGC data file here')

if uploaded_file is not None:
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

    modtime = st.sidebar.number_input('Enter modulation period in seconds')
    if not modtime:
        st.sidebar.warning('Please input the modulation period')
        st.stop()
    st.sidebar.success('Modulation time recorded')

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

    power = st.sidebar.slider('Select level of enhancement',1,100,1)
    colorscale_select = st.sidebar.selectbox('Colorscale',('rainbow', 'jet', 'inferno', 'thermal',
                                                           'portland','spectral', 'balance', 'edge', 'hsv'))
    scheck = st.sidebar.checkbox('Use smoothing?',value=True)
    if scheck:
        smoothing = 'best'
    else:
        smoothing = False

    data_2D_power = np.power(data_2D,1/(power))

###### Plotting
    x_1D = np.arange(start=0,stop=runtime,step=runtime/len(data_2D[0,:]))
    y_2D = np.arange(start=0,stop=modtime,step=modtime/len(data_2D[:,0]))
    fig = go.Figure(data=go.Heatmap(x=x_1D,y=y_2D,z=data_2D_power, zsmooth=smoothing,
                                    colorscale=colorscale_select))
        #https://plotly.com/python-api-reference/generated/plotly.graph_objects.Heatmap.html
#add cache, check out zmid
    fig.update_layout(title='2D heatmap:',xaxis_title='1D time (min)',yaxis_title='2D time (s)',hovermode="x unified")
    st.plotly_chart(fig)

    slicetime = st.number_input('Enter time (min) for extracted chromatogram',min_value=0.0,max_value=runtime,value=0.0)
    arrayslice = int(round(slicetime/runtime*len(data_2D[0,:])))
    fig2 = px.line(x=y_2D,y=data_2D[:,arrayslice],labels={'x':'2D time (s)', 'y':'FID signal (pA*s)'},
                   title='Extracted 2D chromatogram:')
    st.plotly_chart(fig2)
                
    fig3 = px.line(x=x_1D,y=np.sum(data_2D,axis=0),render_mode='svg',line_shape='spline',labels={'x':'1D time (min)', 'y':'FID signal (pA*s)'},
                   title='Collapsed 1D chromatogram:')
    st.plotly_chart(fig3)
