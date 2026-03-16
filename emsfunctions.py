
import random, socket, pickle
import socket
import pickle
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, COIN_CMD
from collections import OrderedDict


# ######################---------------------------------------------------------------------######################

# Funzione per generare un profilo con variazione casuale (distribuzione normale) senza valori negativi
def genera_profilo_casuale_distribuito(profilo_base, media=0, deviazione=1, limite_max=2, limite_min=0):
    profilo_copia = profilo_base[:]  # Copia del profilo base
    profilo_copia = [x + random.gauss(media, deviazione) for x in profilo_copia]  # Aggiunge una variazione casuale
    # Controlla che i valori siano compresi tra limite_min e limite_max
    profilo_copia = [min(max(x, limite_min), limite_max) for x in profilo_copia]  # Impone il limite superiore e inferiore
    return profilo_copia

# Funzione per generare N profili con identificatori dinamici e distribuzione casuale, senza valori negativi
def genera_profili_distribuiti(profilo_base, Nu, media=0, deviazione=1, limite_max=2, limite_min=0):
    profili = {}
    identificatori = [f'B{i+1}' for i in range(Nu)]  # Identificatori come B1, B2, B3, ..., Bn
    for i, identificatore in enumerate(identificatori):
        profili[identificatore] = genera_profilo_casuale_distribuito(profilo_base, media, deviazione, limite_max, limite_min)
    return profili

######################---------------------------------------------------------------------######################

def generate_loads(Nu, w1, w2, w1_1, w2_1):

    # Pattern dei devices (si ripetono ogni 5 profili)
    devices_pattern = [
        [0.4, 1, 0.8],
        [0.3, 1.3, 0.6],
        [1.1, 0.35, 0.8],
        [0.85, 1.45, 0.35],
        [0.55, 1.5, 0.9]
    ]

    # Finestre temporali fisse per tutti
    time_windows = [(0, 23), (0, 23), (0, 23)]

    loads = OrderedDict()

    for i in range(1, Nu + 1):
        # Selezione del pattern di devices (ciclico ogni 5)
        devices = devices_pattern[(i - 1) % 5]
        
        # Assegnazione dei pesi: primi 14 con w1/w2, dal 15 in poi con w1_1/w2_1
        if i <= Nu/2:
            current_w1, current_w2 = w1, w2
        else:
            current_w1, current_w2 = w1_1, w2_1
        
        # Creazione del profilo
        profile_name = f"B{i}"
        loads[profile_name] = {
            "devices": devices.copy(),
            "time_windows": time_windows.copy(),
            "w1": current_w1,
            "w2": current_w2
        }

    return loads



# Funzione per sommare i consumi
def somma_consumi(consumi1, consumi2):
    return [x + y for x, y in zip(consumi1, consumi2)]

######################---------------------------------------------------------------------######################

# Funzione per sottrarre i consumi
def sottrai_consumi(consumi1, consumi2):
    return [x - y for x, y in zip(consumi1, consumi2)]

######################---------------------------------------------------------------------######################


######################---------------------------------------------------------------------######################

def assign_devices_to_profiles(profili_utenti, loads, max_load=3.3):
    updated_profiles = {}
    device_times = {}

    for user, profile in profili_utenti.items():
        updated_profile = profile.copy()
        devices = loads[user]["devices"]
        assigned_times = []
        
        # Ore disponibili (5-21)
        available_hours = list(range(5, 12)) + list(range(18, 22))
        
        for device in devices:
            if not available_hours:
                break  # Se non ci sono più ore disponibili
            
            # Prima prova: cerca ore che non supererebbero il limite
            valid_hours = [h for h in available_hours 
                         if (updated_profile[h] + device) <= max_load]
            
            if valid_hours:
                # Se esistono ore valide, scegli una casuale
                hour = random.choice(valid_hours)
            else:
                # Altrimenti scegli un'ora a caso (anche se supera il limite)
                hour = random.choice(available_hours)
                
            # Assegna il carico
            updated_profile[hour] += device
            assigned_times.append(hour)
            available_hours.remove(hour)
            
            # Se abbiamo superato il limite, cerca di correggere
            if updated_profile[hour] > max_load:
                # Trova ore con spazio disponibile
                alternative_hours = [h for h in range(5, 22) 
                                   if h != hour and 
                                   (updated_profile[h] + device) <= max_load]
                
                if alternative_hours:
                    # Sposta il carico in un'ora alternativa
                    new_hour = random.choice(alternative_hours)
                    updated_profile[hour] -= device
                    updated_profile[new_hour] += device
                    assigned_times[-1] = new_hour  # Aggiorna l'ora assegnata

        updated_profiles[user] = updated_profile
        device_times[user] = assigned_times

    return updated_profiles, device_times


