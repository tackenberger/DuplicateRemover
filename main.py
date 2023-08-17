import datetime
import glob
import logging
import os
import shutil
from multiprocessing import Pool, freeze_support

import exif


def read_exif(img_path):

    with open(img_path, 'rb') as img_file:
        try:
            img = exif.Image(img_file)
            img.has_exif
        except ValueError as err:
            print('{filename} seems to be no image file.'.format(filename=img_file))
            raise err

    if img.has_exif:
        return img
    else:
        return None


def get_creation_date(img):

    try:
        creation_date_str = img.get('datetime_original')
    except:
        raise OSError()
    if creation_date_str is not None:
        return creation_date_str

    creation_date_str = img.get('datetime')
    return creation_date_str


def parse_dt_exif(creation_date_str):
    try:
        creation_dt = datetime.datetime.strptime(creation_date_str, '%Y:%m:%d %H:%M:%S')
    except:
        logging.error('creation_date_str {creation_date_str} is not matching the expected datetime format.'.format(
            creation_date_str=creation_date_str))
        raise
    return creation_dt


def target_dir(base_dir, creation_dt:datetime.datetime):
    return os.path.join(base_dir, creation_dt.strftime('%Y'), creation_dt.strftime('%m'))


def target_name(creation_dt: datetime.datetime, img=None):
    if img is not None:
        model = img.get('model')
        maker = img.get('make')
        device_hint = '_'.join(filter(None, [maker, model])).replace(' ', '')
    else:
        device_hint = ''

    name_str = '_'.join(filter(None, [creation_dt.strftime('%Y%m%d_%H%M%S'), device_hint]))
    return name_str + '.jpg'


def process_image(filename):
    try:
        img = read_exif(filename)
        creation_str = get_creation_date(img)
        creation_dt = parse_dt_exif(creation_str)
        target_dir_name = target_dir(base_name, creation_dt)
        output_file = os.path.join(target_dir_name, target_name(creation_dt, img=img))
    except:
        shutil.copy2(filename, problem_dir)
        return
    if not os.path.exists(output_file):
        try:
            shutil.copy2(filename, output_file)
        except FileNotFoundError as err:
            os.makedirs(target_dir_name)
            shutil.copy2(filename, output_file)
    else:
        pass


def run_multiprocessing(func, i, n_processors):
    with Pool(processes=n_processors) as pool:
        return pool.map(func, i)


if __name__ == '__main__':
    # freeze_support()   # required to use multiprocessing

    initial_path = '.'
    initial_path = '/mnt/c/Users/jtack/Documents/Privat/Bilder/ToBeSorted'


    base_name = '../target_dir'
    base_name = '/mnt/c/Users/jtack/Documents/Privat/Bilder/target_dir'

    problem_dir = '/mnt/c/Users/jtack/Documents/Privat/Bilder/problems'

    n_processors = 16

    # iterate over files in
    # that directory
    # for filename in glob.iglob(f'{initial_path}/**', recursive=True):
    #     # if filename.find('_') == 0:
    #     #     continue
    #     process_image(filename)
    # filename_list = glob.glob(f'{initial_path}/**', recursive=True)
    filename_list = glob.glob(f'{initial_path}/**/*.[jJ][pP][gG]', recursive=True)
    filename_list.extend(glob.glob(f'{initial_path}/**/*.[jJ][pP][eE][gG]', recursive=True))

    out = run_multiprocessing(process_image, filename_list, n_processors)



