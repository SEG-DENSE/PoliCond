#!/usr/bin/env python3
# coding: utf-8
import argparse
import csv
import os
import sqlite3

import pandas as pd


# Convert SQLite DB to CSV
def dumpTable(conn, query, fname, directory, header):
    table = [data for data in conn.cursor().execute(query)]
    output_path = os.path.join(directory, fname)
    os.makedirs(directory, exist_ok=True)  # Ensure output directory exists
    with open(output_path, 'w', encoding='utf-8', newline='') as outputfile:
        csvfile = csv.writer(outputfile, delimiter=',')
        csvfile.writerow(header)
        for row in table:
            csvfile.writerow(row)

def dbToCsv(dbPath, output_dir="."):
    conn = sqlite3.connect(dbPath)
    dumpTable(conn, 'SELECT policyId,entity,collect,data FROM Policy', "Policy.csv", output_dir, ("policyId", "entity", "action", "data"))
    dumpTable(conn, 'SELECT id,sentenceId,policyId,appId FROM AppPolicySentences', "PolicySentences.csv", output_dir, ["id", "sentenceId", "policyId", "appId"])
    dumpTable(conn, 'SELECT flowId,flowEntity,flowData FROM DataFlows', "DataFlows.csv", output_dir, ["flowId", "flowEntity", "flowData"])
    dumpTable(conn, 'SELECT appFlowId,flowId,appId,rawEntity,rawData FROM AppDataFlows', "AppDataFlows.csv", output_dir, ["appFlowId", "flowId", "appId", "rawEntity", "rawData"])
    dumpTable(conn, 'SELECT consistId,flowId,appId,isConsistent FROM ConsistencyResult', "ConsistencyResult.csv", output_dir, ["consistId", "flowId", "appId", "isConsistent"])
    dumpTable(conn, 'SELECT cdid,consistId,policyStatement,contradictingStatement,contradictionNum FROM ConsistencyData', "ConsistencyData.csv", output_dir, ["cdid", "consistId", "policyStatement", "contradictingStatement", "contradictionNum"])
    dumpTable(conn, 'SELECT contrId,contradictionId,appId,policyId1,policyId2 FROM Contradiction', "Contradiction.csv", output_dir, ["cid", "contrId", "packageName", "policyStatement", "contradictingStatement"])
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Process a database file.')
    parser.add_argument('db_path', type=str, help='Path to the .db file')
    args = parser.parse_args()
    db_path = args.db_path

    output_dir = "."
    dbToCsv(db_path, output_dir)

    # Read CSV files with UTF-8 encoding
    policyCsv = os.path.join(output_dir, "Policy.csv")
    policyDf = pd.read_csv(policyCsv,
                           usecols=["policyId","entity","action","data"],
                           dtype={
                               "policyId" : int, "entity" : str,"action" : str,"data" : str
                           },
                           skip_blank_lines=True,
                           encoding='utf-8')
    policyDf.fillna({"policyId" : -1, "entity" : '', "action" : '' ,"data" : ''}, inplace=True)

    dataflowCsv = os.path.join(output_dir, "DataFlows.csv")
    dataflowDf = pd.read_csv(dataflowCsv,
                             usecols=["flowId", "flowEntity", "flowData"],
                             dtype={
                                 "flowId" : int, "flowEntity" : str, "flowData" : str
                             },
                             skip_blank_lines=True,
                             encoding='utf-8')
    dataflowDf.fillna({"flowId" : -1, "flowEntity" : '', "flowData" : ''}, inplace=True)

    appDataflowCsv = os.path.join(output_dir, "AppDataFlows.csv")
    appDataflowDf = pd.read_csv(appDataflowCsv,
                                usecols=["appFlowId", "flowId", "appId", "rawEntity", "rawData"],
                                dtype={
                                    "appFlowId" : int, "flowId" : int, "appId" : str, "rawEntity" : str, "rawData" : str
                                },
                                skip_blank_lines=True,
                                encoding='utf-8')
    appDataflowDf.fillna({"appFlowId" : -1, "flowId" : -1, "appId" : '', "rawEntity" : '', "rawData" : ''}, inplace=True)

    policySentencesCsv = os.path.join(output_dir, "PolicySentences.csv")
    policySentencesDf = pd.read_csv(policySentencesCsv,
                                    usecols=["id", "sentenceId", "policyId", "appId"],
                                    dtype={
                                        "id" : int, "sentenceId" : str, "policyId" : int, "appId" : str
                                    },
                                    skip_blank_lines=True,
                                    encoding='utf-8')
    policySentencesDf.fillna({"id" : -1, "sentenceId" : '', "policyId" : -1, "appId" : ''}, inplace=True)

    consistencyResultCsv = os.path.join(output_dir, "ConsistencyResult.csv")
    conResDf = pd.read_csv(consistencyResultCsv,
                           usecols=["consistId", "flowId", "appId", "isConsistent"],
                           dtype={
                               "consistId" : int, "flowId" : int, "appId" : str, "isConsistent" : str
                           },
                           skip_blank_lines=True,
                           encoding='utf-8')
    conResDf.fillna({"consistId" : -1, "flowId" : -1, "appId" : '', "isConsistent" : ''}, inplace=True)

    contradictionMap = {
        -1 : None, 0  : "C1", 1  : "C2", 2  : "N1", 3  : "C6", 4  : "C3", 5  : "C4", 6  : "N2", 7  : "C7", 8  : "N3",
        9  : "C5", 10 : "N4", 11 : "C8", 12 : "C9", 13 : "C10", 14 : "C11", 15 : "C12",
    }

    consistencyDataCsv = os.path.join(output_dir, "ConsistencyData.csv")
    conDataDf = pd.read_csv(consistencyDataCsv,
                            usecols=["cdid", "consistId", "policyStatement", "contradictingStatement", "contradictionNum"],
                            dtype={
                                "cdid" : int, "consistId" : int, "policyStatement" : int,
                                "contradictingStatement" : float, "contradictionNum" : int,
                            },
                            skip_blank_lines=True,
                            encoding='utf-8')
    conDataDf.fillna({"cdid" : -1, "consistId" : -1, "policyStatement" : -1,
                      "contradictingStatement" : -1, "contradictionNum" : -1}, inplace=True)
    conDataDf["contradictionNum"] = conDataDf["contradictionNum"].replace(contradictionMap)
    conDataDf[["contradictingStatement"]] = conDataDf[["contradictingStatement"]].apply(pd.to_numeric, downcast='integer')

    contradictionDataCsv = os.path.join(output_dir, "Contradiction.csv")
    contrDataDf = pd.read_csv(contradictionDataCsv,
                              usecols=["cid", "contrId", "packageName", "policyStatement", "contradictingStatement"],
                              dtype={
                                  "cid" : int, "contrId" : int, "packageName" : str, "policyStatement" : float,
                                  "contradictingStatement" : float,
                              },
                              skip_blank_lines=True,
                              encoding='utf-8')
    contrDataDf.fillna({"cid" : -1, "contrId" : -1,  "packageName" : '', "policyStatement" : -1,
                        "contradictingStatement" : -1}, inplace=True)
    contrDataDf["contrId"] = contrDataDf["contrId"].replace(contradictionMap)
    contrDataDf[["policyStatement"]] = contrDataDf[["policyStatement"]].apply(pd.to_numeric, downcast='integer')
    contrDataDf[["contradictingStatement"]] = contrDataDf[["contradictingStatement"]].apply(pd.to_numeric, downcast='integer')

    def getSentences(policyId, appId):
        res = policySentencesDf.loc[(policySentencesDf["appId"] == appId) & (policySentencesDf["policyId"] == policyId)]
        return set([sentenceText for _, _, sentenceText, _, _ in res.itertuples()])

    def resolvePolicyStatement(pid):
        if pid is None or pid == -1:
            return (None, None, None)
        _, pEntity, pSentiment, pData = policyDf.loc[policyDf["policyId"] == pid].values[0]
        return (pEntity, pSentiment, pData)

    def writeCsvHeader(csvfile):
        csvfile.writerow(("packageName", "policyEntity", "policyAction", "policyData", "policySentences", "contradictionNum", "contradictoryEntity", "contradictoryAction", "contradictoryData", "contradictionSentences"))

    def writeCsvRow(csvfile, packageName, policyEntity, policyAction, policyData, policySentences, contradictionNum, contradictoryEntity, contradictoryAction, contradictoryData, contradictionSentences):
        csvfile.writerow((packageName, policyEntity, policyAction, policyData, policySentences.encode("utf-8") if policySentences is not None else None, contradictionNum, contradictoryEntity, contradictoryAction, contradictoryData, contradictionSentences.encode("utf-8") if contradictionSentences is not None else None))

    # Write final output CSV
    output_path = './policylint_results.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure output directory exists
    with open(output_path, 'w', encoding='utf-8', newline='') as outputfile:
        csvfile = csv.writer(outputfile, delimiter=',')
        writeCsvHeader(csvfile)

        for _, cid, contrId, packageName, policyStatement, contradictingStatement in contrDataDf.itertuples():
            sentences1 = getSentences(policyStatement, packageName)
            sentences2 = getSentences(contradictingStatement, packageName)
            if len(sentences1) == 0 or len(sentences2) == 0 or sentences1 == sentences2 or sentences1.issubset(sentences2) or sentences2.issubset(sentences1):
                continue
            pEntity, pSentiment, pData = resolvePolicyStatement(policyStatement)
            cEntity, cSentiment, cData = resolvePolicyStatement(contradictingStatement)
            writeCsvRow(csvfile, packageName, pEntity, pSentiment, pData, "||".join(list(sentences1-sentences2)), contrId, cEntity, cSentiment, cData, "||".join(list(sentences2-sentences1)))

if __name__ == "__main__":
    # example usage:
    # python FixedRemoveSameSentenceContradictions.py "..\consistency_results_1.db""
    main()