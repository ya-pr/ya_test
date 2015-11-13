#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

import os

import lem
from common_functions import pretty_json

### Часть 0 (подготовительная).
# Для работы нам понадобятся раздельные файлы с запросами и весами.
# Создадим их из нашего входного файла.
# Сохраняем столбцы в отдельные файлы
path_r = 'data/'
file_data_name = path_r + 'input.tsv'
file_query_name = path_r + 'queries.txt'
file_weight_name = path_r + 'weights.txt'

with open(file_data_name, 'r') as file_data, \
        open(file_query_name, 'w') as file_query, \
        open(file_weight_name, 'w') as file_weight:
    for line in file_data:
        line = line.rstrip('\n').split('\t')
        print(line[1], file=file_query)
        print(line[0], file=file_weight)

print('Done Part0')

### Часть 1.
# Создаём json-файл с леммами. Для этого передаём функции lem файл с запросами,
# файл для записи json-вывода, путь до программы и параметры запуска.
path_w = 'output/'
if not os.path.exists(path_w):
    os.makedirs(path_w)
file_json_name = path_w + 'lems.json'
mystem = '/Applications/mystem'
params = ['-cldige', 'utf-8', '--format', 'json']

with open(file_query_name, 'r') as file_query, \
        open(file_json_name, 'w') as file_json:
    lem.lem(file_query, file_json, mystem=mystem, params=params)

print('Done Part1')

# Теперь у нас есть json-файл с леммами.
# Все дальнейшие операции мы будем делать с ним.

### Часть 2.
# Далее нам необходимо выбрать параметры, по которым мы будем отбирать леммы.
# Тут есть только 2 опции:
# bastard - добавлять ли леммы, в распознании которых Mystem не уверен?
# non_cyrillic - добавлять ли леммы с не кириллическими символами?
bastard = True
non_cyrillic = True

# Чтобы наглядно посмотреть, какие леммы будут отобраны для каждой строки можем
# прогнать каждую строку сначала через парсер, а потом через фильтр.
# В итоге получится текстовый файл с леммами.
file_lems_name = path_w + 'lems.txt'

with open(file_json_name, 'r') as file_json, \
        open(file_lems_name, 'w') as file_lems:
    for line in file_json:
        # парсим строку из json-файла
        line_parse = lem.json_parse(line)
        # фильтруем с учетом наших параметров
        words = lem.lem_filter(line_parse, include_bastard=bastard,
                               include_non_cyrillic=non_cyrillic)
        # lem_filter возвращает всю информацию о слове,
        # но нам нужна только лемма
        lems = [word['lex'] for word in words]
        # сохраняем в файл
        print(' '.join(lems), file=file_lems)

print('Done check lems')

# Теперь мы можем переходить к подсчёту узлов и рёбер и к созданию файлов для
# построения графа в Gephi.

### Часть 2.1.
# Для построения узлов и рёбер у нас имеются две одноименные функции:
# build_node_dict и build_edge_dict. Обе на вход принимают json-файл с леммами,
# файл с весами (необязательный аргумент) и параметры отбора лемм,
# рассмотренные ранее. Если не указать файл с весами, то каждой строке будет
# присвоен единичный вес.

file_nodes_name = path_w + 'nodes.csv'
file_edges_name = path_w + 'edges.csv'
file_nodes_json_name = path_w + 'nodes.json'
file_edges_json_name = path_w + 'edges.json'

# Создаём узлы
with open(file_json_name, 'r') as file_json, \
        open(file_weight_name, 'r') as file_weight, \
        open(file_nodes_name, 'w') as file_nodes, \
        open(file_nodes_json_name, 'w') as file_nodes_json:
    # создаём словарь узлов
    node_dict = lem.build_node_dict(file_json, weights=file_weight,
                                    include_bastard=bastard,
                                    include_non_cyrillic=non_cyrillic)
    # записываем узлы в файл для Gephi
    lem.write_node_dict(file_nodes, node_dict)
    # отдельно сохраняем json-версию словаря узлов (для отладки)
    pretty_json(node_dict, file_nodes_json)

