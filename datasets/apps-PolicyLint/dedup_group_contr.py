import pandas as pd


def dedup_contradiction_in_poligraph(output_file_csv):
    path = r'<PATH>\policylint-reclassify.csv'

    df = pd.read_csv(path, encoding='utf-8')
    df = df[['app_id', 'pos_text', 'neg_text']]
    df = df.drop_duplicates(keep='first', ignore_index=True)
    df['id'] = df.index + 1
    # before dumpint to csv, we need to make sure that the column id is the first column
    df = df[['id', 'app_id', 'pos_text', 'neg_text']]
    df.to_csv(output_file_csv, encoding='utf-8', index=False)


def dedup_contradiction_in_policyLint(output_file_csv):
    path = r'<PATH>\policylint_results.csv'

    df = pd.read_csv(path, encoding='utf-8')
    # packageName	policyEntity	policyAction	policyData	policySentences	contradictionNum	contradictoryEntity	contradictoryAction	contradictoryData	contradictionSentences
    df = df[['packageName', 'policySentences', 'contradictionSentences']]
    # exchange policySentences and contradictionSentences
    # make sure in dictionary order, str(policySentences) < str(contradictionSentences)
    df['policySentences'] = df['policySentences'].astype(str)
    df['contradictionSentences'] = df['contradictionSentences'].astype(str)
    minMap, maxMap = {}, {}
    for index, row in df.iterrows():
        row = row.to_dict()
        minMap[index] = min(row['policySentences'], row['contradictionSentences'])
        maxMap[index] = max(row['policySentences'], row['contradictionSentences'])

        if row['policySentences'] != minMap[index]:
            print(f"row {index} exchange policySentences and contradictionSentences")
            print(f"original policySentences: {row['policySentences']}")
            print(f"new policySentences: {minMap[index]}")
            df.at[index, 'policySentences'] = minMap[index]
            df.at[index, 'contradictionSentences'] = maxMap[index]
            print(df.at[index, 'policySentences'])
            print("------------------------------")
    df = df.drop_duplicates(keep='first', ignore_index=True,
                            subset=['packageName', 'policySentences', 'contradictionSentences'])
    df['id'] = df.index + 1
    # before dumpint to csv, we need to make sure that the column id is the first column
    df = df[['id', 'packageName', 'policySentences', 'contradictionSentences']]
    df.to_csv(output_file_csv, encoding='utf-8', index=False)


if __name__ == '__main__':
    # dedup_contradiction_in_poligraph()
    # dedup_contradiction_in_policyLint()
    pass