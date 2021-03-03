# FaceDetection
Face image classification using Gaussian model, Mixture of Gaussian model, t-distribution, Mixture of t-distribution, Factor Analysis and Mixture of Factor Analyzer

## Setup Information
To run this project follow the next steps:

1. [Optional] If you wish to download the original images from the faceSrub dataset, change the *dowload* flag in the **download.py** script. This will use the information in the **/faceScrub** directory to download the images directly from internet and store then into a directiory named **/actors**.
2. [Optional] If you desire to create new training and testing datasets, change the *create_dataset* flag in **download.py**. The script will then look for the original imges inside the **/actors** directory and create the face and non-face images patches. The resulting datasets are stored in the directory **/data**.
3. Open the **Models.ipynb** notebook and run code to visualize the resulting images. 

This project was built using python 3.7.5.