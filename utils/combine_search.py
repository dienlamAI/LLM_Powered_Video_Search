import numpy as np
import torch
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def merge_searching_results(list_scores, list_indices, list_image_paths):
    '''
    Arg:
      list_scores: List[np.array]
      list_indices: List[np.array]
    '''
    normalized_list_scores = []
    list_image_paths_refined = []
    for score, image_path in zip(list_scores, list_image_paths):
      normalized_list_scores.append(score/np.linalg.norm(score))
      list_image_paths_refined.extend(image_path)

    normalized_list_scores = np.concatenate(normalized_list_scores)
    list_indices_refined = np.concatenate(list_indices)
    list_image_paths_refined = np.array(list_image_paths_refined)

    sorted_indices = np.argsort(normalized_list_scores)[::-1]
    normalized_list_scores = normalized_list_scores[sorted_indices]
    list_indices_refined = list_indices_refined[sorted_indices]
    list_image_paths_refined = list_image_paths_refined[sorted_indices]

    _, unique_indices = np.unique(list_indices_refined, return_index=True)
    
    return normalized_list_scores[unique_indices], list_indices_refined[unique_indices], list_image_paths_refined[unique_indices]

def merge_searching_results_by_addition(list_scores, list_indices):
    '''
    Arg:
      list_scores: List[np.array]
      list_indices: List[np.array]
    '''

    if len(list_scores) == 1:
      return list_scores[0], list_indices[0]
    
    # Normalize score
    new_list_scores = []
    for scores in list_scores:
      new_scores = (scores-np.min(scores))/(np.max(scores)-np.min(scores)+0.000001)
      new_list_scores.append(new_scores)

    result_dict = dict()
    for scores, indices in zip(new_list_scores, list_indices):
      for score, idx in zip(scores, indices):
        if not (result_dict.get(idx, False)):
          result_dict[idx] = score
        else:
          result_dict[idx] = result_dict[idx] + score
    
    scores, idx_image = [], []
    for idx, score in result_dict.items():
      idx_image.append(idx)
      scores.append(score)
    
    idx_image = np.array(idx_image).astype(int)
    scores = np.array(scores)

    sort_index = np.argsort(scores)[::-1]
    scores = scores[sort_index]
    idx_image = idx_image[sort_index]

    return scores, idx_image

def combined_ranking_score(list_results, topk=None, alpha=0.5, beta=0.5, k=60):
    df = pd.DataFrame({
        'scores': np.concatenate([item[0] for item in list_results]),
        'idx_image': np.concatenate([item[1] for item in list_results]),
        'frame_idx': np.concatenate([item[2] for item in list_results]),
        'image_paths': np.concatenate([item[3] for item in list_results]),
        'rank': np.concatenate([item[4] for item in list_results]),
        'source': np.concatenate([item[5] for item in list_results])
    })
    
    min_score = df['scores'].min()
    max_score = df['scores'].max()
    
    if max_score == min_score:
        df['normalized_scores'] = 0
    else:
        df['normalized_scores'] = (df['scores'] - min_score) / (max_score - min_score)

    df['crs_scores'] = alpha * (1 / (k+df['rank'])) + beta * df['normalized_scores']/ (k+df['rank'])
    
    df = df.groupby('image_paths').agg({
        'crs_scores': 'sum',
        'idx_image': 'first',
        'frame_idx': 'first',
        'rank': 'first',
        'source': 'first'
    }).reset_index()
    
    df = df[df['image_paths'] != '']
    df = df.sort_values('crs_scores', ascending=False)

    if topk is not None:
        df = df.head(topk)
    
    return list(df['crs_scores']), list(df["idx_image"]), list(df['frame_idx']), list(df['image_paths']), list(df['source'])

def maximal_marginal_relevance(query_embedding, doc_embeddings, lambda_param=0.5, top_k=5):
    """
    Áp dụng thuật toán Maximal Marginal Relevance (MMR) để chọn các kết quả dựa trên tính liên quan và đa dạng.
    
    Args:
        query_embedding (np.array): Vector embedding của truy vấn.
        doc_embeddings (np.array): Ma trận embedding của các tài liệu.
        lambda_param (float): Tham số điều chỉnh giữa tính liên quan và tính đa dạng.
        top_k (int): Số lượng kết quả trả về.

    Returns:
        selected_docs (list): Danh sách chỉ số của các tài liệu đã chọn.
    """
    # Tính độ tương đồng cosine giữa truy vấn và các tài liệu
    query_similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
    
    # Tính độ tương tự giữa các tài liệu với nhau
    doc_pairwise_similarities = cosine_similarity(doc_embeddings)
    
    selected_docs = []
    candidate_docs = list(range(len(doc_embeddings)))

    # Chọn tài liệu có độ tương đồng lớn nhất với truy vấn làm kết quả đầu tiên
    first_doc = np.argmax(query_similarities)
    selected_docs.append(first_doc)
    candidate_docs.remove(first_doc)
    
    # Lặp để chọn các tài liệu tiếp theo
    for _ in range(top_k - 1):
        mmr_scores = []
        for doc in candidate_docs:
            # Độ tương tự của tài liệu với truy vấn (liên quan)
            relevance = query_similarities[doc]
            
            # Độ tương tự của tài liệu với những tài liệu đã được chọn (đa dạng)
            diversity = max([doc_pairwise_similarities[doc][selected] for selected in selected_docs])
            
            # Tính điểm MMR
            mmr_score = lambda_param * relevance - (1 - lambda_param) * diversity
            mmr_scores.append(mmr_score)
        
        # Chọn tài liệu có điểm MMR cao nhất
        next_doc = candidate_docs[np.argmax(mmr_scores)]
        selected_docs.append(next_doc)
        candidate_docs.remove(next_doc)
    
    return selected_docs