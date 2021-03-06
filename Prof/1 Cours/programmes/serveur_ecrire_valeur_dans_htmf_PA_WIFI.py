# Ecrire les valeurs d'un capteur de température et d'humidité
# dans une page HTML. Déclarer un serveur HTTP. Quand ce serveur
# reçoit une requête, il renvoie dans une page HTML les valeurs du capteur

import network                # module permettant la communication sur un réseau Wifi 
import socket                 # module exploitant l'outil "socket"
import gc                     # garbage collector : ramasse miettes : gestionnaire de l'espace mémoire non-utilisé
gc.collect()                  # activation du garbage collector
#import urequests as requests  #
from machine import Pin       # module de la carte ESP32
import dht                    # module pour l'utilisation du capteur de température et d'humidité

S_led = Pin(17, Pin.OUT)      # déclaration de l'objet Sortie Led
E_sensor = dht.DHT22(Pin(4))  # déclaration de l'objet Entrée Sensor

ssid = 'PA-Si-A023'           # Paramètres de notre Point d'Accès Wifi (raspberry)
password = 'wifiA023'         # mot de passe

station = network.WLAN(network.STA_IF) # création de notre station wifi ESP32
station.active(True)                   # Activation de notre station wifi sur ESP32
station.connect(ssid, password)        # tentative de connexion au Point d'Accès Wifi
while station.isconnected() == False:  # on reste dans la boucle tant que la connexion n'est pas établie 
  pass

print("Connexion au Point d'Accès Wifi établie")  # la connexion est établie
print(station.ifconfig())              # on affiche dans la console les caractéritiques IP de notre carte ESP32
print("")                              # saut d'une ligne dans l'affichage

V_html = """<!doctype html><html lang="fr"><head><meta charset="utf-8" name="affichage" content="width=device-width, initial-scale=1"><title>Réponse du serveur</title></head>
<body><h1>ESP Web Server</h1><p>temperature : ???°C </p><p>Taux d'humidite : ???% </p></body></html>"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # création d'un objet socket
s.bind(('', 80))                       # lier le socket à une adresse IP (ici rien = adresse de la carte) et un port (ici 80)
s.listen(5)                            # le socket est prêt à écouter (5 communications maxi en même temps)

def ecriture_val_html(val, ref): # ref contient le texte à détecter dans la page html et val la valeur à écrire
    """
    Fonction recevant comment paramètres :
    - une valeur
    - le texte à détecter dans la page HTML
    Elle modifie le contenu de la page HTML pour introduire les valeurs du capteur
    """
    global V_html                     # utiisation d'une variable globale
    indexRef = V_html.find(ref)       # récupération de l'indice où se trouve le mot contenu dans "ref"
    if ref == "temperature":          # si ref contient "temperature"
        indexRef2 = V_html.find("°C") # récupération de l'indice où se trouve le mot "°C"
    elif ref == "humidite":           # si ref contient "humidite"
        indexRef2 = V_html.find("%")  # récupération de l'indice où se trouve le mot "%"
    debut_trame_html=''               # déclaration d'un variable str vide
    for lettre in V_html[:indexRef+len(ref)+3]: # remplir la variable avec tout le début du contenu de V_html
        debut_trame_html=debut_trame_html+lettre# jusqu'à la fin du mot contenu dans "ref"
    fin_trame_html=''                 # déclaration d'un variable str vide
    for lettre in V_html[indexRef2:]: # remplir la variable avec toute la fin du contenu de V_html
        fin_trame_html=fin_trame_html+lettre# à partir de l'indice trouvé précédemment
    V_html = debut_trame_html + str(val) + fin_trame_html# élaboration du contenu html complet à envoyer
    
while True:
    conn, addr = s.accept()      # le socket "s" attend une demande. Quand la requête arrive
                                 # conn est un nouvel objet socket qui sert pour recevoir ou envoyer la donnée
                                 # addr variable qui contient l'adresse IP du client ayant envoyé la requête  
    print('Connexion établie avec %s' % str(addr)) # affichage de l'adresse IP du client
    contenu_requete = conn.recv(1024)      # on récupère de l'objet socket conn le contenu de la requête (1024 nombre de data)
    contenu_requete = str(contenu_requete) # on le transforme en texte
    print('Contenu de la requête = %s' % contenu_requete)# on affiche le contenu de la requête
    print("")                      # saut d'une ligne dans l'affichage
    E_sensor.measure()             # lance la lecture du capteur
    V_temp = E_sensor.temperature()# lecture de la température (variable de type float)
    V_hum = E_sensor.humidity()    # lecture de l'humidité (variable de type float)
    V_temp = round(V_temp, 1)      # on ne garde qu'un chiffre après la virgule
    V_hum = round(V_hum, 1)
    ecriture_val_html(V_temp, "temperature") # appel à la fonction pour ajouter la valeur de la température à la variable HTML
    ecriture_val_html(V_hum, "humidite")     # appel à la fonction pour ajouter la valeur de l'humidité à la variable HTML
    V_reponse_complete=('HTTP/1.1 200 OK\nContent-Type: text/html\nConnection: close\n\n'+V_html) # début de la trame HTTP suivi du contenu de V_html
    print("reponseCompete :",V_reponse_complete) # affichage de la trame HTTP envoyé comme réponse
    conn.send(V_reponse_complete)  # envoie de la réponse
    conn.close()                   # on ferme l'objet socket conn

