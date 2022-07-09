# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import random

ONE_MAX_LENGTH = 100    #Длина хромосомы (количество коробок в JSON)

POPULATION_SIZE = 200   #Количество индивидуумов в популяции
P_CROSSOVER = 0.9       #Вероятность скрещивания
P_MUTATION = 0.1        #Вероятность мутации
MAX_GENERATION = 50     #Максимальное количество поколений

class FitnessMax():             #Класс для подсчета приспособленности индивида
    def __init__(self):
        self.values = [0]

class Individual(list):         #Класс реализующий индвида (в виде списка)
    def __init__(self,*args):
        super().__init__(*args)
        self.fitness = FitnessMax()

def oneMaxFitness(individual):          #Расчет приспособленности конкретного индивида
    return sum(individual),             #Возвращать должно что то в духе return volume(individual)/volume(cargo_space)
   

def individualCreator():                 #Функция создающая индивида
    return Individual([random.randint(0, 1) for i in range(ONE_MAX_LENGTH)])

def populationCreator(n = 0):
    return list([individualCreator() for i in range(n)])



population = populationCreator(POPULATION_SIZE)  #Создание популяции
generationCounter = 0                            #Счетчик поколений

fitnessValues = list(map(oneMaxFitness,population)) #Список из преспособленностей особей из текущей популяции

for individual, fitnessValue in zip(population,fitnessValues):
    individual.fitness.values = fitnessValue

maxFitnessValues = []
meanFitnessValues = []

def clone(value):
    ind = Individual(value[:])
    ind.fitness.values = value.fitness.values[0]
    return ind


def selTournament(population, p_len):           #Турнирный отбор из трех
    offspring = []                              # новый список из отобранных особей
    for n in range(p_len):
        i1 = i2 = i3 = 0
        while i1 == i2 or i2 == i3 or i1 == i3:
            i1,i2,i3 = random.randint(0,p_len-1), random.randint(0,p_len-1),random.randint(0,p_len-1)

        offspring.append(max([population[i1], population[i2], population[i3]], key=lambda ind:ind.fitness.values[0]))
    return offspring


def cxOnePont(child1, child2):
    s = random.randint(2, len(child1) - 3)
    child1[s:], child2[s:] = child2[s:], child1[s:]


def mutFlip(mutant, indpb = 0.01):
    for indx in range(len(mutant)):
        if random.random() < indpb:
            mutant[indx] = 0 if mutant[indx] == 1 else 1

fitnessValues = [individual.fitness.values[0] for individual in population]  #значения приспособленности особей к данной популяции

while max(fitnessValues)<ONE_MAX_LENGTH  or generationCounter < MAX_GENERATION :
    generationCounter+=1
    offspring = selTournament(population, len(population))
    offspring = list(map(clone,offspring))

    for child1, child2 in zip(offspring[::2],offspring[1::2]):
        if random.random() < P_CROSSOVER:
            cxOnePont(child1, child2)

    for mutant in offspring:
        if random.random()<P_MUTATION:
            mutFlip(mutant, indpb=1.0/ONE_MAX_LENGTH)

    freshFitnessValues = list(map(oneMaxFitness, offspring))

    for individual, fitnessValue in zip(offspring, freshFitnessValues):
        individual.fitness.values = fitnessValue

    population[:] = offspring

    fitnessValues = [ind.fitness.values[0] for ind in population]

    maxFitness = max(fitnessValues)
    meanFitness = sum(fitnessValues) / len(population)
    maxFitnessValues.append(maxFitness)
    meanFitnessValues.append(meanFitness)
    print(f"Поколение {generationCounter}: Макс приспособ. = {maxFitness}, Средняя приспособ.= {meanFitness}")

    best_index = fitnessValues.index(max(fitnessValues))
    print("Лучший индивидуум = ", *population[best_index], "\n")




