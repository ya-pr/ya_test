#!/usr/bin/env python3.4
# -*- coding: utf-8 -*-

"""Тестирование леммера"""

import os

import lem
from common_functions import pretty_json


def test_lem(mystem, path_w):
    # default
    with open('data/input.txt', 'r') as file_r, \
            open(path_w + 'lems.txt', 'w') as file_w:
        lem.lem(file_r, file_w)

    # different options
    path_w += 'options/'
    if not os.path.exists(path_w):
        os.makedirs(path_w)
    params_list = (
        ['-cl'],
        ['-clde', 'utf-8'],
        ['-cldige', 'utf-8', '--format', 'json'],
        ['-cldige', 'utf-8', '--format', 'xml']
    )
    for params in params_list:
        if 'json' in params:
            ext = 'json'
        elif 'xml' in params:
            ext = 'xml'
        else:
            ext = 'txt'

        with open('data/input.txt', 'r') as file_r, \
                open(path_w + 'lems (%s).%s' % (params, ext), 'w') as file_w:
            lem.lem(file_r, file_w, mystem=mystem, params=params)
    print('Done test_lem')


def test_main():
    lem.main()
    print('Done test_main')


def test_json_parse(file_r_name, path_w):
    parsed = []
    with open(file_r_name, 'r') as file_r, \
            open(path_w + 'json_parse.json', 'w') as file_w:
        for line in file_r:
            line_parse = lem.json_parse(line)
            parsed.append(line_parse)
        pretty_json(parsed, file_w)
    print('Done test_json_parse')


def test_gr_parse():
    # TODO: Заполнить секцию
    pass


def test_lem_filter():
    # TODO: Заполнить секцию
    pass


def test_build_edge_dict(file_r_name, file_weights_name, path_w):
    # default
    with open(file_r_name, 'r') as file_json, \
            open(path_w + 'edges.json', 'w') as file_w:
        edge_dict = lem.build_edge_dict(file_json)
        edges = {' - '.join(edge): count for edge, count in edge_dict.items()}
        pretty_json(edges, file_w)

    # different options
    path_w += 'options/'
    if not os.path.exists(path_w):
        os.makedirs(path_w)
    weights_options = (None, True)
    bastard_options = (True, False)
    non_cyrillic_options = (True, False)

    for weights in weights_options:
        for bastard in bastard_options:
            for non_cyrillic in non_cyrillic_options:
                with open(file_r_name, 'r') as file_json:
                    if weights:
                        file_weights = open(file_weights_name, 'r')
                    else:
                        file_weights = None

                    file_w_name = '{0}edges (' \
                                  'weights={1}, ' \
                                  'bastard={2}, ' \
                                  'non_cyrillic={3}' \
                                  ').json'.format(path_w, weights,
                                                  bastard, non_cyrillic)
                    file_w = open(file_w_name, 'w')
                    edge_dict = lem.build_edge_dict(file_json, file_weights,
                                                    bastard, non_cyrillic)
                    edges = {' - '.join(edge): count for edge, count in
                             edge_dict.items()}
                    pretty_json(edges, file_w)
    print('Done test_build_edge_dict')


def test_write_edge_dict(file_r_name, path_w):
    # build default edge_dict
    with open(file_r_name, 'r') as file_json:
        edge_dict = lem.build_edge_dict(file_json)

    # default
    with open(path_w + 'edges.csv', 'w') as file_w:
        lem.write_edge_dict(file_w, edge_dict)

    # different options
    path_w += 'options/'
    if not os.path.exists(path_w):
        os.makedirs(path_w)
    # with cut
    with open(path_w + 'edges (cut=10).csv', 'w') as file_w:
        lem.write_edge_dict(file_w, edge_dict, cut=10)

    # with '\t'
    with open(path_w + 'edges.tsv', 'w') as file_w:
        lem.write_edge_dict(file_w, edge_dict, sep='\t')

    print('Done test_write_edge_dict')


