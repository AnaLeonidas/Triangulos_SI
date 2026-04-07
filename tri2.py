import networkx as nx
import math
import random
import matplotlib.pyplot as plt
from collections import deque # Adicionado para a fila da BFS

def vertice_no_triangulo(vertice, v1, v2, v3):
    def sinal(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    orientacao_aresta1 = sinal(vertice, v1, v2)
    orientacao_aresta2 = sinal(vertice, v2, v3)
    orientacao_aresta3 = sinal(vertice, v3, v1)

    tem_negativo = (orientacao_aresta1 < 0) or (orientacao_aresta2 < 0) or (orientacao_aresta3 < 0)
    tem_positivo = (orientacao_aresta1 > 0) or (orientacao_aresta2 > 0) or (orientacao_aresta3 > 0)

    return not (tem_negativo and tem_positivo)

def triangulos_colidem(tri1, tri2):
    for vertice in tri1:
        if vertice_no_triangulo(vertice, tri2[0], tri2[1], tri2[2]):
            return True
    for vertice in tri2:
        if vertice_no_triangulo(vertice, tri1[0], tri1[1], tri1[2]):
            return True
    return False

def segmentos_se_interceptam(p1, p2, p3, p4):
    def orientacao(a, b, c):
        val = (b[1] - a[1]) * (c[0] - b[0]) - (b[0] - a[0]) * (c[1] - b[1])
        if abs(val) < 1e-9: return 0  
        return 1 if val > 0 else 2 

    o1 = orientacao(p1, p2, p3)
    o2 = orientacao(p1, p2, p4)
    o3 = orientacao(p3, p4, p1)
    o4 = orientacao(p3, p4, p2)

    if o1 != o2 and o3 != o4:
        return True
    return False

def aresta_livre(p_inicio, p_fim, obstaculos):
    p_medio = ((p_inicio[0] + p_fim[0]) / 2, (p_inicio[1] + p_fim[1]) / 2)
    
    for tri in obstaculos:
        if p_inicio in tri and p_fim in tri:
            return False
            
        if vertice_no_triangulo(p_medio, tri[0], tri[1], tri[2]):
            return False

        bordas = [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])]
        for b1, b2 in bordas:
            if p_inicio == b1 or p_inicio == b2 or p_fim == b1 or p_fim == b2:
                continue
            if segmentos_se_interceptam(p_inicio, p_fim, b1, b2):
                return False
    return True

# --- NOVA FUNÇÃO: BUSCA EM LARGURA ---
def busca_em_largura(grafo, inicio, fim):
    fila = deque([inicio])
    visitados = {inicio: None} 

    while fila:
        atual = fila.popleft()
        if atual == fim:
            caminho = []
            while atual is not None:
                caminho.append(atual)
                atual = visitados[atual]
            return caminho[::-1]

        for vizinho in grafo.neighbors(atual):
            if vizinho not in visitados:
                visitados[vizinho] = atual
                fila.append(vizinho)
    return None

def criar_cenario(limite_x, limite_y, qtd_obstaculos, lado_tri):
    G = nx.Graph()
    inicio = (0, 0)
    destino = (limite_x, limite_y)
    G.add_node(inicio)
    G.add_node(destino)
    
    h_tri = lado_tri * (math.sqrt(3) / 2)
    obstaculos_finalizados = [] 
    todos_vertices = [inicio, destino]

    tentativas_max = qtd_obstaculos * 10
    tentativas = 0

    while len(obstaculos_finalizados) < qtd_obstaculos and tentativas < tentativas_max:
        tentativas += 1
        rx = random.uniform(3, limite_x - lado_tri - 3)
        ry = random.uniform(3, limite_y - h_tri - 3)
        
        v1, v2, v3 = (round(rx, 2), round(ry, 2)), (round(rx + lado_tri, 2), round(ry, 2)), (round(rx + lado_tri/2, 2), round(ry + h_tri, 2))
        novo_tri = (v1, v2, v3)

        if not any(triangulos_colidem(novo_tri, obs) for obs in obstaculos_finalizados):
            obstaculos_finalizados.append(novo_tri)
            todos_vertices.extend([v1, v2, v3])
    
    for v in todos_vertices:
        G.add_node(v)

    for i in range(len(todos_vertices)):
        for j in range(i + 1, len(todos_vertices)):
            p1, p2 = todos_vertices[i], todos_vertices[j]
            if aresta_livre(p1, p2, obstaculos_finalizados):
                dist = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                G.add_edge(p1, p2, weight=dist)

    return G, inicio, destino, todos_vertices, obstaculos_finalizados

# --- PARÂMETROS ---
LARGURA, ALTURA = 100, 100
QUANTIDADE = 100
LADO = 7

G, start, end, vertices_para_desenho, lista_triangulos = criar_cenario(LARGURA, ALTURA, QUANTIDADE, LADO)

# EXECUTANDO A BUSCA
caminho_encontrado = busca_em_largura(G, start, end)

pos = {n: n for n in G.nodes()}
plt.figure(figsize=(10, 10))
plt.axvline(0, color='black', linewidth=1.2)
plt.axhline(0, color='black', linewidth=1.2)
plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)

# 1. Desenha todas as arestas possíveis (em vermelho clarinho como estava)
nx.draw_networkx_edges(G, pos, edge_color='tomato', alpha=0.4, width=1)

# 2. SE encontrar caminho, pinta de AZUL por cima
if caminho_encontrado:
    arestas_caminho = [(caminho_encontrado[i], caminho_encontrado[i+1]) for i in range(len(caminho_encontrado)-1)]
    nx.draw_networkx_edges(G, pos, edgelist=arestas_caminho, edge_color='blue', width=3, label='Caminho Encontrado')

nx.draw_networkx_nodes(G, pos, nodelist=vertices_para_desenho, node_color='orange', node_size=1)
nx.draw_networkx_nodes(G, pos, nodelist=[start], node_color='green', node_size=150, label='Origem (0,0)')
nx.draw_networkx_nodes(G, pos, nodelist=[end], node_color='blue', node_size=150, label=f'Destino ({LARGURA},{ALTURA})')

for tri in lista_triangulos:
    polygon = plt.Polygon(tri, closed=True, facecolor='blue', edgecolor='navy', alpha=0.4)
    plt.gca().add_patch(polygon)

qtd_gerada = len(lista_triangulos)
plt.title(f"Grafo de Visibilidade: {qtd_gerada}/{QUANTIDADE} Obstáculos | BFS em Azul", fontsize=14, fontweight='bold')

margem = 1
plt.xlim(-margem, LARGURA + margem)
plt.ylim(-margem, ALTURA + margem)
plt.xlabel("Eixo X (Horizontal)", fontsize=12)
plt.ylabel("Eixo Y (Vertical)", fontsize=12)
plt.legend(loc='upper left')
plt.tight_layout() 
plt.show()