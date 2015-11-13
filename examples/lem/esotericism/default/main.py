#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

from lem import make_gephi_files

# Воспользуемся функцией верхнего уровня make_gephi_files для создания файла
# с леммами и файлов для Gephi
file_data_name = 'data/input.tsv'
make_gephi_files(file_data_name, query_column=2, weight_column=1)

# В принципе на этом всё. У нас есть все финальные файлы для построения
# графа в Gephi. Если нам необходимо больше гибкости, чем в настройках
# по умолчанию, то дальше уже можно работать с полученными промежуточными
# файлами.
