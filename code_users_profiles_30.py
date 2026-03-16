
import matplotlib.pyplot as plt
import numpy as np
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, COIN_CMD
from pulp import PULP_CBC_CMD
from emsfunctions import *
from collections import OrderedDict
import pandas as pd
import time


G6 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.056, 10.2784, 21.648, 30.5536, 36.256, 40.0928, 40.832, 39.8112, 36.7488, 30.6944, 21.648, 10.6656, 1.0912, 0.0, 0.0, 0.0, 0.0, 0.0]

G=G6

Nu = 30  # Numero di utenti totali

Nc_max = 50  # Numero massimo di cicli
soglia_convergenza = 1  # Soglia di variazione minima per considerare convergenza - soglia 5 per caso 0505

w1=0.1
w2=round(1-w1, 2)
w1_1=0.9
w2_1=round(1-w1_1, 2)


# Carica il file Excel
file_excel = "/Users/giuseppe/Library/CloudStorage/GoogleDrive-giuseppe.sciume01@community.unipa.it/Altri computer/Il mio Laptop /Università/8. SAMOTHRACE/10. Sviluppo EMS/test 10.04.25/profili_utenti_30_3.xlsx"  # Sostituisci con il tuo percorso
dati_excel = pd.read_excel(file_excel, sheet_name="Profili")  # Modifica il nome del foglio se necessario

# Converti in dizionario
profili_utenti = {}
for indice, riga in dati_excel.iterrows():
    nome_utente = f"B{indice+1}"  # Oppure usa una colonna specifica, es. riga['Nome']
    valori = riga.dropna().tolist()[1:]  # Esclude la prima colonna (indice/ID)
    profili_utenti[nome_utente] = valori


# Carica il file Excel
file_excel = "/Users/giuseppe/Library/CloudStorage/GoogleDrive-giuseppe.sciume01@community.unipa.it/Altri computer/Il mio Laptop /Università/8. SAMOTHRACE/10. Sviluppo EMS/test 10.04.25/profili_utenti_30_3.xlsx"  # Sostituisci con il tuo percorso
dati_excel = pd.read_excel(file_excel, sheet_name="Profili_start")  # Modifica il nome del foglio se necessario

# Converti in dizionario
profili_utenti_start = {}
for indice, riga in dati_excel.iterrows():
    nome_utente = f"B{indice+1}"  # Oppure usa una colonna specifica, es. riga['Nome']
    valori = riga.dropna().tolist()[1:]  # Esclude la prima colonna (indice/ID)
    profili_utenti_start[nome_utente] = valori

print("profili_utenti", profili_utenti)
print("profili_utenti_start", profili_utenti_start)


loads = generate_loads(Nu,w1,w2,w1_1,w2_1)


# Mappatura Nu -> utente
def create_nu_to_user(Nu):
    return {i: f"B{i+1}" for i in range(Nu)}

nu_to_user = create_nu_to_user(Nu)

##################### FINE SEZIONE DI DEFINIZIONE UTENTI #####################

start_time = time.time()  # Inizia il timer

###################### CALCOLO CBL TOTALE ###########################

# Funzione per calcolare la CBL totale della comunità
def calcola_cbl_totale(profili_utenti):
    cbl_totale = [0] * 24  # Inizializza la CBL totale a 0 per ogni ora
    for profilo in profili_utenti.values():
        cbl_totale = somma_consumi(cbl_totale, profilo)  # Somma i consumi di ogni utente
    return cbl_totale

B_tot= calcola_cbl_totale(profili_utenti)

B_tot_start= calcola_cbl_totale(profili_utenti_start)


#################### OTTIMIZZAZIONE #####################

# Salva la CBL totale iniziale
B_tot_before = B_tot.copy()
B_tot_cicli = [B_tot.copy()]  # Lista per salvare la CBL dopo ogni ciclo

print("INIZIA L'ALLOCAZIONE")

allocazioni = {}  # Inizializza le allocazioni
convergenza_raggiunta = False  # Flag per la convergenza

for a in range(Nc_max): 
    # Salva la CBL totale prima del ciclo corrente
    B_tot_precedente = B_tot.copy()
    
    # Esegui l'ottimizzazione per ogni utente
    for i in range(Nu):
        profili_utenti_opt, B_tot_opt = ottimizza_energia(i, B_tot, nu_to_user, loads, G, profili_utenti, profili_utenti_start, allocazioni)
    
    # Salva la CBL totale dopo il ciclo corrente
    B_tot_cicli.append(B_tot_opt.copy())


    # Confronto con la soglia di variazione minima
    if np.allclose(B_tot_opt, B_tot_precedente, atol=soglia_convergenza):
        print(f"Convergenza raggiunta al ciclo {a+1}")
        convergenza_raggiunta = True
        profili_utenti_convergenza = profili_utenti_opt.copy()  # Salva i profili degli utenti alla convergenza
        break

if not convergenza_raggiunta:
    print(f"Raggiunto il numero massimo di cicli ({Nc_max}), ma senza convergenza")

# Crea un DataFrame pandas
df5 = pd.DataFrame({
    "Indice": range(len(B_tot_cicli[-1])),  # Colonna indice (0-23)
    "Valori_Btot_alla_convergenza": B_tot_cicli[-1]         # Colonna valori
})


end_time = time.time()  # Ferma il timer
print("Tempo di esecuzione:", end_time - start_time, "secondi")




Ec = np.sum([min(G[h], B_tot_cicli[-1][h]) for h in range(24)])  # Contributo totale della comunità per ogni ora



# Creazione del grafico
ore = range(24)
plt.rcParams.update({'font.size': 14})  # cambia 14 con il valore che preferisci
plt.figure(figsize=(12, 6))

plt.plot([], [], ' ', label=r'N$_u$ = ' + f'{float(Nu):.0f}')  # Usando raw string per LaTeX
plt.plot([], [], ' ', label=f'{Nu/2:.0f}: '+ r'w$_1$ = ' + f'{w1:.1f}, ' +  r'w$_2$ = ' + f'{w2:.1f}')  # Elemento vuoto con solo l'etichetta
plt.plot([], [], ' ', label=f'{Nu/2:.0f}: '+ r'w$_1$ = ' + f'{w1_1:.1f}, ' +  r'w$_2$ = ' + f'{w2_1:.1f}')  # Elemento vuoto con solo l'etichetta

# Linea della CBL iniziale
plt.plot(ore, B_tot_start, label=r'CBL$_{tot}$', linestyle=':', marker='x', color='red')

#plt.plot(ore, DR, label=r'P$_{DR}$', linestyle='-', color='orange')

# Linea della CBL alla convergenza
plt.plot(ore, B_tot_cicli[-1], label=r'CBL$_{tot,conv}$', linestyle='--', marker='o', color='blue')

# Linea della generazione fotovoltaica G1
plt.plot(ore, G6, label='PV Generation', linestyle='-', color='green')
# plt.plot(ore, G1, label='Generazione Fotovoltaica (G1)', linestyle='-', marker='s', color='green')
# Area dell'energia condivisa (minimo tra CBL convergente e generazione PV)



plt.fill_between(ore, 
                 np.minimum(B_tot_cicli[-1], G6), 
                 color='yellow', alpha=0.1, 
                 label=f'Energy Sharing = {Ec:.2f} kWh')


# Impostazione dei tick sull'asse x da 0 a 23
plt.xticks(range(24))

# Impostazioni del grafico
plt.xlabel('Hours')
plt.ylabel('Power (kW)')
#plt.title('Comparison of total REC consumption before and after optimization and PV generation')
plt.legend()
plt.grid()
plt.show()



#print("loads ", allocazioni)