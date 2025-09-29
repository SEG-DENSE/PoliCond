from sklearn.feature_extraction.text import TfidfVectorizer


def tfidf(docs: [str]) -> [str]:
    """
    calculate the most important features of the documents using TF-IDF
    """
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(docs)
        feature_names = vectorizer.get_feature_names_out()
        important_indices = tfidf_matrix.argmax(axis=1).tolist()[0]
        important_features = [feature_names[i] for i in important_indices]
        return important_features
    except Exception as e:
        print(f"Error in TF-IDF processing: {e}")
        return []


if __name__ == '__main__':
    text1 = "word word word word word"
    text2 = "single word"
    text3 = "single word for testing"
    important_features = tfidf([text1, text2, text3])
    print(important_features)
