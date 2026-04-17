# Logistics Optimization: Facility Location & TSP Solver

Questo repository contiene un progetto di ottimizzazione per una compagnia di spedizioni, sviluppato per l'esame di **Automated Decision Making (ADM)**. Il codice affronta il problema di ottimizzare la distribuzione dei pacchi combinando tecniche di clustering e programmazione lineare intera (MILP).

## Panoramica
L'obiettivo è minimizzare i costi operativi e l'impatto ambientale attraverso due fasi di ottimizzazione:
1. **Strategica**: Selezione delle migliori posizioni per le facility (magazzini) tra 50 siti candidati.
2. **Operativa**: Pianificazione del percorso di consegna ottimo (Traveling Salesman Problem) per ogni magazzino verso i propri punti di ritiro.

## Stack Tecnologico
* **Optimization**: Gurobi Optimizer (Modellazione MILP e TSP).
* **Machine Learning**: Scikit-learn (MiniBatchKMeans).
* **Data Analysis**: NumPy, Matplotlib.
* **Linguaggio**: Python.

## Come Funziona

### 1. Clustering della Domanda
Il sistema genera un dataset sintetico di **50.000 punti di consegna**. Per rendere il problema trattabile computazionalmente, viene utilizzato l'algoritmo **K-means** per aggregare la domanda in circa 1.000 centroidi (punti di ritiro). Il numero ottimale di cluster è scelto automaticamente tramite l'euristica dell'Elbow Method.

### 2. Facility Location (MILP)
Viene risolto un modello matematico su **Gurobi** per:
* Attivare un numero massimo di 8 facility tra le 50 disponibili.
* Assegnare ogni punto di ritiro alla facility più vicina, minimizzando la distanza totale percorsa.

### 3. Rotte di Consegna (TSP)
Per ogni facility attivata, il codice calcola il percorso di consegna più breve che tocca tutti i punti assegnati. Il modello include un algoritmo di **Subtour Elimination** dinamico per garantire che il percorso sia un unico ciclo chiuso senza giri isolati.

## Risultati
Il progetto visualizza graficamente:
* La mappa della domanda e la posizione dei magazzini.
* L'assegnazione dei punti alle diverse zone.
* I percorsi TSP ottimali per ogni zona di competenza.

## Struttura
* `main.py`: Script unico che gestisce la generazione dati, il clustering e i modelli di ottimizzazione.
* `Esame_ADM_Filippo_Biagini.pdf`: Relazione consegnata.
