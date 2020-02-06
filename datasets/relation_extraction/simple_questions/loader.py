
def load_simplequestions():
    FILES = ['datasets/simplequestions/annotated_fb_data_test.txt', 'datasets/simplequestions/annotated_fb_data_train.txt', 'datasets/simplequestions/annotated_fb_data_valid.txt']
    # FILES = ['datasets/simplequestions/annotated_fb_data_test.txt']
    questions = []
    labels = []

    for file_path in FILES:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        for line in lines:
            columns = line.split()

            # subject = columns[0]
            relation_uri = columns[1]
            # object_uri = columns[2]
            question = ' '.join(columns[3:])

            questions.append(question)
            labels.append(relation_uri.split('/')[-1])

    return questions, labels


def load_tacred():
    import json
    sentences = []
    relations = []
    subjects = []
    objects = []

    with open('datasets/tacred/train.json') as f:
        examples = json.load(f)
    
    max_seq = 0
    for example in examples:
        tokens = example['token']
        max_seq = max(max_seq, len(tokens))

        sentence = ' '.join(tokens)
        relation = example['relation']
        subject_text = ' '.join(tokens[example['subj_start']:example['subj_end'] + 1])
        object_text = ' '.join(tokens[example['obj_start']:example['obj_end'] + 1])

        sentences.append(sentence)
        relations.append(relation)
        subjects.append(subject_text)
        objects.append(object_text)

    print (max_seq)

load_tacred()


