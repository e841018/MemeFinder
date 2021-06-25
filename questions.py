from PIL import Image
import numpy as np
import random as rd
import os

imgIds = []
img_path1 = './images/1~2868/'
img_path2 = './images/2869~/'
with open("./tfidf/ocr_texts/text.csv", "r") as f:
    lines = f.readlines()

for line in lines:
    imgIds.append(line.split(",")[0])

imgNum = len(imgIds)
questionNum = int(input("number of image: ")) 
qids = rd.sample(imgIds, k=questionNum)

qpairs = []

for qid in qids:
    if os.path.isfile(img_path1+qid+'.jpg'):
        img = Image.open(img_path1+qid+'.jpg')
    elif os.path.isfile(img_path2+qid+'.jpg'):
        img = Image.open(img_path2+qid+'.jpg')
    else:
        print(f"[!] image {qid}.jpg not exists!") 

    img_array = np.array(img)
    h, w, c = img_array.shape
    maskp = rd.randint(1, 4)
    if maskp == 2:
        img_array[:h//2, :w//2, :] = 0
    elif maskp == 3:
        img_array[h//2:, :w//2, :] = 0
    elif maskp == 4:
        img_array[h//2:, w//2:, :] = 0
    else:
        img_array[:h//2, w//2:, :] = 0

    Image.fromarray((img_array).astype(np.uint8)).save('./questions/' + qid + '_' + str(maskp) + '.jpg')
    qpairs.append((int(qid), maskp))

with open("./questions.csv", 'w') as f:
    f.write(f"ImageId,quadrant\n")
    for qpair in qpairs:
        f.write(f"{qpair[0]},{qpair[1]}\n")


    
