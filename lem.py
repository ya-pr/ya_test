#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""
Библиотека функций для работы с леммером Mystem: https://tech.yandex.ru/mystem/
"""

import json
import os
import subprocess
from collections import Counter
from itertools import combinations
from itertools import repeat

from common_functions import merge_files
from common_functions import pretty_json


def lem(file_r, file_w, mystem='/Applications/mystem', params=None):
    """
    Функция вызывает программу Mystem с заданными параметрами.
    Необходимо указать путь до программы, файл для чтения, файл для записи
    и параметры запуска.

    :param file_r: файл для чтения
    :param file_w: файл для записи
    :param mystem: путь до программы Mystem
    :param params: параметры запуска списком (по умолчанию ['-clde', 'utf-8'])
    Подробнее: https://tech.yandex.ru/mystem/doc/index-docpage/#options.
    """
    if not params:
        params = ['-clde', 'utf-8']
    subprocess.call([mystem] + params, stdin=file_r, stdout=file_w)


def json_parse(line):
    """
    Функция читает строку с json-выводом Mystem и приводит её
    в более удобный вид. Возвращает список распознанных лемм вида:
    {
    'text': str - исходный текст
    'analysis': True - наличие секции анализа. Если секция отсутствует,
    то отсутствует и ключ 'analysis'. Анализ обычно отсутствует для цифр,
    пробельных символов и знаков пунктуации.
    'analysis_len': int - длина секции анализа (может быть нулевой: например,
    если леммер встречает не кириллические символы)
    'lex': str - распознанная лемма
    'qual': str - качество распознавания: если "bastard", то нет уверенности
    'gr': str - грамматика
    'gr_parse': dict() - разобранная строка gr
    }

    :param line: json-строка
    :return: line_parse
    """
    line_parse = []  # распарсенный список слов
    words = json.loads(line)  # json-строка, разбитая на части

    for i in range(len(words)):
        word = words[i]
        text = word['text']
        line_parse.append({'text': text})
        if 'analysis' not in word:
            continue

        analysis = word['analysis']
        line_parse[i]['analysis'] = True
        analysis_len = len(analysis)
        line_parse[i]['analysis_len'] = analysis_len

        if analysis_len == 0:  # если отсутствует анализ слова
            continue

        analyse = analysis[0]
        lex = analyse['lex']
        line_parse[i]['lex'] = lex

        if 'qual' in analyse:
            line_parse[i]['qual'] = analyse['qual']

        gr = analyse['gr']
        line_parse[i]['gr'] = gr
        line_parse[i]['gr_parse'] = gr_parse(gr)

    return line_parse


def gr_parse(gr):
    """
    Парсит строчку с грамматикой. Подробно о грамматике можно почитать здесь:
    https://tech.yandex.ru/mystem/doc/grammemes-values-docpage/
    Пока возвращает только первую половину до знака "равно" и часть речи.

    :param gr: строка с грамматикой
    """
    parsed = {}
    (first_part, second_part) = gr.split('=', 1)
    parsed['first_part'] = first_part
    parsed['part_speech'] = first_part.split(',')[0]

    return parsed


def lem_filter(line_parse, include_bastard=True, include_non_cyrillic=True):
    # TODO: сделать так, чтобы можно было безболезненно расширять параметры
    """
    Функция отбирает леммы из распарсенной строки.
    При необходимости преобразует леммы.
    Возвращает объекты вида:
    {
    'lex': str - лемма
    'part_speech': str - часть речи
    'bastard': True/False
    'non_cyrillic': True/False
    }

    :param line_parse: output функции json_parse
    :param include_bastard: нужно ли включать в выборку леммы, в распознании
    которых Mystem не уверен?
    :param include_non_cyrillic: нужно ли включать слова, для которых Mystem
    вернул секцию "анализ" нулевой длины? Обычно такое происходит для слов с
    не кириллическими символами
    :return: line_filter
    """
    line_filter = []
    for word in line_parse:
        if 'analysis' not in word:
            continue
        if word['analysis_len'] == 0:
            if not include_non_cyrillic:
                continue

            non_cyrillic = True
            lex = word['text']
            part_speech = None
            bastard = False
        else:
            if 'qual' in word:
                if not include_bastard:
                    continue
                bastard = True
            else:
                bastard = False

            non_cyrillic = False
            lex = word['lex']
            part_speech = word['gr_parse']['part_speech']

        line_filter.append({
            'lex': lex,
            'part_speech': part_speech,
            'bastard': bastard,
            'non_cyrillic': non_cyrillic,
        })

    return line_filter


def line_with_part_speeches():
    # TODO: Функция должна возвращать строку с последовательностью частей речи
    pass


def build_edge_dict(file_json, weights=None,
                    include_bastard=True, include_non_cyrillic=True):
    """
    Функция создаёт счётчик (словарь) рёбер.

    :param file_json: файл в json-выводом Mystem (тестировалось с параметрами
    ['-cldige', 'utf-8', '--format', 'json'])
    :param weights: файл с весами запросов. Если отсутствует, то каждому
    запросу присваивается единичный вес
    :param include_bastard: смотри lem_filter
    :param include_non_cyrillic: смотри lem_filter
    :return: Counter вида: {ребро: количество}
    """
    edge_dict = Counter()  # счётчик рёбер

    if not weights:
        weights = repeat(1)

    for (line, weight) in zip(file_json, weights):
        # парсим строку вывода Mystem
        line_parse = json_parse(line)
        # отбираем слова, удовлетворяющие нашим критериям
        words = lem_filter(line_parse, include_bastard, include_non_cyrillic)
        # оставляем только уникальные леммы (чтобы повторно не считать
        # повторяющиеся в строке леммы)
        lems = {word['lex'] for word in words}

        # составляем список всех возможных пар лемм без повторов
        pairs_list = combinations(sorted(lems), 2)

        # добавляем каждую пару в словарь
        for pair in pairs_list:
            edge_dict[pair] += int(weight)

    return edge_dict


def build_node_dict(file_json, weights=None,
                    include_bastard=True, include_non_cyrillic=True):
    # TODO: сделать так, чтобы можно было безболезненно расширять параметры
    """
    Функция создаёт словарь узлов.

    :param file_json: файл в json-выводом Mystem (тестировалось с параметрами
    ['-cldige', 'utf-8', '--format', 'json'])
    :param weights: файл с весами запросов. Если отсутствует, то каждому
    запросу присваивается единичный вес
    :param include_bastard: смотри lem_filter
    :param include_non_cyrillic: смотри lem_filter
    :return: словарь вида:
    {узел:
        'count': int
        'part_speech':
            {часть речи1: количество1}
            {часть речи2: количество2}
            {часть речиN: количествоN}
    }
    """
    node_dict = {}  # счётчик узлов

    if not weights:
        weights = repeat(1)

    for (line, weight) in zip(file_json, weights):
        # парсим строку вывода Mystem
        line_parse = json_parse(line)
        # отбираем слова, удовлетворяющие нашим критериям
        words = lem_filter(line_parse, include_bastard, include_non_cyrillic)

        # TODO: Продумать, что делать, если в одной строке встречаются
        # одинаковые леммы, относящиеся к разным частям речи

        # добавляем каждую уникальную лемму в словарь
        lexs_unique = []  # список уже добавленных лемм
        for word in words:
            lex = word['lex']
            if lex in lexs_unique:
                continue
            part_speech = word['part_speech']
            if lex not in node_dict:
                node_dict[lex] = word
                node_dict[lex]['count'] = 0
                node_dict[lex]['part_speech'] = Counter()

            node_dict[lex]['count'] += int(weight)
            node_dict[lex]['part_speech'][part_speech] += int(weight)
            lexs_unique.append(lex)

    return node_dict


def write_edge_dict(file_w, edge_dict, sep=';', cut=0, edge_type='Undirected'):
    """
    Функция сортирует счётчик рёбер по убыванию веса и записывает в файл.
    Файл пригоден для импорта в Gephi: http://gephi.github.io/

    :param file_w: файл для записи
    :param edge_dict: счётчик рёбер, возвращаемый функцией build_edge_dict
    :param sep: разделитель столбцов (по умолчанию ';')
    :param cut: не записывать рёбра с весом меньше, чем cut (по умолчанию 0)
    :param edge_type: тип рёбер (по умолчанию 'Undirected')
    """
    # строка заголовков
    print('Weight', 'Source', 'Target', 'Type', sep=sep, file=file_w)

    # сортируем счётчик по убыванию веса рёбер
    edges_list = sorted(edge_dict.items(), key=lambda x: (x[1] * (-1), x[0]))
    # записываем в файл
    for edge, count in edges_list:
        if count < cut:
            continue
        print(count, edge[0], edge[1], edge_type, sep=sep, file=file_w)


def write_node_dict(file_w, node_dict, sep=';', cut=0):
    # TODO: сделать так, чтобы можно было безболезненно расширять параметры
    """
    Функция сортирует счётчик узлов по убыванию веса и записывает в файл.
    Файл пригоден для импорта в Gephi: http://gephi.github.io/

    :param file_w: файл для записи
    :param node_dict: счётчик узлов, возвращаемый функцией build_node_dict
    :param sep: разделитель столбцов (по умолчанию ';')
    :param cut: не записывать узлы с весом меньше, чем cut (по умолчанию 0)
    """
    # строка заголовков
    print('Count', 'Id', 'Label', 'Type', 'Bastard', 'Non-cyrillic',
          sep=sep, file=file_w)

    # разрешаем конфликты множества частей речи
    node_dict = part_speech_conflict_resolution(node_dict)

    # сортируем счётчик по убыванию веса узлов
    count_list = sorted(node_dict.items(),
                        key=lambda item: (item[1]['count'] * -1, item[0]))
    # записываем в файл
    for node, info in count_list:
        count = info['count']
        if count < cut:
            continue
        print(count, node, node, info['parts'], info['bastard'],
              info['non_cyrillic'], sep=sep, file=file_w)


def part_speech_conflict_resolution(node_dict):
    """
    Если слово относится к нескольким частям речи (в зависимости от контекста),
    то объединяем их в одну запись в порядке убывания веса.

    :param node_dict: счётчик узлов, возвращаемый функцией build_node_dict
    :return: список узлов вида: (узел, количество, часть речи)
    """
    for lex in node_dict:
        parts = node_dict[lex]['part_speech']
        parts_names = []
        for part_speech, count in parts.most_common():
            if not part_speech:  # Если часть речи отсутствует, то "None"
                part_speech = 'None'
            parts_names.append(part_speech)
        node_dict[lex]['parts'] = ','.join(parts_names)

    return node_dict


def make_gephi_files(file_data_name='data/input.txt',
                     path_r='data/', path_w='output/',
                     query_column=1, weight_column=None, sep='\t',
                     headers=False, mystem='/Applications/mystem',
                     bastard=True, non_cyrillic=True,
                     nodes_cut=0, edges_cut=0):
    """
    Функция верхнего уровня для создания файлов узлов и рёбер для Gephi.
    Позволяет сделать всё "в один клик" с настройками по умолчанию.
    Все параметры необязательные.

    :param file_data_name: файл с данными (по умолчанию data/input.txt)
    :param path_r: путь к папке с данными (сюда будут сохраняться промежуточные
    файлы с запросами и весами)
    :param path_w: путь к папке, куда будут записываться все финальные файлы
    :param query_column: номер столбца с запросами  (по умолчанию 1)
    :param weight_column: номер столбца с весами  (по умолчанию отсуствует,
    т.е. каждому запросу будет присвоен единичный вес)
    :param sep: разделитель столбцов (по умолчанию '\t')
    :param headers: есть ли в файле заголовки (по умолчанию False)
    :param mystem: см. функцию lem
    :param bastard: см. функцию lem_filter
    :param non_cyrillic: см. функцию lem_filter
    :param nodes_cut: см. функцию write_node_dict
    :param edges_cut: см. функцию write_edge_dict
    """
    if not os.path.exists(path_r):
        os.makedirs(path_r)
    if not os.path.exists(path_w):
        os.makedirs(path_w)

    # Параметры по умолчанию
    params = ['-cldige', 'utf-8', '--format', 'json']
    path_r = path_r.rstrip('/') + '/'
    file_query_name = path_r + 'queries.txt'
    file_weight_name = path_r + 'weights.txt'
    path_w = path_w.rstrip('/') + '/'
    file_lems_name = path_w + 'lems.txt'
    file_json_name = path_w + 'lems.json'
    file_nodes_name = path_w + 'nodes.csv'
    file_edges_name = path_w + 'edges.csv'
    file_nodes_json_name = path_w + 'nodes.json'
    file_edges_json_name = path_w + 'edges.json'

    # Сохраняем столбцы с запросами и весами в отдельные файлы
    with open(file_data_name, 'r') as file_data, \
            open(file_query_name, 'w') as file_query, \
            open(file_weight_name, 'w') as file_weight:
        if headers:
            next(file_data)
        for line in file_data:
            line = line.rstrip('\n').split(sep)
            print(line[query_column - 1], file=file_query)
            if weight_column:
                print(line[weight_column - 1], file=file_weight)
            else:
                print(1, file=file_weight)

    # Прогоняем через леммер
    with open(file_query_name, 'r') as file_query, \
            open(file_json_name, 'w') as file_json:
        lem(file_query, file_json, mystem=mystem, params=params)

    # Список лемм для каждой исходной строки (для проверки)
    with open(file_json_name, 'r') as file_json, \
            open(file_lems_name, 'w') as file_lems:
        for line in file_json:
            line_parse = json_parse(line)
            words = lem_filter(line_parse, include_bastard=bastard,
                               include_non_cyrillic=non_cyrillic)
            lems = [word['lex'] for word in words]
            print(' '.join(lems), file=file_lems)

    # Создаём словари узлов и рёбер
    # Узлы
    with open(file_json_name, 'r') as file_json, \
            open(file_weight_name, 'r') as file_weight:
        node_dict = build_node_dict(file_json, weights=file_weight,
                                    include_bastard=bastard,
                                    include_non_cyrillic=non_cyrillic)
    # Рёбра
    with open(file_json_name, 'r') as file_json, \
            open(file_weight_name, 'r') as file_weight:
        edge_dict = build_edge_dict(file_json, weights=file_weight,
                                    include_bastard=bastard,
                                    include_non_cyrillic=non_cyrillic)

    # Сохраняем словари в json-файлы
    # Узлы
    with open(file_nodes_json_name, 'w') as file_nodes_json:
        pretty_json(node_dict, file_nodes_json)

    # Рёбра
    with open(file_edges_json_name, 'w') as file_edges_json:
        edges = {' - '.join(edge): count for edge, count in edge_dict.items()}
        pretty_json(edges, file_edges_json)

    # Записываем словари для Gephi
    # Узлы
    with open(file_nodes_name, 'w') as file_nodes:
        write_node_dict(file_nodes, node_dict, sep=';', cut=nodes_cut)

    # Рёбра
    with open(file_edges_name, 'w') as file_edges:
        write_edge_dict(file_edges, edge_dict, sep=';', cut=edges_cut)


def main():
    """
    Поведение по умолчанию. Открывает файл data/input.txt в кодировке utf-8 и
    отдает его программе Mystem с параметрами ['-clde', 'utf-8'].
    Сохраняет результат в файл output/lem.txt. После этого объединяет его с
    исходным файлом и записывает в файл output/output.tsv. Разделитель: таб.
    """
    if not os.path.exists('output'):
        os.makedirs('output')
    mystem_path = '/Applications/mystem'  # путь до программы Mystem
    params = ['-clde', 'utf-8']
    with open('data/input.txt', 'r') as file_r, \
            open('output/lems.txt', 'w') as file_w:
        lem(file_r, file_w, mystem=mystem_path, params=params)
    print('Done lem')

    with open('data/input.txt', 'r') as file_r1, \
            open('output/lems.txt', 'r') as file_r2, \
            open('output/output.tsv', 'w') as file_w:
        merge_files(file_r1, file_r2, file_w, sep='\t')
    print('Done merge_files')


if __name__ == '__main__':
    main()
