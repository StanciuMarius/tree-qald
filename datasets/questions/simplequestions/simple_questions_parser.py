import json
import os
import sys
import random
sys.path.insert(0, os.getcwd())

relation_count = {}
question_sample_count = 500
question_samples = []
max_count = 0

with open(r'datasets\questions\simplequestions\data\annotated_fb_data_train.txt', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        cols = line.split('\t')
        relation = cols[1]
        if relation in relation_count:
            relation_count[relation] += 1
            max_count = max(relation_count[relation], max_count)
        else:
            relation_count[relation] = 1

    # pick some random question samples. Sample probability is proportional to the relation count
    # random.shuffle(lines)
    # for line in lines:
    #     cols = line.split('\t')
    #     relation = cols[1]
    #     count = relation_count[relation]
    #     weight = count / max_count
    #     prob = random.uniform(0, 1)
    #     if prob < weight:
    #         question_samples.append(' '.join(cols[3:]))
    #     if len(question_samples) >= question_sample_count:
    #         break



# with open(r'datasets\questions\simplequestions\data\fb_train_500_samples.txt', 'w', encoding='utf-8') as output_file:
#     for index, question in enumerate(question_samples):
#         output_file.write(str(index) + '|' + question)


# with open(r'datasets\questions\simplequestions\data\annotated_fb_data_train.txt', 'r', encoding='utf-8') as input_file:
#     question_vs_relation = {}
#     lines = input_file.readlines()
#     for line in lines:
#         cols = line.split('\t')
#         relation = cols[1]
#         question = ' '.join(cols[3:]).strip()
#         question_vs_relation[question] = relation.replace('www.freebase.com/', 'fb:')

#     with open('annotator\qald_annotated_trees.json', 'r', encoding='utf-8') as output_file:
#         example_array = json.load(output_file)
#         for example in example_array:
#             question = ' '.join(example['tokens']).strip()
#             if question not in question_vs_relation:
#                 print(question)
#             else:
#                 pass
                # print(question_vs_relation[question])

# relations = [(count, relation) for relation, count in relation_count.items()]

# top_relations = sorted(relations, key=lambda t: -t[0])
# for relation in top_relations:
#     print(relation)
