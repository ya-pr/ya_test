#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-
"""
Выгрузка данных из желтенького интерфейса Вордстата.

Берёт данные из файла file_name (по умолчанию "Data/input.txt").
Отправляет GET-запрос с указанными параметрами. Получает csv-файл.
Готовые файлы кладёт в path_out (по умолчанию "Output").
"""

import sys
import os
import time
import csv
import urllib.request
import urllib.parse

# Перенаправление потока стандартного вывода (запись лога в файл)
sys.stdout = open('log.txt', 'a', encoding='utf-8')


# Функция преобразования времени в читабельный формат
def t(unix=None):
    return '%s' % (time.strftime("%d %b %Y %H:%M:%S", time.localtime(unix)))


# Основная функция
def wordstat(file_name, start_from_line, path_out, date_from, date_to, geo_quant, geo, text_geo):
    # Пишем время, имя модуля и функции
    print('%s\t%s' % (t(), 'Start script wordstat.wordstat'))

    # Создаём папку path_out, если не существует
    if not os.path.exists(path_out):
        os.makedirs(path_out)

    file_r = open('%s' % file_name, 'r', encoding='utf-8')
    total_line = 0  # счётчик строк
    base = 'http://advq.yandex.ru/iadvq?'  # или wordstat-old.yandex.ru/iadvq?

    for line in file_r:
        total_line += 1
        if total_line < start_from_line:
            continue

        word = line.strip('\n')

        # параметры GET-запроса
        data = {'cmd': 'batch_form',
                'format': 'excel',
                'date_from': date_from,
                'date_to': date_to,
                'date_quant': date_quant,
                'geo_quant': geo_quant,
                'geo': geo,
                'text_geo': text_geo,
                'file': word}

        url = base + urllib.parse.urlencode(data)

        # wordstat падает, поэтому вводим временную задержку каждые 10 итераций
        if total_line % 10 == 0:
            time.sleep(1200)
        urllib.request.urlretrieve(url, '%s/%s.csv' % (path_out, word))
        print('%s\tDone word #%d\t%s' % (t(), total_line, url))
        time.sleep(180)  # ещё одна временная задержка после каждой итерации
    print('%s\tFinish script wordstat.wordstat\n----------' % t())


# Функция объединения данных по нескольким словам в один файл
def in_one_file(file_name, file_name_out, path_in):
    # Пишем время, имя модуля и функции
    print('%s\t%s' % (t(), 'Start script wordstat.in_one_file'))

    words = open('%s' % file_name, 'r', encoding='utf-8')
    file_w = open('%s' % file_name_out, 'w', encoding='utf-8')

    total_line = 0  # счётчик строк
    for word in words:
        total_line += 1
        word = word.strip('\n')
        file_r = open('%s/%s.csv' % (path_in, word), 'r', encoding='utf-8')
        file_r.readline()
        if total_line > 1:
            file_r.readline()

        for line in file_r:
            line = line.strip('\n')
            file_w.write(line + '\n')
        file_r.close()
    file_w.close()
    print('%s\tFinish script wordstat.in_one_file\n----------' % t())


# Функция объединения данных по нескольким словам в один файл без учёта периода
def in_one_file_sum(file_name, file_name_out, path_in):
    # Пишем время, имя модуля и функции
    print('%s\t%s' % (t(), 'Start script wordstat.in_one_file_sum'))

    words = open('%s' % file_name, 'r', encoding='utf-8')
    file_w = open('%s' % file_name_out, 'w', encoding='utf-8')
    csv_w = csv.writer(file_w, delimiter=';', quoting=csv.QUOTE_NONE)

    total_line = 0  # счётчик строк
    for word in words:
        total_line += 1
        word = word.strip('\n')
        file_r = open('%s/%s.csv' % (path_in, word), 'r', encoding='utf-8')
        file_r.readline()
        csv_r = csv.DictReader(file_r, delimiter=';', quoting=csv.QUOTE_NONE)
        if total_line == 1:
            csv_w.writerow(csv_r.fieldnames[:-2])

        dict_sum = {}
        for line in csv_r:
            reg = (line['reg_id'], line['reg_name'])
            cnt = int(line['cnt'])
            if reg not in dict_sum:
                dict_sum[reg] = cnt
            else:
                dict_sum[reg] += cnt

        for reg in dict_sum:
            csv_w.writerow([word, reg[0], reg[1], dict_sum[reg]])
        file_r.close()
    file_w.close()
    print('%s\tFinish script wordstat.in_one_file_sum\n----------' % t())


if __name__ == '__main__':
    file_name = 'Data/input.txt'  # файл со словами
    start_from_line = 1  # строка, с которой начинать выполнение скрипта
    path_out = 'Output'  # папка назначения

    # Параметры Get-запроса
    date_from = '01.01.2013'  # начальная дата
    date_to = '24.08.2014'  # конечная дата
    date_quant = 'M'  # 'M' - по месяцам, 'W' - по неделям
    geo_quant = '3'  # 3 - страны; 4 - регионы; 5 - области; 6 - города
    geo = '225'  # GeoId. Россия - 225, Украина - 187, Москва - 213
    text_geo = 'Россия'  # текстовое описание GeoId
    wordstat(file_name, start_from_line, path_out,
             date_from, date_to, geo_quant, geo, text_geo)

    # После того как выгрузили все слова, объединяем всё в один файл
    file_name_out = 'Output/Output.csv'
    path_in = path_out
    in_one_file(file_name, file_name_out, path_in)

    # Общее количество запросов по словам без учета времени
    file_name_out = 'Output/Output_sum.csv'
    in_one_file_sum(file_name, file_name_out, path_in)
