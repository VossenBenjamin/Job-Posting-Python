# Job-Posting-Python

## Repository Overview
This repo contains a single Python script, `PreLoadedAssistant.py`, which automates job posting summarization using the OpenAI API. The script reads an input CSV and appends structured summaries to `masterList.csv`.

## Main Script
`PreLoadedAssistant.py` performs these key tasks:

1. **Environment Setup** – Loads the OpenAI API key from `OPENAI_API_KEY`, initializes the client, and reads `Job Input File.csv`.
2. **`ask_assistant` Function** – Sends a question to the assistant in a thread and waits for the reply.
3. **`get_structured_job_posting` Function** – Creates a thread, uploads job details, requests two short summaries, a "day in the life," and ideal candidate traits.
4. **Processing Loop** – Iterates over the input CSV. For each row it gathers responses from the assistant and immediately appends them to `masterList.csv`.

The script relies on a pre-created `ASSISTANT_ID` and requires network access. Existing rows in the output CSV are preserved between runs.

## Next Steps
Consider improving error handling, parameterizing the input/output file paths, and adding unit tests or documentation for setup.
