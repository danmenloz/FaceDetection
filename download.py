# Download faceScrub dataset
import csv
import random
import subprocess
import shutil
from pathlib import Path
from PIL import Image

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

    for actor_entry in Path('./actors/faces/').iterdir():
        if actor_entry.is_dir():
            for face_entry in actor_entry.iterdir():
                faces.append( {'name':actor_entry.name, 'face':str(face_entry)} )

    for actor_entry in Path('./actors/images/').iterdir():
        if actor_entry.is_dir():
            for image_entry in actor_entry.iterdir():
                # Search for dictionary and add key
                for face in faces:
                    if face['face'].find(image_entry.stem):
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

    # Create test set directory
    test_dir = 'data/test/'
    print('Creating {} directory...'.format(test_dir))
    Path(test_dir).mkdir(parents=True)
    for face in test_set:
        image = Image.open(face['face'])
        print('Resizing {} '.format( str(Path(face['face']).name)) )
        if Path(face['face']).suffix == '.png':
            image = image.convert('RGB')
        new_image = image.resize(resolution)
        save_path = str(Path(test_dir) / Path(face['face']).stem) +  '.jpg'
        new_image.save( save_path, 'JPEG')
        face['resized'] = save_path

    # Create test set directory
    training_dir = 'data/training/'
    print('Creating {} directory'.format(training_dir))
    Path(training_dir).mkdir(parents=True)
    for face in training_set:
        image = Image.open(face['face'])
        print('Resizing {} '.format( str(Path(face['face']).name)) )
        if Path(face['face']).suffix == '.png':
            image = image.convert('RGB')
        new_image = image.resize(resolution)
        save_path = str(Path(training_dir) / Path(face['face']).stem) +  '.jpg'
        new_image.save( save_path, 'JPEG')
        face['resized'] = save_path


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
