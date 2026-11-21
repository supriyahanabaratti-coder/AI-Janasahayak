
def extract_eligibility_information(document_text):
    keywords = [
        "eligibility",
        "eligible",
        "age",
        "income",
        "qualification",
        "पात्रता",
        "ಅರ್ಹತೆ"
    ]

    matching_lines = []

    for line in document_text.splitlines():
        if any(word in line.lower() for word in keywords):
            matching_lines.append(line.strip())

    return matching_lines
