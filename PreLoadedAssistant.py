import pandas as pd
import openai
import os
import time

# Load API Key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OpenAI API key not found. Make sure it's set correctly.")

# Initialize OpenAI client properly
client = openai.OpenAI(api_key=api_key)

# Pre-created Assistant ID
ASSISTANT_ID = "PLACEHOLDER_FOR_ASSISTANT_ID"  # Replace with your actual Assistant ID

# File paths
input_file = "Job Input File.csv"
output_file = "masterList.csv"

# Load input data
df = pd.read_csv(input_file, encoding="utf-8")


def ask_assistant(thread_id, question):
    """
    Sends a message to the assistant within an existing thread and retrieves the response.
    """
    # Add question message to thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )

    # Run the Assistant on this thread
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID
    )

    # Wait for the Assistant to complete processing
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run_status.status == "completed":
            break
        time.sleep(1)  # Wait before checking again

    # Retrieve messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)

    # Extract the latest response
    response_text = messages.data[0].content[0].text.value.strip()
    return response_text


def get_structured_job_posting(position_title, position_summary, feedback):
    """
    Calls OpenAI Assistant API in multiple steps:
    1. Provides job details
    2. Asks for Short Summary
    3. Asks for Day in the Life
    4. Asks for Ideal Candidate traits
    """

    # Create a new thread for the Assistant
    thread = client.beta.threads.create()

    # Step 1: Provide Job Details
    job_details = f"""
    Here is a job description for the role of {position_title}:

    {position_summary}

    """

    if pd.notna(feedback):
        job_details += f"\nAdditional Feedback:\n{feedback}"

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=job_details
    )

    print(f"Sent job details for {position_title} to Assistant...")

    # Step 2a: Ask for First Short Summary
    short_summary_1 = ask_assistant(thread.id, "Please provide a short summary of the job description in one engaging sentence.")

    # Step 2b: Ask for Second Short Summary
    short_summary_2 = ask_assistant(thread.id, "Please provide a different short summary of the job description in one engaging sentence.")

    # Step 3: Ask for Day in the Life
    day_in_life = ask_assistant(thread.id, "Please provide the job overview.")

    # Step 4: Ask for Ideal Candidate Traits
    ideal_candidate = ask_assistant(thread.id, "List key skills, soft skills, or personality traits needed for this role, with each trait being six words or fewer, separated by |.")

    return short_summary_1, short_summary_2, day_in_life, ideal_candidate


# Process each job posting **one at a time** and append immediately
for _, row in df.iterrows():
    hris_id = row["HRIS ID"]
    position_title = row["Position Title"]
    position_summary = row["Position Summary"]
    feedback = row["Feedback"]

    # Generate structured job posting via Assistant
    short_summary_1, short_summary_2, day_in_life, ideal_candidate = get_structured_job_posting(position_title, position_summary, feedback)
    # Combine short summaries with a pipe
    short_summary = f"{short_summary_1} | {short_summary_2}"
    # Convert the single row into a DataFrame for appending
    new_df = pd.DataFrame([[hris_id, position_title, short_summary, day_in_life, ideal_candidate]],
                          columns=["HRIS ID", "Position Title", "Short Summary", "Day in the Life", "Ideal Candidate"])

    # Append the new row immediately
    new_df.to_csv(output_file, mode='a', index=False, header=not os.path.exists(output_file))

    print(f"✅ Appended processed job: {position_title} to {output_file}")

print("✅ All job postings processed and appended successfully!")