# Создаём рёбра
with open(file_json_name, 'r') as file_json, \
        open(file_weight_name, 'r') as file_weight, \
        open(file_edges_name, 'w') as file_edges, \
        open(file_edges_json_name, 'w') as file_edges_json:
    # создаём словарь рёбер
    edge_dict = lem.build_edge_dict(file_json, weights=file_weight,
                                    include_bastard=bastard,
                                    include_non_cyrillic=non_cyrillic)
    # записываем рёбра в файл для Gephi
    lem.write_edge_dict(file_edges, edge_dict)
    # отдельно сохраняем json-версию словаря рёбер (для отладки)
    edges = {' - '.join(edge): count for edge, count in edge_dict.items()}
    pretty_json(edges, file_edges_json)

print('Done Part2.1')

### Часть 2.2.
# Чтобы получить узлы и рёбра без учёта веса запросов (то есть по
# формулировкам), просто не будем передавать файл с весом в функции
# построения узлов и рёбер.
path_w_form = path_w + 'По формулировкам/'
if not os.path.exists(path_w_form):
    os.makedirs(path_w_form)
file_nodes_name = path_w_form + 'nodes.csv'
file_edges_name = path_w_form + 'edges.csv'
file_nodes_json_name = path_w_form + 'nodes.json'
file_edges_json_name = path_w_form + 'edges.json'

# Создаём узлы
with open(file_json_name, 'r') as file_json, \
        open(file_nodes_name, 'w') as file_nodes, \
        open(file_nodes_json_name, 'w') as file_nodes_json:
    node_dict = lem.build_node_dict(file_json,
                                    include_bastard=bastard,
                                    include_non_cyrillic=non_cyrillic)
    lem.write_node_dict(file_nodes, node_dict)
    pretty_json(node_dict, file_nodes_json)

# Создаём рёбра
with open(file_json_name, 'r') as file_json, \
        open(file_edges_name, 'w') as file_edges, \
        open(file_edges_json_name, 'w') as file_edges_json:
    edge_dict = lem.build_edge_dict(file_json,
                                    include_bastard=bastard,
                                    include_non_cyrillic=non_cyrillic)
    lem.write_edge_dict(file_edges, edge_dict)
    edges = {' - '.join(edge): count for edge, count in edge_dict.items()}
    pretty_json(edges, file_edges_json)

print('Done Part2.2')

### Часть 2.3.
# Если мы хотим получить узлы и рёбра не из всего входного файла, а только из
# какого-то топа, то просто отбираем соответствующие N строк из json-файла
# с леммами и из файла с весами. И даём отобранные строки на вход
# уже использовавшимся ранее функциям.

# Отбираем строки
top = 1000
lines = []  # отобранные строки
weights = []  # отобранные веса
line_count = 0  # счётчик прочитанных строк
with open(file_json_name, 'r') as file_json, \
        open(file_weight_name, 'r') as file_weight:
    for (line, weight) in zip(file_json, file_weight):
        if line_count > top:
            break
        lines.append(line)
        weights.append(weight)
        line_count += 1

# После того, как мы отобрали строки, делаем те же процедуры,
# что и в части 2.1, но на вход вместо полных файлов даём эти строки
path_w_form = path_w + 'Топ-%s/' % top
if not os.path.exists(path_w_form):
    os.makedirs(path_w_form)
file_nodes_name = path_w_form + 'nodes.csv'
file_edges_name = path_w_form + 'edges.csv'
file_nodes_json_name = path_w_form + 'nodes.json'
file_edges_json_name = path_w_form + 'edges.json'

# Создаём узлы
with open(file_nodes_name, 'w') as file_nodes, \
        open(file_nodes_json_name, 'w') as file_nodes_json:
    node_dict = lem.build_node_dict(lines, weights,
                                    include_bastard=bastard,
                                    include_non_cyrillic=non_cyrillic)
    lem.write_node_dict(file_nodes, node_dict)
    pretty_json(node_dict, file_nodes_json)

# Создаём рёбра
with open(file_edges_name, 'w') as file_edges, \
        open(file_edges_json_name, 'w') as file_edges_json:
    edge_dict = lem.build_edge_dict(lines, weights,
                                    include_bastard=bastard,
                                    include_non_cyrillic=non_cyrillic)
    lem.write_edge_dict(file_edges, edge_dict)
    edges = {' - '.join(edge): count for edge, count in edge_dict.items()}
    pretty_json(edges, file_edges_json)

print('Done Part2.3')
