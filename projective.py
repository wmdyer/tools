import pandas as pd
import networkx as nx
import argparse, sys

def load_ud_file(filename):
    ud = pd.read_csv(filename, sep="\t",error_bad_lines=False, engine='python', header=None, comment= '#', quoting=3)
    ud.columns = ['idx', 'wordform', 'lemma', 'ud_pos', 'sd_pos', 'morph', 'head', 'rel1', 'rel2', 'other']
    return ud

def print_progress(i, n, s):
    j = (i+1) / n
    sys.stdout.write('\r')
    sys.stdout.write("[%-20s] %d%% N %d/%d %s" % ('='*int(20*j), 100*j, i, n, s))
    sys.stdout.flush()
    return i + 1

def analyze(g):
    np_words = set()
    doms = {}
    
    # for each node in g, get list of dominating nodes
    for node in g:
        doms[node] = nx.shortest_path(g, source=0, target=node)

    # for each edge (u,v) in g, determine whether all intervening words (ids) are dominated by u
    for edge in g.edges():
        u = edge[0]
        v = edge[1]
        i = 1
        if u > v:
            i = -1
        for n in range(u+i,v,i):
            if u not in doms[n]:
                np_words.add(n)
    n = len(np_words)

    # return whether this tree has a non-projective dependency and number of non-projective words (ids)
    return int(n>0), n


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='measure projectivity in conllu file')
    parser.add_argument('ud_file', help='UD conllu file')
    args = parser.parse_args()

    df = load_ud_file(args.ud_file)

    G = None
    num_sent = 0
    num_word = 0
    n=df.shape[0]
    sid = 0
    wid = 0

    # iterate through conllu file, building up a graph G for each sentence,
    #   then analyze G for non-projectivity once it's complete
    for i,row in df.iterrows():
        print_progress(i+1, n, "")
        try:
            idx = int(row['idx'])
            head = int(row['head'])
            if idx == 1:
                sid += 1
                if G is not None:
                    ns, nw = analyze(G)
                    num_sent+=ns
                    num_word+=nw
                G = nx.DiGraph()
            wid+=1
            G.add_edge(head, idx)
        except:
            pass
        
    # analyze final tree in conllu file
    ns, nw = analyze(G)
    num_sent+=ns
    num_word+=nw    

    print("\n\nnon-projective")
    print(" sents: {:.4f} {}/{}".format(num_sent/sid, num_sent, sid))
    print(" words: {:.4f} {}/{}".format(num_word/wid, num_word, wid))    
    
