from services.parser.tree2labels.tree import SeqTree, RelativeLevelTreeEncoder
from services.parser.tree2labels.dataset import _set_tag_for_leaf_unary_chain

def transform_split(path, binarized, dummy_tokens, root_label,encode_unary_leaf, abs_top,
                    abs_neg_gap, join_char,split_char):

    BOS = "-BOS-"
    EOS = "-EOS-"
    EMPTY = "-EMPTY-"

    with open(path, encoding="utf-8") as f:
        trees = f.readlines()
    
    sequences = []
    sequences_for_leaf_unaries = []
    for tree in trees:

        tree, tokens = tree.split('|')
        words = [token.strip() for token in tokens.split(' ')]

        tree = SeqTree.fromstring(tree, remove_empty_top_bracketing=True)

        tree.set_encoding(RelativeLevelTreeEncoder())
        used_words = tree.leaves()

        tags = [s.label() for s in tree.subtrees(lambda t: t.height() == 2)]
        tree.collapse_unary(collapsePOS=True, collapseRoot=True)    
        unary_sequence =  [s.label() for s in tree.subtrees(lambda t: t.height() == 2)] 
        
        used_gold = [(w,t,g) for w,t,g in zip(used_words, tags, tree.to_maxincommon_sequence(is_binary=binarized,
                                                                                #dummy_tokens=dummy_tokens,
                                                                                root_label=root_label,
                                                                                encode_unary_leaf=encode_unary_leaf,
                                                                                # abs_top=abs_top,
                                                                                # abs_neg_gap=abs_neg_gap
                                                                                ))]
        gold = []
        used_index = 0

        for i in range(len(words)):
            if str(i) in used_words:
                _, t, g = used_gold[used_index]
                used_index += 1
            else:
                t, g = 'TOKEN', 'UNUSED'
            gold.append((words[i],t,g))
        
        if dummy_tokens:
            gold.insert(0, (BOS, BOS, BOS) )
            gold.append( (EOS, EOS, EOS) )
        sequences.append(gold)
        
        gold_unary_leaves = []
        gold_unary_leaves = [(BOS, BOS, BOS) ]
        gold_unary_leaves.extend( [(w,t, _set_tag_for_leaf_unary_chain(unary) ) for w,t,unary in zip(words, tags, unary_sequence)] )
        gold_unary_leaves.append((EOS, EOS, EOS))
        sequences_for_leaf_unaries.append(gold_unary_leaves)
    return sequences, sequences_for_leaf_unaries

def postprocess_labels(preds):
    
    #This situation barely happens with LSTM's models
    for i in range(1, len(preds)-2):
        if preds[i] in ["-BOS-","-EOS-"] or preds[i].startswith("NONE"):
            preds[i] = "ROOT_S"
    
    #TODO: This is currently needed as a workaround for the retagging strategy and sentences of length one
    if len(preds)==3 and preds[1] == "ROOT":
        preds[1] = "NONE"        
    
    return preds