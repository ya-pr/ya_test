#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""
Библиотека общих функций, упрощающих рутину
"""

import json


def save_column(file_r, file_w, sep='\t', col=1, headers=False):
    """
    Предварительная обработка: сохраняем в файл только один выбранный столбец.
    Функция принимает 2 файла (для чтения и для записи),
    разделитель столбцов и номер сохраняемого столбца.
    Если в файле есть заголовки, то первую строку можно пропустить.

    :param file_r: файл с данными
    :param file_w: файл, в который будем записывать нужный столбец
    :param sep: разделитель столбцов (по умолчанию '\t')
    :param col: номер столбца (по умолчанию 1)
    :param headers: есть ли в файле заголовки (по умолчанию False)
    """
    if headers is True:
        next(file_r)
    for line in file_r:
        # разбиваем строку на столбцы, берём нужный
        # и удаляем символ перевода строки в конце
        line = line.split(sep)[col - 1].rstrip('\n')
        file_w.write(line + '\n')  # записываем в файл


def merge_files(file_r1, file_r2, file_w, sep='\t'):
    """
    Пост-обработка: объединяем леммы с исходным файлом. Функция принимает
    2 файла для чтения, 1 файл для записи и разделитель столбцов.

    :param file_r1: исходный файл
    :param file_r2: файл с леммами
    :param file_w: файл для записи
    :param sep: разделитель столбцов (по умолчанию '\t')
    """
    for line1, line2 in zip(file_r1, file_r2):
        file_w.write(line1.strip() + sep + line2.strip() + '\n')


def pretty_json(obj, file_w):
    """
    Pretty-вывод для сохранения в json.
    :param obj: объект для сохранения
    :param file_w: файл для записи
    """
    json.dump(obj, file_w, sort_keys=True, indent=2, ensure_ascii=False)
