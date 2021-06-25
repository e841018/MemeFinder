import random

questions = []
with open('questions.csv') as f:
    header = f.readline()
    while True:
        line = f.readline()
        if line == '':
            break
        img_id, quadrant = line.strip().split(',')
        questions.append([int(img_id), int(quadrant)])

def sample_quiz(k=20):
    return random.sample(questions, k)
