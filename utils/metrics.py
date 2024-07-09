'''
    Description: script to calculate all similarity metrics
'''
from Levenshtein import distance


# Calculate all similiarity measures
def dataframe_similarity(df1,df2):
    result_full = dataframe_similiarity_full(df1,df2)
    result_relax = dataframe_similarity_relaxed(df1,df2)
    result_textual = dataframe_similiarity_textual(df1,df2,0.75)

    return {'precision':round(result_full['precision'],3), 'recall':round(result_full['recall'],3), 'f1':round(result_full['f1'],3)
            ,'relaxed_precision':round(result_relax['precision'],3), 'relaxed_recall':round(result_relax['recall'],3), 'relaxed_f1':round(result_relax['f1'],3)
            ,'textual_precision':round(result_textual['precision'],3), 'textual_recall':round(result_textual['recall'],3), 'textual_f1':round(result_textual['f1'],3)
            }


##### Comparison based on all columns
def dataframe_similiarity_full(df1,df2):

   # Ensure both dataframes compare the same columns, sorted alphabetically
    if set(df1.columns) != set(df2.columns):
        return "Can't calculate Precision, Recall and F1. DataFrames must have the same columns"
     
    df1 = df1.sort_values(by=list(df1.columns)).reset_index(drop=True)
    df2 = df2.sort_values(by=list(df1.columns)).reset_index(drop=True)

    # Create tuples of the rows
    df1['combined'] = df1.apply(lambda row: tuple(row), axis=1)
    df2['combined'] = df2.apply(lambda row: tuple(row), axis=1)
    
    # Create sets of the tuple rows for fast comparison
    set_df1 = set(df1['combined'])
    set_df2 = set(df2['combined'])
    
    # True Positives (TP): Items in both sets
    tp = len(set_df1.intersection(set_df2))
    
    # False Positives (FP): Items in df1 but not in df2
    fp = len(set_df1 - set_df2)
    
    # False Negatives (FN): Items in df2 but not in df1
    fn = len(set_df2 - set_df1)
    
    # Calculating precision, recall, and F1-score
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {'precision':round(precision,3), 'recall':round(recall,3), 'f1':round(f1,3) }


##### Comparison based on all columns except activity_id
def dataframe_similarity_relaxed(df1, df2):
    
    # drop columns with activity_id
    df1=df1.drop(['activity_id'], axis=1)
    df2=df2.drop(['activity_id'], axis=1)

   # Ensure both dataframes compare the same columns, sorted alphabetically
    if set(df1.columns) != set(df2.columns):
        return "Can't calculate Precision, Recall and F1. DataFrames must have the same columns"

    df1 = df1.sort_values(by=list(df1.columns)).reset_index(drop=True)
    df2 = df2.sort_values(by=list(df1.columns)).reset_index(drop=True)
    
    # Create tuples of the rows
    df1['combined'] = df1.apply(lambda row: tuple(row), axis=1)
    df2['combined'] = df2.apply(lambda row: tuple(row), axis=1)
    
    # Create sets of the tuple rows for fast comparison
    set_df1 = set(df1['combined'])
    set_df2 = set(df2['combined'])
    
    # True Positives (TP): Items in both sets
    tp = len(set_df1.intersection(set_df2))
    
    # False Positives (FP): Items in df1 but not in df2
    fp = len(set_df1 - set_df2)
    
    # False Negatives (FN): Items in df2 but not in df1
    fn = len(set_df2 - set_df1)
    
    # Calculating precision, recall, and F1-score
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0    

    return {'precision':round(precision,3), 'recall':round(recall,3), 'f1':round(f1,3)}


##### Comparison based on all columns using Levenshtein distance
def dataframe_similiarity_textual(df1,df2, threshold=0.75):

   # Ensure both dataframes compare the same columns, sorted alphabetically
    if set(df1.columns) != set(df2.columns):
        return "Can't calculate Precision, Recall and F1. DataFrames must have the same columns"

    df1 = df1.sort_values(by=list(df1.columns)).reset_index(drop=True)
    df2 = df2.sort_values(by=list(df1.columns)).reset_index(drop=True)

    ##### Textual comparison based on all columns
    tp, fp, fn = 0, 0, 0

    df2.fillna("",inplace=True)

    labels = df1.apply(";".join, axis=1)
    preds = df2.apply(";".join, axis=1)

    for label in labels:
        similarity_list=[]
        for pred in preds:
            similarity_list.append(distance(label,pred)/max(len(label), len(pred)))
        similarity_score = 1 - min(similarity_list) 
        if similarity_score >= threshold:
            tp += 1
        else:
            fp += 1

    fn = max(len(labels),len(preds)) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0 

    return {'precision':round(precision,3), 'recall':round(recall,3), 'f1':round(f1,3)}