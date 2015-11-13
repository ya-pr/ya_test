#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

"""
Создать все возможные уникальные пары объектов. Возможен запуск из командной
строки
"""

import sys


def pairs(elements, unique=False):
    """
    Возвращает список всех возможных пар объектов без повторов.
    Объекты в парах отсортированы по возрастанию.
    При желании можно оставить только уникальные объекты.

    :type elements: iterable object
    :param elements: набор объектов
    :param unique: флаг удаления повторяющихся объектов
    :return: список отсортированных пар объектов
    """
    if unique:
        elements = set(elements)

    # Сортируем входной набор, чтобы пары всегда получались единообразно
    # вне зависимости от входных данных. Наборы (1,2,3) и (3,2,1) будут
    # на выходе давать одинаковые пары: (1,2), (1,3), (2,3)
    elements = sorted(elements)

    pairs_list = []
    # удаляем по одному элементу пока в наборе не останется всего один
    while len(elements) > 1:
        first = elements.pop(0)
        for el in elements:
            pair = (first, el)
            pairs_list.append(pair)

    return pairs_list


def main():
    """
    Запуск из командной строки. Берет данные из стандартного ввода (объекты,
    разделенные пробелом) и выводит всевозможные уникальные пары).
    Принимает ключ --unique: удалять повторяющиеся объекты
    """

    if '--unique' in sys.argv:
        unique = True
    else:
        unique = False

    for line in sys.stdin:
        elements = line.strip().split(' ')
        print(pairs(elements, unique))


if __name__ == '__main__':
    main()
