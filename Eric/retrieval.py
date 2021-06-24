# %%
import numpy as np
import pickle
import csv
from sklearn.cluster import KMeans
from time import time

# input files
feature_file = 'features/memes_tw.pkl'
tag_file = 'images/memes_tw/tag.csv'

# load features
with open(feature_file, 'rb') as f:
    features = pickle.load(f)
n_image, n_feature = features.shape
features_norm = np.linalg.norm(features, axis=1)
print(f'Successfully loaded features from {feature_file}')
print(f'    {type(features)}, shape = {features.shape}, dtype = {features.dtype}')

# load csv
csv_dict = {}
idx2id = []
with open(tag_file, encoding='utf-8') as f:
    header = f.readline()[:-1]
    reader = csv.reader(f)
    for row in reader:
        id_ = int(row[0])
        base = row[1]
        cls = row[2] if len(row) > 2 else ''
        tags = row[3:]
        csv_dict[id_] = (base, cls, tags)
        idx2id.append(id_)
print(f'Successfully loaded tags from {tag_file}')
print('    header:', header)
print('    #row =', len(idx2id))
assert n_image == len(idx2id)

# idx2id[idx] = id_
# id2idx[id_] = idx
id2idx = {}
for idx, id_ in enumerate(idx2id):
    id2idx[id_] = idx

def retrieve_cosine(vec, n_ranklist):
    cosines = (features @ vec[:, np.newaxis]).ravel() / features_norm
    # cosine = cec @ features.T
    indices = np.argsort(cosines)[-n_ranklist:][::-1]
    return [idx2id[idx] for idx in indices]

def retrieve(feedback_ids, n_ranklist=10):
    # average
    average_vec = np.zeros(n_feature)
    for id_ in feedback_ids:
        idx = id2idx[id_]
        average_vec += features[idx]
    if len(feedback_ids) > 0:
        average_vec /= len(feedback_ids)

    # find nearest neighbors
    ids = retrieve_cosine(average_vec, n_ranklist)
    return ids

# KMeans

# t = time()
# print('Clustering with KMeans ...')
# kmeans = KMeans(n_clusters=20, random_state=0, max_iter=5).fit(features)
# print(f'KMeans took {time()-t:.2f} seconds') # KMeans took 201.32 seconds
# with open('kmeans.pkl', 'wb') as f:
#     pickle.dump(kmeans, f)

# with open('kmeans.pkl', 'rb') as f:
#     kmeans = pickle.load(f)
# for i in range(20):
#     print(retrieve_cosine(kmeans.cluster_centers_[i], n_ranklist=1))

if __name__ == '__main__':
    from code import InteractiveConsole
    console = InteractiveConsole(locals=locals())
    console.interact()