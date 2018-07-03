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


def save_data(format, filename, data_dict, append_time):
    # make a copy to convert it to dict of lists
    new_dict = dict(data_dict)
    new_dict = to_list_all(new_dict)
    if append_time:
        new_filename = filename + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    else:
        new_filename = filename
    if format == 'JSON':
        with open(new_filename, 'w') as f:
            f.write(json.dumps(new_dict))
    elif format == 'XML':
        with open(new_filename, 'w') as f:
            f.write(dicttoxml.dicttoxml(new_dict))
    elif format == 'CSV':
        pass
    elif format == 'XLSX':
        pass
    else:
        pass


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
    if model == 'Polynomial':
        fit_params = np.polyfit(
            pixel_indices, wavenumbers, raman_configs.DEFAULT_POLINOMIAL_ORDER)
        poly = np.poly1d(fit_params)
        return poly
    # if model is not available, do nothing
    return lambda x: x
