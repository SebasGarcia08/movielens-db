import urllib.request
import os
import os.path as osp
import zipfile

# URL to download the MovieLens 100K dataset
url = 'http://files.grouplens.org/datasets/movielens/ml-100k.zip'



# Specify the directory to save the downloaded file
save_path = './data/ml-100k.zip'

# Download the dataset
urllib.request.urlretrieve(url, save_path)

os.makedirs("./data", exist_ok=True)

# Extract the downloaded ZIP file
with zipfile.ZipFile(save_path, 'r') as zip_ref:
    zip_ref.extractall('./data')
    
print('MovieLens 100K dataset downloaded and extracted successfully!')
