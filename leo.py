from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic
import folium
import webbrowser
import pandas as pd
import PySimpleGUI as sg

def obter_coordenadas_usuario():
    geolocator = Nominatim(user_agent="teste-palancacode")
    while True:
        layout = [[sg.Text("Digite o local desejado:")],
                  [sg.Input(key="lugar")],
                  [sg.Button("Ok"), sg.Button("Cancelar")]]
        window = sg.Window("Consulta", layout)
        event, values = window.read()
        window.close()
        if event == "Ok":
            lugar_input = values["lugar"]
            try:
                location_user = geolocator.geocode(lugar_input)
                if location_user:
                    return location_user.latitude, location_user.longitude
                else:
                    sg.popup_error("Local não encontrado. Tente novamente.", title="Erro")
            except GeocoderTimedOut:
                sg.popup_error("Tempo limite excedido. Tente novamente.", title="Erro")
        elif event == "Cancelar" or event == sg.WIN_CLOSED:
            return None

def calcular_distancia_usuario(local_usuario, coordenadas_mercado):
    return geodesic(local_usuario, coordenadas_mercado).kilometers

file_path = sg.popup_get_file("Selecione o arquivo CSV")

while True:
    try:
        db = pd.read_csv(file_path, sep=';')
        break
    except FileNotFoundError:
        sg.popup_error("Arquivo não encontrado. Certifique-se de que o caminho do arquivo está correto.", title="Erro")
        file_path = sg.popup_get_file("Selecione o arquivo CSV")

while True:
    local_usuario = obter_coordenadas_usuario()
    if local_usuario:
        renda_minima = float(sg.popup_get_text("Digite a renda mínima: "))

        pontos = []

        for index, row in db.iterrows():
            if row['SAL'] >= renda_minima:
                pontos.append(index)

        latitude = -22.3145
        longitude = -49.0600

        bauru_map = folium.Map(location=[latitude, longitude], zoom_start=12)

        coordenadas_usuario = local_usuario

        popup_usuario = f"<b>Local do Usuário</b><br>{coordenadas_usuario}"
        folium.Marker(coordenadas_usuario, popup=popup_usuario, icon=folium.Icon(color='red')).add_to(bauru_map)

        for ponto in pontos:
            row = db.iloc[ponto]
            dist = calcular_distancia_usuario(local_usuario, [row['LAT'], row['LONG']])
            if dist <= 30:  # Adicione esta linha
                popup_content = f"<b>{row['RUA']}</b><br>Distância: {dist:.2f} km<br>Salário: {row['SAL']:.2f}"
                folium.Marker([row['LAT'], row['LONG']], popup=popup_content).add_to(bauru_map)

        bauru_map.save("mapa_bauru.html")
        webbrowser.open("mapa_bauru.html")

        continuar = sg.popup_yes_no("Deseja realizar outra consulta?")
        if continuar == "No":
            break
    else:
        break
