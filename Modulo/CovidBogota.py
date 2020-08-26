import pandas as pd
import matplotlib.pyplot as plt
from ipywidgets import interact, interactive
import ipywidgets as widgets
import numpy as np
import urllib.request
import json
import requests
from pandas.io.json import json_normalize
from IPython.core.display import HTML, display

url='https://datosabiertos.bogota.gov.co/api/3/action/datastore_search?resource_id=b64ba3c4-9e41-41b8-b3fd-2da21d627558&limit=1000000' 
response = requests.get(url)
data = response.json()
recs = data['result']['records']
df0=json_normalize(recs)
df=df0.dropna()
df[["Edad"]]= df[["Edad"]].astype(float)

def f(localidad):
    df2=df[df["Localidad de residencia"]==localidad].groupby("Estado").count()
    ind=df2.index
    data=df2["Edad"]
    fig, ax = plt.subplots(figsize=(6, 5), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(data,wedgeprops=dict(width=0.5), 
                                      startangle=-40)
    pct=["{:.2%}".format(da/sum(data)) for da in data]
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")
    
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))        
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(ind[i]+"  "+pct[i], xy=(x, y),
                    xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)
    ax.set_title("Distribución de casos en "+localidad+
                 "\n\n"+str(sum(data))+" casos confirmados"+"\n")

    plt.show()
    return
Liloc=list(df["Localidad de residencia"].unique()) # Extraemos la lista de localidades

W1=interactive(f, localidad=widgets.Dropdown(options=Liloc,value="Usme", 
                                       description="Localidad:", 
                                       disabled=False,))

### Segundo Widget

def filtroedad(edades):    
    Edad_Filtro=df[df["Edad"]>=edades[0]][df[df["Edad"]>=edades[0]]["Edad"]<=edades[1]]
    Casos=Edad_Filtro.groupby("Localidad de residencia").count()
    Casos=Casos.sort_values("Edad")
    fig, ax = plt.subplots(figsize=(10, 8))
    # Una función para poner la cantidad de casos
    def autolabel(rects):
        for rect in rects:
            width = rect.get_width()
            ax.annotate('{}'.format(width),
                        xy=(width,rect.get_y() + rect.get_height() / 2),
                        xytext=(3,0),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='left', va='center')

    rects=ax.barh(Casos.index,Casos["Edad"],color="#ebbb38")
    ax.set(xlim=(0, max(Casos["Edad"])*1.12))
    plt.title("En total hay "+str(sum(Casos["Edad"]))+" en Bogotá")
    autolabel(rects)
    plt.show()
    return
wid=widgets.IntRangeSlider(
    value=[10, 70],
    min=0,
    max=120,
    step=1,
    description='Edades:',
    orientation='horizontal',
    readout=True,
    readout_format='d',
)
W2=interactive(filtroedad,edades=wid)

#### Dashboard

def miprimerdashboard():
    display(HTML(             '<h2>Casos distribuidos por localidades en Bogotá</h2>'+
                '<p>El siguiente gráfico muestra las distribuciones por localidades en Bogotá:</p>'))
    Casos=df.groupby("Localidad de residencia").count()
    Casos=Casos.sort_values("Edad")
    fig, ax = plt.subplots(figsize=(10, 8))
    # Una función para poner la cantidad de casos
    def autolabel(rects):
        for rect in rects:
            width = rect.get_width()
            ax.annotate('{:,}'.format(width),
                        xy=(width,rect.get_y() + rect.get_height() / 2),
                        xytext=(3,0),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='left', va='center')

    rects=ax.barh(Casos.index,Casos["Edad"],color="#386eeb")
    ax.set(xlim=(0, max(Casos["Edad"])+2000))
    plt.title("En total hay "+str(sum(Casos["Edad"]))+" en Bogotá")
    autolabel(rects)
    plt.show()
    display(HTML('<h2>Proporción de casos en cada una de las localidades en Bogotá</h2>'+
                '<p>Seleccione la localidad e identifique cuántos casos hay en cada Localidad Bogotana:</p>'))
  
    display(W1)
    display(HTML('<h2>Distribución por edades</h2>'+
                '<p>Ahora veamos como se dsitribuyen por edades:</p>'))
  
    display(W2)
    
    #Cuarto Gráfico
    display(HTML('<h2>Comportamiento de fallecidos versus recuperados en Bogotá</h2>'+
                '<p>A continuación se visualiza la distribución de los estados mencionados por localidad:</p>'))
    
    df2=df[df["Estado"]=="Fallecido"].groupby("Localidad de residencia").count()
    df3=df[df["Estado"]=="Recuperado"].groupby("Localidad de residencia").count()
    ind = np.arange(len(df2))
    width = 0.4
    fig, ax = plt.subplots(figsize=(10,12))
    rects=ax.barh(df2.index,df2["Edad"],width,color='#e04848',label='Fallecidos')
    autolabel(rects)
    rects=ax.barh(ind + width, df3.Edad, width, color='#3fe84d', label='Recuperados')
    autolabel(rects)
    ax.set(yticks=ind + width, yticklabels=df2.index, ylim=[2*width - 1, len(df2)])
    ax.legend()
    plt.axis([0.0,17000.0,-0.3,len(df2)])
    plt.title("En total hay {:,} fallecidos y".format (sum(df2["Edad"])) +" {:,} recuperados".format (sum(df3["Edad"])) )
    plt.show()
    
    return