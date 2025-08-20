import fitz  # PyMuPDF

def extract_text_from_pdf(filepath):
    text = ""
    pdf = fitz.open(filepath)
    for page in pdf:
        text += page.get_text()
    pdf.close()
    with open("study_guide.txt", "w", encoding="utf-8") as f:
        f.write(text)
    return text

if __name__ == "__main__":
    extract_text_from_pdf("C:\\Users\\Rupsa\\Desktop\\ai chatbot stidy\\pdf\\phy.pdf")
