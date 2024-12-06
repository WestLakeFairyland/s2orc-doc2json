# doc2json for RAG

This is a fork of the **doc2json** project to work with our system. It provides a **FastAPI** that accepts a PDF and returns the parsed content in a structured JSON format. The files are stored in the `test/work` directory.

## Requirements

- **Grobid**: This system relies on Grobid for processing PDFs into structured data.
  - You need to [run Grobid](https://grobid.readthedocs.io/en/latest/Run-Grobid/) in Docker. It has been tested in **Windows WSL**.
  - To run Grobid, use the following command:

    ```bash
    sudo docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.1
    ```

  - Grobid should only take a few seconds to process a PDF.

## Behavior

- **PDF to JSON**: The API takes a PDF file, processes it through Grobid, and returns a JSON with the following details:
  - **Metadata**: Includes general paper information like title, authors, year, etc.
  - **Body text**: Main content of the paper, which is organized by sections and paragraphs.
  - **References**: Citations from the paper, which are stored separately in the JSON file. Citations include IDs that are linked in the main text.
  - **Figures and Tables**: Captions for figures and tables are included in the `ref_entries`.

### Limitations and Observations

- **Paragraph Recognition**:
  - Grobid does a fairly good job of connecting rows, though it's not 100% accurate with paragraphs.
  - It sometimes misdivides paragraphs or adds additional paragraphs in sections like the abstract.
  - There are cases where page breaks disrupt paragraph detection, although some of these are fixed automatically by Grobid.
  
- **Section Titles**:
  - Each section of the body text includes a **section** field, which contains the section title.
  - In some cases, the section title is missing or only includes a subtitle (e.g., "SME attribution visualization of Aqueous solubility", instead of "Methods", "Results").
  
- **Equations**:
  - The detection and extraction of equations is not perfect at this stage. More refinement is needed for better handling of mathematical content.

## TODO

- [ ] **Setup the API**: Ensure that the FastAPI service is correctly configured to handle PDF uploads and Grobid processing.


# The original README: Convert scientific papers to S2ORC JSON

This project is a part of [S2ORC](https://github.com/allenai/s2orc). For S2ORC, we convert PDFs to JSON using Grobid and a custom TEI.XML to JSON parser. That TEI.XML to JSON parser (`grobid2json`) is made available here. We additionally process LaTeX dumps from arXiv. That parser (`tex2json`) is also made available here.

The S2ORC github page includes a JSON schema, but it may be easier to understand that schema based on the python classes in `doc2json/s2orc.py`.

This custom JSON schema is also used for the [CORD-19](https://github.com/allenai/cord19) project, so those who have interacted with CORD-19 may find this format familiar.

Possible future components (no promises):
- Linking bibliography entries (bibliography consolidation) to papers in S2ORC

## Setup your environment

NOTE: Conda is shown but any other python env manager should be fine

Go [here](https://docs.conda.io/en/latest/miniconda.html) to install the latest version of miniconda.

Then, create an environment:

```console
conda create -n doc2json python=3.8 pytest
conda activate doc2json
pip install -r requirements.txt
python setup.py develop
```

## PDF Processing

The current `grobid2json` tool uses Grobid to first process each PDF into XML, then extracts paper components from the XML.

### Install Grobid
> Build from the [latest Grobid repo](https://github.com/kermitt2/grobid) or use [Grobid docker](https://grobid.readthedocs.io/en/latest/Grobid-docker/) if you have problems on installing Gorbid.


You will need to have Java (tested with Java 11) installed on your machine. Then, you can install your own version of Grobid and get it running, or you can run the following script:

```console
bash scripts/setup_grobid.sh
```

Note: before running this script, make sure the paths match your installation path. Else it will fail to install.

This will setup Grobid, currently hard-coded as version 0.7.3. Then run:

```console
bash scripts/run_grobid.sh
```

to start the Grobid server. Don't worry if it gets stuck at 87%; this is normal and means Grobid is ready to process PDFs.

The expected port for the Grobid service is 8070, but you can change this as well. Make sure to edit the port in both the Grobid config file as well as `grobid/grobid_client.py`.

### Process a PDF

There are a couple of test PDFs in `tests/input/` if you'd like to try with that.

For example, you can try:

```console
python doc2json/grobid2json/process_pdf.py -i tests/pdf/N18-3011.pdf -t temp_dir/ -o output_dir/
```

This will generate a JSON file in the specified `output_dir`. If unspecified, the file will be in the `output/` directory from your path.

## LaTeX Processing

If you want to process LaTeX, in addition to installing Grobid, you also need to install the following libraries:

- [latexpand](https://ctan.org/pkg/latexpand?lang=en) (`apt install texlive-extra-utils`)
- [tralics](http://www-sop.inria.fr/marelle/tralics/) (`apt install tralics`)

To process LaTeX, all files must be in a zip file, similar to the `*.gz` files you can download from arXiv. 

Like PDF, first start Grobid using the `run_grobid.sh` script. Then, try to process one of the test files available under `tests/latex/`. For example, you can try:

```console
python doc2json/tex2json/process_tex.py -i test/latex/1911.02782.gz -t temp_dir/ -o output_dir/
```

Again, this will produce a JSON file in the specified `output_dir`.

Why do you need Grobid? We use the Grobid citation and author APIs to convert raw strings into structured forms.

## PMC JATS XML Processing

To process JATS XML, try:

```console
python doc2json/jats2json/process_jats.py -i test/jats/PMC5828200.nxml -o output_dir/
```

This will create a JSON file with the same paper id in the specified output directory.

## Loading a S2ORC JSON file

The format of S2ORC releases have drifted over time. Use the `load_s2orc` function in `doc2json/s2orc.py` to try and load historic and currect S2ORC JSON.

## Run a Flask app and process documents through a web service

To process PDFs, you will first need to start Grobid (defaults to port 8070). If you are processing LaTeX, no need for this step.

```console
bash scripts/run_grobid.sh
```

Then, start the Flask app (defaults to port 8080).

```console
python doc2json/flask/app.py
```

Go to [localhost:8080](localhost:8080) to upload and process papers.

Or alternatively, you can do things like:

```console
curl localhost:8080/ -F file=@tests/pdf/N18-3011.pdf
```

## Citation

If you use this utility in your research, please cite:

```
@inproceedings{lo-wang-2020-s2orc,
    title = "{S}2{ORC}: The Semantic Scholar Open Research Corpus",
    author = "Lo, Kyle  and Wang, Lucy Lu  and Neumann, Mark  and Kinney, Rodney  and Weld, Daniel",
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.acl-main.447",
    doi = "10.18653/v1/2020.acl-main.447",
    pages = "4969--4983"
}
```

## Contact

Contributions are welcome. Note the embarassingly poor test coverage. Also, please note this pipeline is not perfect. It will miss text or make errors on most PDFs. The current PDF to JSON step uses Grobid; we may replace this with a different model in the future.

Issues: contact `lucyw@allenai.org` or `kylel@allenai.org`

