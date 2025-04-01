## Scanner de port

import threading
import socket

# Définir une fonction qui va tester un port spécifique
def scan_port(host, port):
    try:
        # Création d'un objet socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Définir un délai pour éviter le TIMEOUT et blocage
        sock.settimeout(1)
        # Tentative de connexion sur le port (0 si la connexion a réussi)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"[+] Port {port} ouvert")
        sock.close()
    except Exception as e:
        # Gestion des erreurs
        print(f"[-] Erreur sur le port {port}: {e}")

# On demande à l'utilisateur l'adresse IP de la cible
target = input("Entrez l'IP à scanner: ")

# On demande la plage d'adresses à scanner
start_port = int(input("Port de début: "))
end_port = int(input("Port de fin: "))

# On informe l'utilisateur qu'on commence le scan
print(f"\n[***] Scan de {target} sur les ports {start_port} à {end_port} [***]\n")

# On crée un thread (exécution parallèle) pour chaque port
for port in range(start_port, end_port + 1):
    t = threading.Thread(target=scan_port, args=(target, port))
    t.start()
