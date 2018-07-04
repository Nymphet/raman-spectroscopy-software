import json
import pandas
import dicttoxml
import numpy as np
import datetime
from scipy import interpolate

import raman_configs


def to_list_all(data):
    # recursively check for arrays in dict and convert them to lists
    if type(data) == np.ndarray:
        return data.tolist()
    if type(data) == list:
        return data
    if type(data) == dict:
        new_dict = dict()
        for key in data:
            new_dict[key] = to_list_all(data[key])
        return new_dict
    return data


def create_to_save_data(format, data_dict):
    new_dict = dict(data_dict)
    new_dict = to_list_all(new_dict)
    if format == 'JSON':
        return json.dumps(new_dict)
    elif format == 'XML':
        return dicttoxml.dicttoxml(new_dict)
    elif format == 'CSV':
        return ''
    elif format == 'XLSX':
        return ''


def save_data(format, filename, data_dict, append_time):
    # make a copy to convert it to dict of lists
    new_dict = dict(data_dict)
    new_dict = to_list_all(new_dict)
    if append_time:
        new_filename = filename + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    else:
        new_filename = filename

    with open(new_filename, 'w') as f:
        f.write(create_to_save_data(format, data_dict))


def remove_zeros_and_sort(list1, list2):
    is_zero_1 = [1 if i else 0 for i in list1]
    is_zero_2 = [1 if i else 0 for i in list2]
    res = [sum(x) for x in zip(is_zero_1, is_zero_2)]
    new_list1 = []
    new_list2 = []
    for i in range(len(res)):
        if res[i]:
            new_list1.append(list1[i])
            new_list2.append(list2[i])
    return sorted(new_list1), sorted(new_list2)


def create_1d_regression(data_dict, model):
    assert len(data_dict) == 2
    pixel_indices, wavenumbers = remove_zeros_and_sort(
        data_dict['pixel_indices'], data_dict['wavenumbers'])
    if model == 'B-Spline':
        t, c, k = interpolate.splrep(
            pixel_indices, wavenumbers, k=raman_configs.DEFAULT_B_SPLINE_PARAMS_K, s=raman_configs.DEFAULT_B_SPLINE_PARAMS_S)
        spline = interpolate.BSpline(t, c, k, extrapolate=True)
        return spline
    if model == 'Polynomial-2':
        fit_params = np.polyfit(
            pixel_indices, wavenumbers, 2)
        poly = np.poly1d(fit_params)
        return poly
    if model == 'Polynomial-3':
        fit_params = np.polyfit(
            pixel_indices, wavenumbers, 3)
        poly = np.poly1d(fit_params)
        return poly
    if model == 'Linear':
        fit_params = np.polyfit(
            pixel_indices, wavenumbers, 1)
        poly = np.poly1d(fit_params)
        return poly
    if model == 'User Defined':
        return raman_configs.USER_DEFINED_MODEL(pixel_indices, wavenumbers)
    # if model is not available, do nothing
    return lambda x: x


def average_over_samples(data_dict_list):
    all_keys = set().union(*(d.keys() for d in data_dict_list))
    data_dict = dict()
    for key in all_keys:
        data_list = [d[key] for d in data_dict_list]
        data_dict[key] = np.mean(data_list, axis=0)
    return data_dict


def subtract_dict_data(data_dict1, data_dict2):
    keys = data_dict1.keys()
    new_data_dict = dict()
    for key in keys:
        new_data_dict[key] = np.subtract(data_dict1[key], data_dict2[key])
    return new_data_dict