def test_build_node_dict(file_r_name, file_weights_name, path_w):
    # default
    with open(file_r_name, 'r') as file_json, \
            open(path_w + 'nodes.json', 'w') as file_w:
        node_dict = lem.build_node_dict(file_json)
        pretty_json(node_dict, file_w)

    # different options
    path_w += 'options/'
    if not os.path.exists(path_w):
        os.makedirs(path_w)
    weights_options = (None, True)
    bastard_options = (True, False)
    non_cyrillic_options = (True, False)

    for weights in weights_options:
        for bastard in bastard_options:
            for non_cyrillic in non_cyrillic_options:
                with open(file_r_name, 'r') as file_json:
                    if weights:
                        file_weights = open(file_weights_name, 'r')
                    else:
                        file_weights = None

                    file_w_name = '{0}nodes (' \
                                  'weights={1}, ' \
                                  'bastard={2}, ' \
                                  'non_cyrillic={3}' \
                                  ').json'.format(path_w, weights,
                                                  bastard, non_cyrillic)
                    file_w = open(file_w_name, 'w')
                    node_dict = lem.build_node_dict(file_json, file_weights,
                                                    bastard, non_cyrillic)
                    pretty_json(node_dict, file_w)

    print('Done test_build_node_dict')


def test_write_node_dict(file_r_name, path_w):
    # build default node_dict
    with open(file_r_name, 'r') as file_json:
        node_dict = lem.build_node_dict(file_json)

    # default
    with open(path_w + 'nodes.csv', 'w') as file_w:
        lem.write_node_dict(file_w, node_dict)

    # different options
    path_w += 'options/'
    if not os.path.exists(path_w):
        os.makedirs(path_w)
    # with cut
    with open(path_w + 'nodes (cut=10).csv', 'w') as file_w:
        lem.write_node_dict(file_w, node_dict, cut=10)

    # with '\t'
    with open(path_w + 'nodes.tsv', 'w') as file_w:
        lem.write_node_dict(file_w, node_dict, sep='\t')

    print('Done test_write_node_dict')


def test_part_speech_conflict_resolution():
    # TODO: Заполнить секцию
    pass


def test_make_gephi_files(file_data_name, path_w):
    # default
    lem.make_gephi_files(path_w=path_w)

    # different options
    path_w += 'options/'

    # with cut
    path_w_opt = path_w + 'with_cut/'
    lem.make_gephi_files(file_data_name, path_w=path_w_opt,
                         query_column=2, headers=True,
                         nodes_cut=10, edges_cut=10)

    # with weights
    path_w_opt = path_w + 'with_weights/'
    lem.make_gephi_files(file_data_name, path_w=path_w_opt,
                         query_column=2, weight_column=3, headers=True)

    print('Done test_make_gephi_files')


def main():
    path_w = 'output/lems/'
    if not os.path.exists(path_w):
        os.makedirs(path_w)
    test_lem(mystem='/Applications/mystem', path_w=path_w)
    test_main()

    params = ['-cldige', 'utf-8', '--format', 'json']
    file_r_name = "output/lems/options/lems (%s).json" % params
    file_weights = 'data/weights.txt'

    path_w = 'output/parse/'
    if not os.path.exists(path_w):
        os.makedirs(path_w)
    test_json_parse(file_r_name, path_w)

    path_w = 'output/edges/'
    if not os.path.exists(path_w):
        os.makedirs(path_w)
    test_build_edge_dict(file_r_name, file_weights, path_w)
    test_write_edge_dict(file_r_name, path_w)

    path_w = 'output/nodes/'
    if not os.path.exists(path_w):
        os.makedirs(path_w)
    test_build_node_dict(file_r_name, file_weights, path_w)
    test_write_node_dict(file_r_name, path_w)

    path_w = 'output/make_gephi_files/'
    file_data_name = 'data/input.tsv'
    test_make_gephi_files(file_data_name, path_w)


if __name__ == '__main__':
    main()
