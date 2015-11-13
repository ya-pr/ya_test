#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-

from lem import make_gephi_files

# Воспользуемся функцией верхнего уровня из пакета 'lem' для создания файла
# с леммами и файлов для Gephi
file_data_name = 'data/Задачки.tsv'
make_gephi_files(file_data_name, query_column=2, headers=True, edges_cut=5)