######################---------------------------------------------------------------------######################

# Funzione per calcolare la CBL totale della comunità
def calcola_cbl_totale(profili_utenti):
    cbl_totale = [0] * 24  # Inizializza la CBL totale a 0 per ogni ora
    for profilo in profili_utenti.values():
        cbl_totale = somma_consumi(cbl_totale, profilo)  # Somma i consumi di ogni utente
    return cbl_totale


###################### OTTIMIZZAZIONE Multi OBIETTIVO ###########################

from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus, COIN_CMD

def ottimizza_energia(Nu, Btot, nu_to_user, loads, G, profili_utenti, profili_utenti_start, allocazioni):
    if Nu not in nu_to_user:
        raise ValueError(f"Errore: Nu={Nu} non valido.")
    
    user = nu_to_user[Nu]
    devices = loads[user]["devices"]
    time_windows = loads[user]["time_windows"]
    num_devices = len(devices)
    w1, w2 = loads[user]["w1"], loads[user]["w2"]  # Pesi per i due obiettivi

    # Rimozione allocazioni precedenti (se presenti)
    if user in allocazioni:
        for i, ora_precedente in enumerate(allocazioni[user]):
            if ora_precedente != -1:
                Btot[ora_precedente] -= devices[i]
                profili_utenti[user][ora_precedente] -= devices[i]

    # Inizializzazione problema
    problem = LpProblem(f"MultiObjective_Optimization_{user}", LpMinimize)
    
    # Variabili
    x = LpVariable.dicts("x", [(i, h) for i in range(num_devices) for h in range(24)], cat="Binary")
    diff_G = LpVariable.dicts("diff_G", range(24), lowBound=0)  # Distanza |CBL - G1|
    diff_profile = LpVariable.dicts("diff_profile", range(24), lowBound=0)  # Distanza dal profilo originale

    ### OBIETTIVO COMBINATO ###
    problem += (
        w1 * lpSum(diff_G[h] for h in range(24)) +  # Minimizza scostamento da G1
        w2 * lpSum(diff_profile[h] for h in range(24))  # Minimizza scostamento dal profilo originale
    )


    ### VINCOLI ###
    # 1. Differenza assoluta tra CBL e G1
    for h in range(24):
        problem += diff_G[h] >= (lpSum(devices[i] * x[(i, h)] for i in range(num_devices)) + Btot[h] - G[h])
        problem += diff_G[h] >= -(lpSum(devices[i] * x[(i, h)] for i in range(num_devices)) + Btot[h] - G[h])
    
    # 2. Differenza assoluta dal profilo originale (con i loads iniziali)
    for h in range(24):
        problem += diff_profile[h] >= (profili_utenti[user][h] + lpSum(devices[i] * x[(i, h)] for i in range(num_devices)) - profili_utenti_start[user][h])
        problem += diff_profile[h] >= -(profili_utenti[user][h] + lpSum(devices[i] * x[(i, h)] for i in range(num_devices)) - profili_utenti_start[user][h])

    # 3. Ogni dispositivo acceso una volta nella sua finestra
    for i in range(num_devices):
        problem += lpSum(x[(i, h)] for h in range(time_windows[i][0], time_windows[i][1] + 1)) == 1
    
    # 4. Massimo 2 dispositivi accesi contemporaneamente per utente
    for h in range(24):
        problem += lpSum(x[(i, h)] for i in range(num_devices)) <= 2

    # Risoluzione
    solver = COIN_CMD(path="/opt/homebrew/bin/cbc")
    problem.solve(solver)

    if LpStatus[problem.status] != "Optimal":
        raise ValueError("Soluzione ottimale non trovata.")

    # Aggiornamento allocazioni e profili
    nuova_allocazione = [-1] * num_devices
    for i in range(num_devices):
        for h in range(24):
            if x[(i, h)].varValue == 1:
                nuova_allocazione[i] = h
                Btot[h] += devices[i]
                profili_utenti[user][h] += devices[i]
    
    allocazioni[user] = nuova_allocazione
    return profili_utenti, Btot

