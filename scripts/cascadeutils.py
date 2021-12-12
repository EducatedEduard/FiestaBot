import os

def generate_negative_description_file():
    with open('neg.txt', 'w') as f:
        for filename in os.listdir('train/negative'):
            f.write('negative/' + filename + '\n')


print('Generating neg.txt')
generate_negative_description_file()
