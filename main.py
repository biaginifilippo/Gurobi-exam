import random
import sys
import matplotlib.pyplot as plt
import numpy as np
import math
from sklearn.cluster import MiniBatchKMeans as KMeans
import gurobipy as gp
from gurobipy import GRB


def plot_elbow(inertia, x):
    p = []
    diff = []
    min_j = 0
    for i in range(len(inertia) - 1):
        p.append(inertia[i] - inertia[i + 1])
    for i in range(len(p) - 1):
        diff.append(p[i] - p[i + 1])
    for i in range(len(diff)):
        if diff[i] > 0.5:
            min_j = i + 1
    if inertia[-2] - inertia[-1] > 1.2:
        min_j = len(inertia) - 1
    #print(str("diff" + str(diff)))
    #print(str("inertia" + str(inertia)))
    plt.plot(x, inertia)
    plt.scatter(x, inertia)
    plt.scatter(x[min_j], inertia[min_j], c='Red', s=60)
    plt.title("Inertia")
    plt.show()
    return min_j


def kmeans_func(n_clusters, x):
    kmeans = KMeans(n_clusters=n_clusters, n_init=10)
    labels = kmeans.fit_predict(x)
    centers = kmeans.cluster_centers_
    inertia = kmeans.inertia_
    return centers, labels, inertia


def costumer_assignment(centres, max_facilities, possible_facilities):
    plot_x_c = []
    plot_y_c = []
    plot_x_f = []
    plot_y_f = []
    """plot di tutti centri e tutte le facilities"""
    for n, [i, j] in enumerate(centres):
        (x, y) = (i, j)
        centres[n] = (x, y)
        plot_x_c.append(x)
        plot_y_c.append(y)
    plt.scatter(plot_x_c, plot_y_c, c='Blue', s=10)
    for (i, j) in possible_facilities:
        (x, y) = (i, j)
        plot_x_f.append(x)
        plot_y_f.append(y)
    plt.scatter(plot_x_f, plot_y_f, c='Green', marker='*', s=60)
    plt.title("Problem Map")
    plt.show()
    model = gp.Model()
    y = model.addVars(range(len(possible_facilities)), vtype=GRB.BINARY, name='y')
    distances = {}
    for i, centre in enumerate(centres):
        for j, facility in enumerate(possible_facilities):
            distances[i, j] = math.dist(centre, facility)

    assignments = model.addVars(distances, vtype=GRB.BINARY, name="assignments")
    """Vincolo, ongi punto deve essere assegnato una e una sola volta"""
    model.addConstrs(
        gp.quicksum(assignments[i, j] for j in range(len(possible_facilities))) == 1 for i in range(len(centres)))
    """vincolo che impone la coerenza tra le facility y e gli assegnamenti"""
    for i, centre in enumerate(centres):
        model.addConstrs(assignments[i, j] <= y[j] for j in range(len(possible_facilities)))
    """vincolo sul numero massimo di facilities utilizzabili"""
    model.addConstr(gp.quicksum(y[j] for j in range(len(possible_facilities))) <= max_facilities, name="max_facilities")
    model.setObjective(
        gp.quicksum(
            gp.quicksum(
                distances[i, j] * assignments[i, j] for i in range(len(centres))) for j in
            range(len(possible_facilities))),
        GRB.MINIMIZE)
    model.optimize()
    # print(model.getJSONSolution())
    model.write("exam.lp")
    """Estrazione dei dati dal modello"""
    values = [v.x for v in assignments.values()]
    values_y = [v.x for v in y.values()]
    np_y = np.array(values_y)
    np_assignments = np.array(values)
    np_assignments = np.reshape(np_assignments, (len(centres), len(possible_facilities)))
    np_assignments = np_assignments.T

    indexes = []
    yy = []
    for i, elem in enumerate(np_y):
        if elem == 0:
            indexes.append(i)
        else:
            yy.append(i)
    np_assignments = np.delete(np_assignments, indexes, axis=0)
    #print(np_assignments.shape)
    print(str("Selected facilities:" + str(yy)))
    """
        Plot di quali facilities ho scelto
    """
    plot_x_c = []
    plot_y_c = []

    for n, [i, j] in enumerate(centres):
        (x, y) = (i, j)
        centres[n] = (x, y)
        plot_x_c.append(x)
        plot_y_c.append(y)
    plt.scatter(plot_x_c, plot_y_c, c='Blue', s=10)
    plt.scatter(plot_x_f, plot_y_f, c='Green', marker='*', s=20)
    plot_x_fs = []
    plot_y_fs = []
    for i in yy:
        (x, y) = possible_facilities[i]
        plot_x_fs.append(x)
        plot_y_fs.append(y)
    plt.scatter(plot_x_fs, plot_y_fs, c='Red', marker='*', s=100)
    plt.title("Best facilities")
    plt.show()
    return np_assignments, yy, distances


