# Download faceScrub dataset
import csv
import random
import subprocess
import copy
import time
import re


# faceScrub directory
actors_file = './faceScrub/facescrub_actors.txt'
actresses_file = './faceScrub/facescrub_actresses.txt'

# Training and test dataset sizes
training_size = 1000
test_size = 10

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


# img_left = copy.deepcopy(training_size)
img_dwld = 0

# Download test images
test_images = []
actors_test = []
fail = []

idx = 0 # index to download images
while img_dwld<test_size:
    print('idx:{}  img_dwld:{} range:({},{})\n'.format(idx,img_dwld,idx, idx+test_size-img_dwld ))
    time.sleep(5)
    dwld_test_images = [] 
    for i in range(idx, idx+test_size-img_dwld ):
        dwld_test_images.append(actors_list[i])
        # actors_test.append(actors_list[i]['name'])
    # actors_test = list(set(actors_test)) # remove duplicates

    # Create txt source file
    with open('test.txt', 'w', newline='') as file:
        fieldnames = dwld_test_images[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for image in dwld_test_images:
            writer.writerow(image)

    # Run fascescrub download tool
    cmd = "python3 ./faceScrub/python3_download_facescrub.py test.txt test/ \
        --crop_face --logfile=test.log --timeout=5 --max_retries=3"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).wait()

    # Update fail log file
    with open("test.log", "r") as log:
        for l in log:
            # search for sucessful download indicator
            srch = re.search("line \d+: http",l)

            # get url
            url = re.search("(?P<url>https?://[^\s]+)", l)

            if url != None and srch == None:
                fail.append(url.group("url"))
    
    # Clean fail list
    clean = []
    for item in fail:
        if item[-1] == ':':
            clean.append(item[:-1])
        else:
            clean.append(item)
    clean = list(set(clean)) # remove duplicates

    # Append fail list to file
    with open('fail.txt', 'a+') as file:
        urls  = [url.strip() for url in file]
        for item in clean:
            if item not in urls:
                file.write("%s\n" % item)
                urls.append(item)
        fail = copy.deepcopy(urls) # update fail list

    # Update list
    for i in range(idx, idx+test_size-img_dwld ):
        if actors_list[i]['url'] not in fail:
            test_images.append(actors_list[i])
    
    # Update idx to start new download
    print('\nDownloads failed: ' + str(len(fail)))
    idx = idx + test_size-img_dwld
    img_dwld = img_dwld + idx-len(fail)

# Final test.txt file
with open('test.txt', 'w', newline='') as file:
    fieldnames = test_images[0].keys()
    writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    for image in test_images:
        writer.writerow(image)

# # Create training list, make sure that no actor from test set is here
# training_images = []
# for actor in actors_list[test_size:]:
#     if actor['name'] not in actors_test:
#         training_images.append(actor)
#     if len(training_images) == training_size:
#         break

# # Create txt source file
# with open('training.txt', 'w', newline='') as file:
#     fieldnames = training_images[0].keys()
#     writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter='\t')
#     writer.writeheader()
#     for image in training_images:
#         writer.writerow(image)






