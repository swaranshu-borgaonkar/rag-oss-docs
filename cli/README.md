# cli/

Command-line version of the pipeline.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 build_and_query.py
```

This builds the Chroma index from `docs/` and runs 4 example queries,
printing the top-matching chunks to the terminal. See the top-level
[repo README](../README.md) for pipeline details and design notes.
