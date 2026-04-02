''' Created on Mon Jun 5 11:40:19 2023

    General purpose utilities.

    @author: ivan

Copyright (c) 2023 Fraunhofer IKTS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import codecs

def print_progress_bar(iteration, total, prefix='', suffix='',
                       decimals=1, length=100, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar.

    Args:
        iteration (int):   current iteration - required
        total     (int):   total iterations - required
        prefix    (str):   prefix string - optional
        suffix    (str):   suffix string - optional
        decimals  (int):   positive number of decimals in percent complete - optional
        length    (int):   character length of bar - optional
        fill      (str):   bar fill character - optional
        print_end (str):   end character (e.g. "\r", "\r\n") - optional

    Returns:
        Nothing.

    Raises:
        Nothing.
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar_var = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar_var}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()

def check_utf8(filename):
    """
    Check if file conforms to the UTF-8 format

    Args:
        filename (str): file name to be checked - required.

    Returns:
        True if the file is UTF-8 encoded, otherwise False.

    Raises:
        UnicodeDecodeError
    """

    try:
        with codecs.open(filename, encoding='utf-8', errors='strict') as file_name:
            for _ in file_name:
                pass
            return True
    except UnicodeDecodeError:
        print(f'Skipping: {filename} is invalid UTF-8')
        return False


def load_data(files):

    """
    Loads textual data from multiple files with utf-8 check into list of strings (lines)

    Args:
        files list(str):  list of file names to be loaded - required.

    Returns:
        List of strings, where elements are the lines from the files.

    Raises:
        FileNotFoundError
    """

    docs = []
    for f_i in files:
        try:
            f_n = os.path.join(os.getcwd(), f_i)
            if not check_utf8(f_n):
                continue
            with open(f_n, 'r', encoding='utf8') as txtfile:
                for line in txtfile:
                    chars = line.strip()
                    if len(chars)!=0:
                        docs.append(chars)
        except FileNotFoundError:
            print('Error opening file:', f_i)
    return docs
