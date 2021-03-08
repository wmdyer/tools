import sys, argparse, tqdm
import pandas as pd
import numpy as np


def read_file(infilename, ud_columns):
    df = pd.read_csv(infilename, sep='\t', comment='#', header=None, dtype=str, quoting=3, engine='python', error_bad_lines=False, skip_blank_lines=True, index_col=None )
    df.columns = ud_columns

    # make IDX and HEAD numeric
    df[['IDX', 'HEAD']] = df[['IDX', 'HEAD']].apply(pd.to_numeric, errors='coerce')

    # make sure LEMMA is populated
    df = df.loc[df['LEMMA'] != "_"]

    # case-normalize both lemma and wordform
    df['LEMMA'] = df['LEMMA'].str.lower()
    df['WORDFORM'] = df['WORDFORM'].str.lower()

    # populate source conllu file
    df['SOURCE'] = infilename.split('/')[-1]

    return df

def extract(df, outfilename, HAPAX):

    df.to_csv('counts.csv')
    
    df = df.loc[
        # remove multiword tokens
        ('-' not in df['IDX'])

        # remove punctuation
        & (df['UPOS'] != 'PUNCT')

        # remove compounds
        & (df['DEPREL'] != 'compound')
    ]

    df = df.reset_index(drop=True)


    if not HAPAX:
        # build up list of multiply-attested adjs
        ac = pd.DataFrame(df.loc[df['UPOS'] == 'ADJ']['WORDFORM'])
        ac['COUNT'] = 1
        ac = ac.groupby(['WORDFORM']).sum().reset_index()[['WORDFORM', 'COUNT']]
        multi_adj = ac.loc[ac['COUNT'] > 1]['WORDFORM'].values

    # get sentence boundaries
    idx = df['IDX'].values
    sent_idx = [0]
    sent_idx = np.append(sent_idx, np.where(idx[:-1] > idx[1:])[0])
    
    tripfile = open(outfilename, 'w')
    tripfile.write('\t'.join(['triple', 'source']) + '\n')

    count = 0

    # iterate through sentences
    for start in tqdm.tqdm(sent_idx):
        start_idx = np.where(sent_idx == start)[0][0]
        try:
            end = sent_idx[start_idx+1]
            dfs = df.iloc[start:end]
            source = dfs['SOURCE'].values[0]            
        except:
            dfs = df.loc[df['IDX'] == -1]
            source = None

        dfs = dfs.reset_index(drop=True)
        
        # iterate through nouns in sentence
        for i,row in dfs.loc[dfs['UPOS'] == 'NOUN'].iterrows():

            feats = set(['Degree=Cmp', 'Degree=Sup', 'NumType=Ord'])

            adjs = dfs.loc[
                #adjs can't have other deps            
                (~dfs['IDX'].isin(dfs['HEAD'].values))
            
                # adjs must have current noun as head
                & (dfs['HEAD'] == row['IDX'])

                # adjs must have UPOS of 'ADJ'
                & (dfs['UPOS'] == 'ADJ')

                #adjs must have DEPREL of 'amod'
                & (dfs['DEPREL'] == 'amod')
                 
                # adjs can't be comparatives, superlatives, or ordinal numbers
                & (~dfs['FEATS'].apply(lambda x: any([f in str(x).split('|') for f in feats])))

                # adjs should be within two words of their head
                & (np.abs(dfs['IDX'].index.values - dfs['HEAD'].index.values) < 3)
            ]

            if not HAPAX:
                # adjs must be in list of multiply-attested adjs
                adjs = adjs.loc[adjs['WORDFORM'].isin(multi_adj)]

            # must be two adjs
            if len(adjs) == 2:

                # get indexes of 2 adjs and noun
                ids = list(adjs['IDX'].index.values)
                ids.append(row.name)

                # generate triple of wordforms/POS
                tdf = dfs.iloc[np.sort(ids)]
                triple = ','.join(tdf.WORDFORM.astype(str).str.cat(tdf.UPOS.astype(str), sep='/'))
                tripfile.write(triple + '\t' + source + '\n')
                count += 1

    print("extracted " + str(count) + " triples")
    tripfile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='extract triples from conllu file(s)')
    parser.add_argument('-i', '--infile', dest='infile', nargs='+', required=True, help='conllu file(s)')
    parser.add_argument('-o', '--outfile', dest='outfile', nargs=1, required=False, help='triples file (default: triples.csv)')
    parser.add_argument('-hl', '--hapax', dest='hapax', action='store_true', default=False, required=False, help='include hapax legomenon, default false')
    args = parser.parse_args()

    try:
        outfile = args.outfile[0]
    except:
        outfile = "triples.csv"

    ud_columns = ['IDX', 'WORDFORM', 'LEMMA', 'UPOS', 'XPOS', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC', 'SOURCE']
    df = pd.DataFrame(columns = ud_columns)
    
    print("loading ...")
    for i, infile in enumerate(args.infile):
        print("  " + infile)
        df = df.append(read_file(infile, ud_columns[:-1]))

    print("extracting ...")
    extract(df, outfile, args.hapax)
