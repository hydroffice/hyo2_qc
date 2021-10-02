import logging
import os

logger = logging.getLogger(__name__)


def root_data_folder():
    """Return the root test data folder"""
    data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'data'))
    if not os.path.exists(data_folder):
        raise RuntimeError("the root test data folder does not exist: %s" % data_folder)
    return data_folder


def input_data_folder():
    """Return the input test data folder"""
    input_folder = os.path.abspath(os.path.join(root_data_folder(), 'input'))
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
    return input_folder


def input_test_files(ext):
    """Return a list of files with the given extension present in the input test data folder"""
    file_list = list()
    for root, _, files in os.walk(input_data_folder()):
        for f in files:
            if f.endswith(ext):
                file_list.append(os.path.join(root, f))
    return file_list


def output_data_folder():
    """Return the output test data folder"""
    output_folder = os.path.abspath(os.path.join(root_data_folder(), 'output'))
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return output_folder


def output_test_files(ext):
    """Return a list of files with the given extension present in the output test data folder"""
    file_list = list()
    for root, _, files in os.walk(output_data_folder()):
        for f in files:
            if f.endswith(ext):
                file_list.append(os.path.join(root, f))
    return file_list


def input_submission_folders():
    """Return a list of submission folders"""
    dir_list = list()
    for root, dirs, files in os.walk(input_data_folder()):
        for d in dirs:
            if d[:3] == "OPR":
                dir_list.append(os.path.join(root, d))
    return dir_list


def download_data_folder():
    """Return the download test data folder"""
    download_folder = os.path.abspath(os.path.join(root_data_folder(), 'download'))
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    return download_folder


def download_test_files(ext):
    """Return a list of files with the given extension present in the download test data folder"""
    file_list = list()
    for root, dirs, files in os.walk(download_data_folder()):
        for f in files:
            if f.endswith(ext):
                file_list.append(os.path.join(root, f))
    return file_list
