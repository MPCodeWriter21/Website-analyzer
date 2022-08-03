import re
import os
import zipfile
import platform

import requests

from typing import Tuple, Union, Callable

from bs4 import BeautifulSoup

latest_version_pattern = re.compile(r'Latest stable release: ChromeDriver (\d+\.\d+\.\d+\.\d+)')


def get_chrome_driver_latest_version() -> Union[None, str]:
    """
    Get the latest version of Chrome Driver from the web.

    :return: The latest version of Chrome Driver.
    """
    url = 'https://chromedriver.chromium.org/'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    for a in soup.find_all('a'):
        if 'ChromeDriver' in a.text:
            if version := latest_version_pattern.fullmatch(a.find_parent().find_parent().text):
                return version.group(1)


def download_chrome_driver(path: Union[str, os.PathLike] = None, remove_zip: bool = False,
                           progress_callback: Callable = lambda downloaded, total_size: None) -> Tuple[str, str]:
    """
    Download the latest version of Chrome Driver.

    :param path: The path to save the Chrome Driver.
    :param remove_zip: If True, it will remove the zip file after extracting.
    :param progress_callback: A callback function that will be called when downloading.
    :return: The version and path of the Chrome Driver.
    """
    version = get_chrome_driver_latest_version()
    # Windows
    if platform.system() == 'Windows':
        name = 'chromedriver_win32.zip'
    # Linux
    elif platform.system() == 'Linux':
        name = 'chromedriver_linux64.zip'
    # Mac
    elif platform.system() == 'Darwin':
        name = 'chromedriver_mac64.zip'
    else:
        raise Exception(f'Unsupported platform: {platform.system()}! Please download ChromeDriver manually.')

    url = f'https://chromedriver.storage.googleapis.com/{version}/{name}'

    # Download the file
    res = requests.get(url, stream=True)
    total_size = int(res.headers.get('content-length', 0))

    if res.status_code != 200:
        raise requests.HTTPError(f'Failed to download ChromeDriver: Error {res.status_code}')

    with open(name, 'wb') as f:
        if not total_size:
            f.write(res.content)
        else:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    progress_callback(f.tell(), total_size)

    # Extract the file
    with zipfile.ZipFile(name, 'r') as zip_file:
        filename = zip_file.filelist[0].filename
        zip_file.extractall()

    # Remove the zip file
    if remove_zip:
        os.remove(name)

    # Move the Chrome Driver to the specified path
    if path:
        os.rename(filename, path)

    return version, path or filename


def get_chrome_driver(path: Union[str, os.PathLike] = None, force_download: bool = False, remove_zip: bool = False,
                      progress_callback: Callable = lambda *args: None) -> str:
    """
    Get the latest version of Chrome Driver.

    :param path: The path to save the Chrome Driver.
    :param force_download: If True, it won't check if a driver is already downloaded.
    :param remove_zip: If True, it will remove the zip file after extracting.
    :param progress_callback: A callback function that will be called when downloading.
    :return: The path of the Chrome Driver.
    """
    if not force_download:
        path = 'chromedriver'
        if platform.system() == 'Windows':
            path += '.exe'

        if os.path.exists(path):
            return path

    return download_chrome_driver(path, remove_zip, progress_callback)[-1]