def subtour_elim(arcs, n, tsp_list, number):
    visited = [False for i in range(n)]
    tsp_x =[]
    tsp_y =[]
    shortestTour = range(n + 1)  # initial length has 1 more city
    for (i, j) in arcs:
        """guardo se passo su un nodo in cui sono già passato"""
        if not visited[i]:
            isave = i
            narcs = 1
            visited[i] = True
            Tour = [i]
            while j != isave:
                neighbor = [kk for (jj, kk) in arcs.select(j, '*') if kk != i]
                k = neighbor[0]

                visited[j] = True
                Tour.append(j)
                i = j
                j = k
                narcs = narcs + 1
            if narcs < len(shortestTour):
                shortestTour = Tour
    """Se non ho trovato alcun subtour plotto il percorso ottimo"""
    if narcs == len(tsp_list):
        for i in shortestTour:
            tsp_x.append(tsp_list[i][0])
            tsp_y.append(tsp_list[i][1])
        plt.scatter(tsp_x, tsp_y, c="Red", s=20)
        plt.plot(tsp_x, tsp_y)
        plt.title(str("Optimal route for Facility number: ") + str(number))
        plt.show()
    return shortestTour


def tsp(tsp_list, number, order):
    model = gp.Model()
    dist = {}
    n = len(tsp_list)
    """Creo un dizionario di distanze"""
    for i, centre1 in enumerate(tsp_list):
        for j, centre2 in enumerate(tsp_list):
            if j != i:
                dist[i, j] = math.dist(centre1, centre2)
    edges = [(i, j) for (i, j) in dist.keys() if i != j]
    vars = model.addVars(edges, vtype=GRB.BINARY, name='e')

    for i, j in vars.keys():
        vars[j, i] = vars[i, j]

    """aggiungo il vincolo di grado 2 e la funzione obiettivo"""
    model.addConstrs(vars.sum(i, '*') == 2 for i in range(n))
    objective = gp.quicksum(vars[i, j] * dist[i, j] for i, _ in enumerate(tsp_list) for j, _ in enumerate(tsp_list) if i != j)
    model.setObjective(objective, GRB.MINIMIZE)

    tourLength = 0
    cutCount = 0
    """Ripeto il ciclo while finchè non ho eliminato tutti i subtour"""
    while (tourLength < n):
        model.optimize()
        vals = model.getAttr('x', vars)
        selected_edges = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)
        """chiamo la funzione per eliminare i subtour"""
        tour = subtour_elim(selected_edges, n, tsp_list, number)

        tourLength = len(tour)
        """Se mi ha ritornato un tour di lunghezza inferiore alla massima devo eliminare gli archi del subtour"""
        if tourLength < n:
            model.addConstr(gp.quicksum(vars[i, j] for i in tour for j in tour if tour.index(j) > tour.index(i))
                        <= len(tour) - 1)
            cutCount = cutCount + 1
    model.write(str("tsp_num_" + str(order) +".lp"))

    return


def main():
    """parametri per inizializzazione"""
    num_customers = 50000
    num_candidate_facilities = 50
    max_facilities = 8
    num_gaussians = 10
    tries = [800, 950, 1100, 1250, 1400]
    """inizializzazione dell'istanza"""
    customers_per_gaussian = np.random.multinomial(num_customers,
                                                   [1 / num_gaussians] * num_gaussians)
    customer_locs = []
    for num_customers_per_gaussian in customers_per_gaussian:
        # each center coordinate in [-0.5, 0.5]
        center = (random.random() - 0.5, random.random() - 0.5)
        customer_locs += [
            (random.gauss(0, .1) + center[0], random.gauss(0, .1) + center[1])
            for _ in range(num_customers_per_gaussian)
        ]
    facility_locs = [
        (random.random() - 0.5, random.random() - 0.5)
        for _ in range(num_candidate_facilities)
    ]
    inertia_list = []
    labels_list = []
    centres_list = []
    """Svolgo varie volte il kmeans e conservo tutti i risultati"""
    for i in tries:
        print(str(i) + "...")
        c, l, n = kmeans_func(i, customer_locs)
        centres_list.append(c)
        labels_list.append(l)
        inertia_list.append(n)
    """Utilizzo l'euristica dell'elbow per scegliere il miglior numero di centroidi"""
    selected_index = plot_elbow(inertia_list, tries)
    centres = centres_list[selected_index]
    """Assegno i centroidi alle facilities seguendo una metrica di minimizzazione della distanza"""
    assignments, selected_facilities, distances = costumer_assignment(centres, max_facilities, facility_locs)
    # assignments e facilities sono np array
    # assignments ha shape (len(selected_facilicies), n_centres)
    tsp_list = []
    plot_x_c = []
    plot_y_c = []
    plot_tsp_x = []
    plot_tsp_y = []
    """Esecusione di num_selected_facilities TSP differenti, prima creo la lista relativa al tsp e poi chiamo la funzione"""
    for i, facility in enumerate(selected_facilities):
        tsp_list.append(facility_locs[facility])
        for j, centre in enumerate(assignments[i]):
            if centre == 1:
                tsp_list.append(centres[j])
        """Esecuzione di vari plot per mostrare in modo chiaro e definito cosa sta accadendo"""
        for [x, y] in centres:
            plot_x_c.append(x)
            plot_y_c.append(y)
        for (x, y) in tsp_list:
            plot_tsp_x.append(x)
            plot_tsp_y.append(y)
        plt.scatter(plot_x_c, plot_y_c, c='Blue', s=10)
        plt.scatter(plot_tsp_x, plot_tsp_y, c='Red', s=20)
        plt.scatter(facility_locs[facility][0], facility_locs[facility][1], marker='*', c='Green', s=40)
        plt.title(str("Facility number: " + str(facility)))
        plt.show()
        tsp(tsp_list, facility, i)
        tsp_list = []
        plot_x_c = []
        plot_y_c = []
        plot_tsp_x = []
        plot_tsp_y = []

    return


if __name__ == "__main__":
    main()
    sys.exit()
