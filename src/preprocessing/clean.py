import re


def preprocess(text):
    """Basic cleaning and naive section splitting.
    Returns a dict with keys: abstract, body, references
    """
    if not text:
        return {'abstract':'', 'body':'', 'references':''}
    clean = re.sub(r'\s+', ' ', text).strip()

    abstract = ''
    references = ''
    body = clean

    # Try to extract Abstract
    m = re.search(r'Abstract[:\s]*(.*?)(?=(Introduction|I\.|1\.|Background|Methods))', clean, re.IGNORECASE)
    if m:
        abstract = m.group(1).strip()

    # Try to extract References
    m2 = re.search(r'References[:\s]*(.*)$', clean, re.IGNORECASE)
    if m2:
        references = m2.group(1).strip()
        # remove references from body
        body = clean[:m2.start()].strip()

    return {'abstract': abstract, 'body': body, 'references': references}
