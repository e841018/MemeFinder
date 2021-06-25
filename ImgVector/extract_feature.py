# %%
from argparse import ArgumentParser
import numpy as np
import torch
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
from torchvision import transforms, datasets
from tqdm import tqdm
import pickle

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
# load model
from efficientnet_pytorch import EfficientNet
model = EfficientNet.from_pretrained(args.model_name, advprop=args.advprop)
image_size = EfficientNet.get_image_size(args.model_name)
model = model.to(device).eval()

# %%
# define dataset
if args.advprop:
    normalize = transforms.Lambda(lambda img: img * 2.0 - 1.0)
else:
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225])
transform = transforms.Compose([
    transforms.Resize(image_size),
    transforms.CenterCrop(image_size),
    transforms.ToTensor(),
    normalize,
])
dataset = datasets.ImageFolder(args.image_folder, transform=transform)

# %%
# extract features
batch_size = 64
loader = torch.utils.data.DataLoader(
    dataset=dataset,
    batch_size=batch_size,
    shuffle=False)
L = len(dataset)
features = np.zeros((L, 1000), dtype=np.float32) # outputs.shape == (B, 1000) 
for b, batch in enumerate(tqdm(loader)):
    inputs, classes = batch
    inputs = inputs.to(device)
    with torch.no_grad():
        outputs = model(inputs).cpu().detach().numpy()
    start = b * batch_size
    end = start + batch_size
    features[start:end, :] = outputs

# %%
# sort with int(filename)
features_sorted = np.zeros((L, 1000), dtype=np.float32)

id_list = []
for name in dataset.imgs:
    id_list.append(int(name[0].split('\\')[-1].split('.')[0]))
indices = np.argsort(id_list)
for i, idx in enumerate(indices):
    features_sorted[i] = features[idx]
features = features_sorted

# %%
# dump features
with open(args.feature_file, 'wb') as f:
    pickle.dump(features, f)
print(f'Successfully dumped features into {args.feature_file}')
print(f'    {type(features)}, shape = {features.shape}, dtype = {features.dtype}')
