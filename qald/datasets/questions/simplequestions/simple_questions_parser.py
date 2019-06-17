relation_count = {}
with open(r'datasets\simplequestions\data\annotated_fb_data_train.txt', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        cols = line.split('\t')
        relation = cols[1]
        if relation in relation_count:
            relation_count[relation] += 1
        else:
            relation_count[relation] = 1



relations = [(count, relation) for relation, count in relation_count.items()]

top_relations = sorted(relations, key=lambda t: -t[0])
for relation in top_relations:
    print(relation)
