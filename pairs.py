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
    Принимает 2 ключа:
    --unique: удалять повторяющиеся объекты
    --test: запустить тестирование функции
    """
    if '--test' in sys.argv:
        test()
        return

    unique = False
    if '--unique' in sys.argv:
        unique = True

    for line in sys.stdin:
        elements = line.strip().split(' ')
        print(pairs(elements, unique))


def test():
    """
    Набор тестов функции
    """
    string1 = '1 1 2 3 4'
    string2 = '4 3 2 1 1'
    true_pairs = [('1', '1'), ('1', '2'), ('1', '3'), ('1', '4'), ('1', '2'),
                  ('1', '3'), ('1', '4'), ('2', '3'), ('2', '4'), ('3', '4')]
    true_pairs_unique = [('1', '2'), ('1', '3'), ('1', '4'),
                         ('2', '3'), ('2', '4'), ('3', '4')]

    pairs1 = pairs(string1.split(' '))
    pairs2 = pairs(string2.split(' '))
    pairs1_unique = pairs(string1.split(' '), unique=True)
    pairs2_unique = pairs(string2.split(' '), unique=True)

    # Test1
    if pairs1 == pairs2:
        print("Test1 OK")
    else:
        print("Test1 FAIL")

    # Test2
    if pairs1_unique == pairs2_unique:
        print("Test2 OK")
    else:
        print("Test2 FAIL")

    # Test3
    if pairs1 == true_pairs:
        print("Test3 OK")
    else:
        print("Test3 FAIL")

    # Test4
    if pairs1_unique == true_pairs_unique:
        print("Test4 OK")
    else:
        print("Test4 FAIL")


if __name__ == '__main__':
    main()
