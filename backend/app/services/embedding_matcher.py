# Import the built-in os module
# We use this to read environment variables from the system
import os

# Import Python's built-in regular expression module
# This helps us search and split text using patterns
import re

# Import type hints from typing
# Final = value should not be changed
# List = list type
# Set = set type
from typing import Final, List, Set

# Import NumPy, a library for numerical operations
# It is commonly used for arrays, vectors, and math
import numpy as np

# Import SentenceTransformer from sentence_transformers
# This model turns text into embeddings (number vectors)
from sentence_transformers import SentenceTransformer

# Set the model name to use for embeddings
# os.getenv(...) checks if EMBEDDING_MODEL exists in environment variables
# If not, it uses "all-MiniLM-L6-v2" as the default
MODEL_NAME: Final[str] = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Load the sentence transformer model one time
# This model will later convert text into vector embeddings
_model = SentenceTransformer(MODEL_NAME)


# Define a helper function to clean text
# It takes a string and returns a cleaned string
def _clean_text(text: str) -> str:
    # text.split() breaks text into words and removes extra spaces/newlines
    # " ".join(...) joins the words back with a single space between them
    # .strip() removes spaces at the beginning and end
    return " ".join(text.split()).strip()


# Define a function to split large text into smaller chunks
# max_chunk_words says how many words we allow in each chunk
def _split_into_chunks(text: str, max_chunk_words: int = 80) -> List[str]:
    """
    Split text into chunks so local matches are easier to detect.
    """
    # Clean the text first so spacing is consistent
    text = _clean_text(text)

    # If text is empty after cleaning, return an empty list
    if not text:
        return []

    # Split text into sentences
    # The regex looks for punctuation like . ! ? followed by spaces
    # or new lines
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)

    # Remove empty pieces and trim spaces around each sentence
    sentences = [s.strip() for s in sentences if s.strip()]

    # This will store the final chunks
    chunks: List[str] = []

    # This stores sentences for the chunk currently being built
    current_chunk: List[str] = []

    # Keep track of how many words are in the current chunk
    current_word_count = 0

    # Go through each sentence one by one
    for sentence in sentences:
        # Count how many words are in this sentence
        word_count = len(sentence.split())

        # If adding this sentence would make the chunk too big,
        # save the current chunk and start a new one
        if current_chunk and current_word_count + word_count > max_chunk_words:
            # Join the current chunk sentences into one string and save it
            chunks.append(" ".join(current_chunk))

            # Start a new chunk with the current sentence
            current_chunk = [sentence]

            # Reset word count for the new chunk
            current_word_count = word_count
        else:
            # Otherwise, add the sentence to the current chunk
            current_chunk.append(sentence)

            # Update the total word count
            current_word_count += word_count

    # After the loop, if there is still a chunk being built, save it
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # Return the list of text chunks
    return chunks


# Define a function to extract keywords from text
# It returns a set of keywords
def _extract_keywords(text: str) -> Set[str]:
    """
    Very simple keyword extraction.
    This can be replaced later with a more advanced skill extractor.
    """
    # Convert everything to lowercase so matching is easier
    text = text.lower()

    # Use regex to find words/tokens
    # Examples it may catch: python, sql, c++, node.js
    # set(...) removes duplicates automatically
    tokens = set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.\-]{1,}\b", text))

    # These are common words we do not want to count as keywords
    # They are called stopwords
    stopwords = {
        "the", "and", "for", "with", "you", "your", "are", "our", "this", "that",
        "from", "have", "has", "will", "into", "they", "them", "their", "job",
        "role", "work", "team", "using", "used", "use", "years", "year", "plus",
        "who", "what", "when", "where", "how", "why", "can", "may", "should",
        "must", "about", "than", "then", "also", "all", "any", "not", "but",
        "his", "her", "she", "him", "its", "too", "per", "etc"
    }

    # Return only tokens that are not in the stopwords list
    return {token for token in tokens if token not in stopwords}


# Define a function to convert text strings into embeddings
# Embeddings are lists of numbers that represent meaning
def _embed_texts(texts: List[str]) -> np.ndarray:
    # _model.encode(...) converts each text into a vector
    # convert_to_numpy=True makes the result a NumPy array
    # normalize_embeddings=True makes each vector length = 1
    # This is useful for cosine similarity
    return _model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )


