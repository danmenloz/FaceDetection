# Download faceScrub dataset
import csv
import random
import subprocess
import shutil
from pathlib import Path
from PIL import Image
from random import randrange
from tqdm import tqdm

# Flags to enable download and data sets creation
download = False
create_dataset = True

# Training and test dataset sizes
training_size = 1000
test_size = 100

# Image resolution
resolution = (20,20)

if download:
    # faceScrub directory
    actors_file = './faceScrub/facescrub_actors.txt'
    actresses_file = './faceScrub/facescrub_actresses.txt'

    actors_list = []
    actresses_list = []

    # Read actors' file
    with open(actors_file, newline = '') as actors:                                                                                          
        actors_reader = csv.DictReader(actors, delimiter='\t')
        for actor in actors_reader:
            actors_list.append(actor)

    # Read actresses' file
    with open(actresses_file, newline = '') as actresses:                                                                                          
        actresses_reader = csv.DictReader(actresses, delimiter='\t')
        for actresses in actresses_reader:
            actresses_list.append(actor)

    # Combine and shuffle combined list
    actors_list.append(actresses_list)
    random.shuffle(actors_list)

    # Create source file
    with open('download.txt', 'w', newline='') as file:
        fieldnames = actors_list[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for actor in actors_list:
            try: 
                writer.writerow(actor)
            except:
                print(actor)

    # Run fascescrub download tool
    cmd = "python3 ./faceScrub/python3_download_facescrub.py download.txt actors/ \
        --crop_face --logfile=download.log --timeout=5 --max_retries=3"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()




if create_dataset:

    # Read download directory
    print('Reading download folder...')
    faces = []

    for actor_entry in tqdm(Path('./actors/faces/').iterdir(), desc ="Reading faces"):
        if actor_entry.is_dir():
            for face_entry in actor_entry.iterdir():
                faces.append( {'name':actor_entry.name, 'face':str(face_entry)} )

    for actor_entry in tqdm(Path('./actors/images/').iterdir(), desc ="Reading images"):
        if actor_entry.is_dir():
            for image_entry in actor_entry.iterdir():
                # Search for dictionary and add key
                for face in faces:
                    if face['face'].find(image_entry.stem)>=0:
                        face['image'] = str(image_entry)

    # Shuffle list
    random.shuffle(faces)

    print('Creating test and training lists...')
    # Create test set list
    test_set = []
    actors = []
    for i in range(test_size):
        test_set.append(faces[i])
        actors.append(faces[i]['name'])
    actors = list(set(actors)) # delete duplicates

    # Create training set list, make sure that no actor from test set is here
    training_set = []
    for face in faces[test_size:]:
        if face['name'] not in actors:
            training_set.append(face)
        if len(training_set) == training_size:
            break

    def random_crop(image_path, target_size):
        image = Image.open(image_path)
        if Path(image_path).suffix == '.png':
            image = image.convert('RGB')
        img_size = image.size
        x_max = img_size[0] - target_size[0]
        y_max = img_size[1] - target_size[1]
        random_x = randrange(0, x_max//2 + 1) * 2
        random_y = randrange(0, y_max//2 + 1) * 2
        area = (random_x, random_y, random_x + target_size[0], random_y + target_size[1])
        c_img = image.crop(area)
        return c_img

    # Create test set directory
    test_dir = 'data/test/'
    print('Creating {} directory...'.format(test_dir))
    Path(test_dir).mkdir(parents=True)
    (Path(test_dir) / '0').mkdir()
    (Path(test_dir) / '1').mkdir()
    for face in test_set:
        img1 = Image.open(face['face'])
        print('Resizing {} '.format( str(Path(face['face']).name)) )
        if Path(face['face']).suffix == '.png':
            img1 = img1.convert('RGB')
        img1 = img1.resize(resolution)
        save_path = str(Path(test_dir) / '1' / Path(face['face']).stem ) +  '.jpg'
        img1.save( save_path, 'JPEG')
        face['1'] = save_path
        img0 = random_crop(face['image'],resolution)
        save_path = str(Path(test_dir) / '0'/ Path(face['image']).stem ) +  '.jpg'
        img0.save( save_path, 'JPEG')
        face['0'] = save_path



    # Create test set directory
    training_dir = 'data/training/'
    print('Creating {} directory'.format(training_dir))
    Path(training_dir).mkdir(parents=True)
    (Path(training_dir) / '0').mkdir()
    (Path(training_dir) / '1').mkdir()
    for face in training_set:
        img1 = Image.open(face['face'])
        print('Resizing {} '.format( str(Path(face['face']).name)) )
        if Path(face['face']).suffix == '.png':
            img1 = img1.convert('RGB')
        img1 = img1.resize(resolution)
        save_path = str(Path(training_dir) / '1'/ Path(face['face']).stem) +  '.jpg'
        img1.save( save_path, 'JPEG')
        face['1'] = save_path
        img0 = random_crop(face['image'],resolution)
        save_path = str(Path(test_dir) / '0'/ Path(face['image']).stem ) +  '.jpg'
        img0.save( save_path, 'JPEG')
        face['0'] = save_path

    # Create txt info files
    print('Creating txt files...')
    with open( str(Path(test_dir) / 'test.txt'), 'w', newline='') as file:
        fieldnames = test_set[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for face in test_set:
            writer.writerow(face)

    with open( str(Path(training_dir) / 'training.txt'), 'w', newline='') as file:
        fieldnames = training_set[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for face in training_set:
            writer.writerow(face)

    
    

    print('Datasets created sucessfully!\n')
