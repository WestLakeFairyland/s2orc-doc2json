import os
import json
from doc2json.grobid2json.process_pdf import process_pdf_file


def process_pdf_to_json(pdf_path, output_dir):
    """
    Convert a PDF to JSON and save it in the specified directory.
    Args:
        pdf_path (str): Path to the input PDF file.
        output_dir (str): Path to the directory where the output JSON file will be saved.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate the JSON output path directly in the output directory
    json_output_path = os.path.join(output_dir, os.path.basename(pdf_path).replace(".pdf", ".json"))

    try:
        # Call the Grobid processing function, using the same directory for temp and output
        process_pdf_file(input_file=pdf_path, output_dir=output_dir, temp_dir=output_dir)
        print(f"JSON output saved at: {json_output_path}")
    except Exception as e:
        print(f"Error processing PDF: {e}")


def extract_main_text(json_data):
    """
    Extracts the main text from the JSON.
    Args:
        json_data (dict): The parsed JSON data.
    Returns:
        str: The main body text in markdown format.
    """
    pdf_parse_content = json_data.get('pdf_parse', {})
    body_text = pdf_parse_content.get('body_text', [])

    # Join the text entries with newlines (markdown format), separating each "text" entry
    main_text = "\n\n".join(text_entry['text'] for text_entry in body_text if 'text' in text_entry)
    return main_text


def extract_metadata(json_data):
    """
    Extract title, authors, and abstract from the JSON.
    Args:
        json_data (dict): The parsed JSON data.
    Returns:
        dict: A dictionary containing the title, authors, and abstract.
    """
    # Extract title, authors, and abstract from the JSON
    title = json_data.get('title', 'No title available')
    authors = json_data.get('authors', 'No authors available')
    abstract = json_data.get('abstract', 'No abstract available')

    # Format the authors (assuming it's a list of dictionaries)
    formatted_authors = ', '.join([f"{author['first']} {author['last']}" for author in authors])

    return {
        "Title": title,
        "Authors": formatted_authors,
        "Abstract": abstract
    }


# %% example usage
if __name__ == "__main__":
    output_dir = "tests/work"
    # Example PDF path
    # prefix = '2023-Chemistry-intuitive explanation of graph neural networks for molecular property prediction with substructure masking'
    prefix = 'dudev-lim-2013-competition-among-metal-ions-for-protein-binding-sites-determinants-of-metal-ion-selectivity-in-proteins'

    pdf_path = fr"{output_dir}/{prefix}.pdf"

    # Process the PDF to JSON
    process_pdf_to_json(pdf_path, output_dir)

    # Load the JSON data
    json_path = fr"{output_dir}/{prefix}.json"
    with open(json_path, 'r') as file:
        json_data = json.load(file)

    # Extract metadata (title, authors, abstract)
    extracted_info = extract_metadata(json_data)

    # Write the main text to a markdown file
    main_text = extract_main_text(json_data)
    markdown_output_path = fr"{output_dir}/{prefix}_main_text.md"

    with open(markdown_output_path, 'w', encoding='utf-8') as markdown_file:
        markdown_file.write(main_text)

    print(f"Main text has been written to: {markdown_output_path}")
