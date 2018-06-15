import pygame, time, collections, random, heapq


pygame.init()
BLACK = (0, 0, 0)  # colores para usar en la ventana
P1_COLOUR = (0, 255, 255)  # color de traza del jugador 1
P2_COLOUR = (255, 0, 255)  # color de traza del jugador 2
moves = {'up':(0, -2), 'down':(0, 2), 'left':(0, -2), 'right':(0, 2)} # diccionario utilitario

# distancia manhattan entre dos nodos
def manhattan(nodeL, nodeR):
    return abs(nodeL[0] - nodeR[0]) + abs(nodeL[1] - nodeR[1])

class Queue: # Clase para acceder facilmente a collections.deque
    def __init__(self):
        self.elements = collections.deque() # nuevo deque (double ended queue)
    
    def empty(self):
        return len(self.elements) == 0 # checar si está vacío
    
    def push(self, x): # encolar elemento x
        self.elements.append(x)
    
    def pop(self): # remover y devolver el elemento en el frente
        return self.elements.popleft()

    def last(self): # ver el último nodo en la fila
        node = self.elements.pop() # lo sacamos
        self.elements.append(node) # lo metemos de vuelta
        return node # lo devolvemos

# Clase Cola de Prioridad (usa heap de Python)
class PriorityQueue:
    # Constructor
    def __init__(self):
        self.elements = []

    # Checa si esta vacía
    def empty(self):
        return len(self.elements) == 0

    # Inserta elemento item con prioridad priority
    def push(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    # regresa el elemento prioritario
    def pop(self):
        return heapq.heappop(self.elements)[1]

# Clase jugador
class Player:
    # Constructor
    def __init__(self, direction, isHuman=False):
        self.direction = direction # direccion como una tupla
        self.isHuman = isHuman # si es humano o AI
        if self.isHuman: # Si es humano lo construimos diferente
            self.x = 50 # con cierta posición
            self.y = height // 2
            self.colour = P1_COLOUR # Y cierto color
        else: # de otro modo es IA y va en otro lado
            self.x = width - 50
            self.y = height // 2
            self.colour = P2_COLOUR # Con otro color
            self.xTarget = 50 # además de valores especiales para seguir su objetivo y crear un camino
            self.yTarget = height // 2
            self.pathTarget = Queue() # como el camino a seguir para derrotar al humano
            self.difficulty = random.randint(1, 2) # dificultad a usar
        self.speed = 1  # velocidad del jugador
        self.boost = False  # si tiene nitro
        self.start_boost = time.time()  # para controlar la medida del nitro
        self.boosts = 3 # cantidad de nitros
        self.rect = pygame.Rect(self.x - 1, self.y - 1, 2, 2)  # rectangulo del jugador

    # metodo para dibujar
    def __draw__(self):
        self.rect = pygame.Rect(self.x - 1, self.y - 1, 2, 2)  # redefine el rectangulo
        pygame.draw.rect(screen, self.colour, self.rect, 0)  # dibuja al jugador en la pantalla

    # actualizar objetivo y camino, IA nada mas
    def updateTarget(self):
        self.xTarget, self.yTarget = p2.x, p2.y # actualiza los objetivos
        # Este punto se supone que es un buen punto para "matar" al enemigo
        if p2.direction == moves['left']:
            self.yTarget -= 2
        elif p2.direction == moves['right']:
            self.yTarget += 2
        elif p2.direction == moves['up']:
            self.xTarget += 2
        elif p2.direction == moves['down']:
            self.xTarget -= 2
        # Uso de la IA buscando caminos
        if self.difficulty == 1:
            self.bfs()
        else:
            self.aSearch()

    # metodo para revisar la direccion de un nodo respecto a otro
    def checkDir(self, target):
        if self.x < target[0]:
            return moves['right']
        if self.x > target[0]:
            return moves['left']
        if self.y < target[1]:
            return moves['down']
        if self.y > target[1]:
            return moves['up']

    # metodo mover para evitar el privado '__move__', como una 'API' para la IA
    def move(self):
        if self.isHuman: # Si es humano que siga normal
            past = (self.x, self.y) 
            self.__move__() # nos movemos normal
            usedBoard[past[0]][past[1]] = True
        else: # si es IA
            if not self.pathTarget.empty(): # mientras haya direcciones a seguir en el camino
                self.direction = self.checkDir(self.pathTarget.pop()) # sigamoslas
            
            self.updateTarget() # actualiza las direcciones y la cola
            # importante! primero calculamos la direccion y luego marcamos el nodo como usado
            past = (self.x, self.y) 
            self.__move__() # nos movemos normal
            usedBoard[past[0]][past[1]] = True

    # Movimiento
    def __move__(self):
        if not self.boost:  # Si no hay nitro
            self.x += self.direction[0]
            self.y += self.direction[1]
        else: # si lo hay
            self.x += self.direction[0] * 2
            self.y += self.direction[1] * 2

    # Nitro
    def __boost__(self): 
        if self.boosts > 0: # si tenemos nitro
            self.boosts -= 1 # quitamos
            self.boost = True # activamos
            self.start_boost = time.time() # y a correr! (0.5s)

    # calcular los vecinos de un nodo dado un tablero prueba
    def computeNeighbors(self, coords, testBoard):
        neighbors = [] # vacía por las dudas
        # Si x > 0 y está vacío el tablero, vamos a la izquierda
        if coords[0] > 0:
            if not usedBoard[coords[0] - 1][coords[1]] and not testBoard[coords[0] - 1][coords[1]]:
                neighbors.append( (coords[0] - 1, coords[1]) )
        # Si y > 0 y está vacío el tablero, vamos arriba
        if coords[1] > 0:
            if not usedBoard[coords[0]][coords[1] - 1] and not testBoard[coords[0]][coords[1] - 1]:
                neighbors.append( (coords[0], coords[1] - 1) )
        # Si x < width y está vacío el tablero, vamos a la derecha
        if coords[0] < width:
            if not usedBoard[coords[0] + 1][coords[1]] and not testBoard[coords[0] + 1][coords[1]]:
                neighbors.append( (coords[0] + 1, coords[1]) )
        # Si y < height y está vacío el tablero, vamos abajo
        if coords[1] < height:
            if not usedBoard[coords[0]][coords[1] + 1] and not testBoard[coords[0]][coords[1] + 1]:
                neighbors.append( (coords[0], coords[1] + 1) )

    # Busqueda de camino con A*
    def aSearch(self):
        testBoard = usedBoard # tablero de prueba para inundar
        neighbors = PriorityQueue() # Creamos un heap o cola de prioridad
        neighbors.push((self.x, self.y), 0) # metemos nuestro nodo inicial
        pathGenerated = {} # Camino creado
        costUpTo = {} # Costo generado
        pathGenerated[(self.x, self.y)] = None # Inicializamos el camino
        costUpTo[(self.x, self.y)] = 0 # y los costos
        while not neighbors.empty(): # Mientras haya vecinos
            current = neighbors.pop() # obtenemos el mejor vecino
            testBoard[current[0]][current[1]] = True # lo marcamos usado
            if current == (self.xTarget, self.yTarget): # si es el objetivo nos salimos
                break
            frontier = self.computeNeighbors(current, testBoard) # Si no, le sacamos los vecinos
            if frontier: # si no está vacía
                for node in frontier: # Y para cada uno
                    newCost = costUpTo[node] + 1 # Costo de viajar al siguiente es 1
                    if node not in costUpTo or newCost < costUpTo[node]: # si el nodo no ha sido visitado o el costo es menor
                        costUpTo[node] = newCost # vamos a recorrerlo y añadirlo
                        priority = newCost + manhattan(node, (self.xTarget, self.yTarget)) # creamos su prioridad
                        neighbors.push(node, priority) # lo metemos en el heap
                        pathGenerated[node] = current # y en el camino
        
        for key in pathGenerated: # metemos el camino
            self.pathTarget.push(key) # para que lo visitemos


    # Busqueda de camino con BFS
    def bfs(self): # calcula el camino a seguir
        testBoard = usedBoard # creamos el tablero de prueba para inundar
        neighbors = Queue() # cola de nodos a visitar
        neighbors.push((self.x, self.y)) # metemos el nodo actual
        while not neighbors.empty(): # mientras haya nodos por inundar
            current = neighbors.pop() # obtenemos el nodo de la cola
            self.pathTarget.push(current)
            # Si llegamos al objetivo, terminar y salir
            if current[0] == self.xTarget and current[1] == self.yTarget:
                return
            testBoard[current[0]][current[1]] = True # Marcar como usado
            frontier = self.computeNeighbors(current, testBoard) # Obtener vecinos del nodo actual
            if frontier: # actualizar la cola
                for node in frontier:
                    neighbors.push(node)

# para crear un nuevo juego
def new_game():
    new_p1 = Player((2, 0)) # IA de dificultad aleatoria
    new_p2 = Player((-2, 0), True) # Jugador
    return new_p1, new_p2


width, height = 600, 660  # dimensiones de la ventana
usedBoard = [[False] * width for _ in range(height)] # para uso con la BFS y la A*
offset = height - width  # espacio vertical extra
screen = pygame.display.set_mode((width, height))  # crea la ventana
pygame.display.set_caption("Tron")  # coloca el titulo del juego

font = pygame.font.Font(None, 72) # cambiamos el tamaño de la fuente

clock = pygame.time.Clock()  # para regular los FPS
check_time = time.time()  # para revisar colisiones en tiempo y forma

objects = list()  # lista de todosl os jugadores
path = list()  # lista de todos los caminos ya recorridos
p1 = Player((2, 0))  # crea IA
p2 = Player((-2, 0), True) # crea al jugador
objects.append(p1) # metemos la IA
path.append((p1.rect, '1')) # metemos su objeto en el camino
objects.append(p2) # ahora ocn el jugador
path.append((p2.rect, '2'))

player_score = [0, 0]  # puntuaciones

wall_rects = [pygame.Rect([0, offset, 15, height]) , pygame.Rect([0, offset, width, 15]),\
              pygame.Rect([width - 15, offset, 15, height]),\
              pygame.Rect([0, height - 15, width, 15])]  # los muros de fuera de la ventana
# variables de uso
done = False
new = False

while not done:
    for event in pygame.event.get():  # obtener todos los eventos ocurridos
        if event.type == pygame.QUIT:  # cerrar el juego
            done = True
        elif event.type == pygame.KEYDOWN:  # tecla presionada
            # Movimientos del jugador
            # >Flechas para moverse
            # >Nitro con shift derecho

            # Esta parte se puede activar para 2 jugadores, solo se descomenta y juega con WASD y TAB
            # if event.key == pygame.K_w and objects[0].direction != (0, 2):
            #     objects[0].direction = (0, -2)
            # elif event.key == pygame.K_s and objects[0].direction != (0, -2):
            #     objects[0].direction = (0, 2)
            # elif event.key == pygame.K_a and objects[0].direction != (2, 0):
            #     objects[0].direction = (-2, 0)
            # elif event.key == pygame.K_d and objects[0].direction != (-2, 0):
            #     objects[0].direction = (2, 0)
            # elif event.key == pygame.K_TAB:
            #     objects[0].__boost__()
            
            # Aquí comienzan los movimientos del jugador
            if event.key == pygame.K_UP and objects[1].direction != (0, 2):
                objects[1].direction = (0, -2)
            elif event.key == pygame.K_DOWN and objects[1].direction != (0, -2):
                objects[1].direction = (0, 2)
            elif event.key == pygame.K_LEFT and objects[1].direction != (2, 0):
                objects[1].direction = (-2, 0)
            elif event.key == pygame.K_RIGHT and objects[1].direction != (-2, 0):
                objects[1].direction = (2, 0)
            elif event.key == pygame.K_RSHIFT:
                objects[1].__boost__()

    screen.fill(BLACK)  # limpia la pantalla

    for r in wall_rects: # para cada rectangulo
        pygame.draw.rect(screen, (42, 42, 42), r, 0)  # dibuja los muros

    for obj in objects:
        if time.time() - obj.start_boost >= 0.5:  # limita el nitro a 0.5s
            obj.boost = False

        # Revisar colisiones
        if (obj.rect, '1') in path or (obj.rect, '2') in path or obj.rect.collidelist(wall_rects) > -1:  # choco con el camino o muro
            # previene chocar consigo mismo
            if (time.time() - check_time) >= 0.1:
                check_time = time.time()
                #puntuaciones
                if obj.colour == P1_COLOUR:
                    player_score[1] += 1
                else:
                    player_score[0] += 1

                new = True
                new_p1, new_p2 = new_game()
                objects = [new_p1, new_p2]
                path = [(p1.rect, '1'), (p2.rect, '2')]
                break
        else:  # sin atravesar
            path.append((obj.rect, '1')) if obj.colour == P1_COLOUR else path.append((obj.rect, '2'))

        obj.__draw__()
        obj.move()

    for r in path:
        if new is True:  # vacía el camino, evita glitches
            path = []
            new = False
            break
        if r[1] == '1':
            pygame.draw.rect(screen, P1_COLOUR, r[0], 0)
        else:
            pygame.draw.rect(screen, P2_COLOUR, r[0], 0)

    # muestra las puntuaciones
    if player_score[0] > 1:
        done = True
    score_text = font.render('{0} : {1}'.format(player_score[0], player_score[1]), 1, (255, 153, 51))
    score_text_pos = score_text.get_rect()
    score_text_pos.centerx = width // 2
    score_text_pos.centery = offset // 2
    screen.blit(score_text, score_text_pos)

    pygame.display.flip()  # voltea el display
    clock.tick(60)  # regula los FPS

pygame.quit()