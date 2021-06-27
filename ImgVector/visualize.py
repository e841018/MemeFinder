# %%
from argparse import ArgumentParser
from matplotlib import pyplot as plt
plt.ion()
import numpy as np
import torch
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
from torchvision import transforms, datasets
import pickle
from sklearn.manifold import TSNE
from scipy.spatial import KDTree

# %%
# parse args
parser = ArgumentParser()
parser.add_argument('-r', default='efficientnet-b0', dest='model_name')
parser.add_argument('-a', default=False, action='store_true', dest='advprop')
parser.add_argument('-i', default='images/test/', dest='image_folder')
parser.add_argument('-f', default='features/test.pkl', dest='feature_file')
args = parser.parse_args()
if args.image_folder != 'images/test/' and args.feature_file == 'features/test.pkl':
    if args.image_folder[-1] == '/':
        name = args.image_folder.split('/')[-2]
    else:
        name = args.image_folder.split('/')[-1]
    args.feature_file = f'features/{name}.pkl'
print('args:', args)

# %%
# define dataset
from efficientnet_pytorch import EfficientNet
model_name = 'efficientnet-b0'
image_size = EfficientNet.get_image_size(model_name)

transform = transforms.Compose([
    transforms.Resize(image_size),
    transforms.CenterCrop(image_size),
    transforms.ToTensor(),
    # normalize, # for visualization purpose
])
dataset = datasets.ImageFolder(args.image_folder, transform=transform)

def imshow(ax, index):
    image = dataset[index][0].permute(1, 2, 0)
    ax.clear()
    ax.imshow(image)
    ax.get_yaxis().set_visible(False)
    ax.get_xaxis().set_visible(False)

# load features
with open(args.feature_file, 'rb') as f:
    features = pickle.load(f)
print(f'Successfully loaded features from {args.feature_file}')
print(f'    {type(features)}, shape = {features.shape}, dtype = {features.dtype}')

# %%
# visualize in 2D

RUN_TSNE = False
if RUN_TSNE:
    print('running TSNE ...')
    tsne = TSNE(n_components=2)
    features_embedded = tsne.fit_transform(features)
    with open('tsne_memes_tw.pkl', 'wb') as f:
        pickle.dump(features_embedded, f)
else:
    with open('ImgVector/tsne_test.pkl', 'rb') as f:
        features_embedded = pickle.load(f)

from time import time
t = time()
print('building KDTree ...')
tree = KDTree(features_embedded)
print(f'building KDTree took {time()-t:.2f} seconds')

fig = plt.figure()
plt.scatter(*features_embedded.T, s=2)
fig_im, ax_im = plt.subplots(1, 1)

def onclick(event):
    coord = (event.xdata, event.ydata)
    print('coord =', coord)
    dist, idx = tree.query(coord, k=1)
    # plt.figure()
    imshow(ax_im, idx)
cid = fig.canvas.mpl_connect('button_press_event', onclick)

# %%
from code import InteractiveConsole
console = InteractiveConsole(locals=locals())
console.interact()