# Define a function to calculate similarity between two normalized vectors
def _cosine_from_normalized(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    For normalized vectors, cosine similarity is the dot product.
    """
    # Since both vectors are normalized, dot product = cosine similarity
    # np.dot multiplies the vectors and sums the result
    return float(np.dot(vec_a, vec_b))


# Define a function to compare the full resume and full job description
def _document_similarity(resume_text: str, job_description: str) -> float:
    # Convert both texts into embeddings
    embeddings = _embed_texts([resume_text, job_description])

    # Compare embedding 0 (resume) with embedding 1 (job description)
    return _cosine_from_normalized(embeddings[0], embeddings[1])


# Define a function to compare resume and job description chunk by chunk
def _chunk_similarity(resume_text: str, job_description: str) -> float:
    """
    For each JD chunk, find the best matching resume chunk, then average.
    This better reflects whether the resume covers the requirements.
    """
    # Split the resume into smaller parts
    resume_chunks = _split_into_chunks(resume_text)

    # Split the job description into smaller parts
    jd_chunks = _split_into_chunks(job_description)

    # If either side has no chunks, similarity cannot be measured
    if not resume_chunks or not jd_chunks:
        return 0.0

    # Combine all chunks into one list
    # This lets us embed them all in one call
    all_chunks = resume_chunks + jd_chunks

    # Convert all chunks into embeddings
    embeddings = _embed_texts(all_chunks)

    # The first part of embeddings belongs to the resume chunks
    resume_embeddings = embeddings[:len(resume_chunks)]

    # The second part belongs to the JD chunks
    jd_embeddings = embeddings[len(resume_chunks):]

    # This list will store the best match score for each JD chunk
    best_scores = []

    # Check each job-description chunk
    for jd_emb in jd_embeddings:
        # Compare this JD chunk against every resume chunk
        # Since embeddings are normalized, np.dot gives cosine similarities
        scores = np.dot(resume_embeddings, jd_emb)

        # Take the best resume match for this JD chunk
        best_scores.append(float(np.max(scores)))

    # Return the average of all the best match scores
    return float(np.mean(best_scores))


# Define a function to measure keyword overlap
def _keyword_overlap_score(resume_text: str, job_description: str) -> float:
    """
    Measures how many JD keywords appear in the resume.
    """
    # Extract keywords from the resume
    resume_keywords = _extract_keywords(resume_text)

    # Extract keywords from the job description
    jd_keywords = _extract_keywords(job_description)

    # If the job description has no keywords, return 0
    if not jd_keywords:
        return 0.0

    # Find words that exist in both sets
    overlap = resume_keywords.intersection(jd_keywords)

    # Return the percentage of JD keywords found in the resume
    return len(overlap) / len(jd_keywords)


# Define a function to convert a raw score into a more human-friendly 0-100 score
def _calibrate_score(raw_score: float) -> float:
    """
    Map raw score into a more practical 0-100 range.

    Raw score is expected in [0, 1].
    """
    # Make sure raw_score stays between 0 and 1
    raw_score = max(0.0, min(1.0, raw_score))

    # Piecewise mapping means:
    # use different formulas for different score ranges
    # This is done to make the final scores feel more intuitive
    if raw_score < 0.35:
        # Lower scores are compressed a bit
        scaled = raw_score * 100 * 0.6
    elif raw_score < 0.60:
        # Middle range gets stretched differently
        scaled = 21 + (raw_score - 0.35) / 0.25 * 39
    else:
        # High scores are mapped into the 60-100 range
        scaled = 60 + (raw_score - 0.60) / 0.40 * 40

    # Clamp again to 0-100 just in case, then round to 1 decimal place
    return round(max(0.0, min(100.0, scaled)), 1)


# Main function: compare a resume against a job description
def score_resume_vs_job(resume_text: str, job_description: str) -> float:
    """
    Score resume vs. job description on a 0-100 scale.

    Combines:
    - document-level semantic similarity
    - chunk-level requirement coverage
    - keyword overlap
    """
    # Clean both texts first
    resume_text = _clean_text(resume_text)
    job_description = _clean_text(job_description)

    # If either input is empty, return 0
    if not resume_text or not job_description:
        return 0.0

    # Compare full resume to full job description
    doc_score = _document_similarity(resume_text, job_description)

    # Compare chunk-by-chunk coverage
    chunk_score = _chunk_similarity(resume_text, job_description)

    # Compare keyword overlap
    keyword_score = _keyword_overlap_score(resume_text, job_description)

    # Combine the three scores using weights
    # 45% document similarity
    # 35% chunk similarity
    # 20% keyword overlap
    raw_score = (
        0.45 * doc_score +
        0.35 * chunk_score +
        0.20 * keyword_score
    )

    # Convert raw score into a 0-100 score and return it
    return _calibrate_score(raw_score)