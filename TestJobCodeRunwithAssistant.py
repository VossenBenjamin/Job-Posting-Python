Python 3.13.1 (tags/v3.13.1:0671451, Dec  3 2024, 19:06:28) [MSC v.1942 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> import pandas as pd
... import openai
... import os
... import time
... 
... # Load API Key from the environment variable
... api_key = os.getenv("OPENAI_API_KEY")
... 
... if not api_key:
...     raise ValueError("OpenAI API key not found. Make sure it's set correctly.")
... 
... # Initialize OpenAI client properly
... client = openai.OpenAI(api_key=api_key)
... 
... # Load CSV File
... df = pd.read_csv("Job_Posting_Test.csv")
... 
... # Check if 'SUMMARY' column exists
... if 'SUMMARY' not in df.columns:
...     raise ValueError("Column 'SUMMARY' not found in the CSV file.")
... 
... # Step 1: Create an Assistant with all instructions (Only needs to be done once)
... assistant = client.beta.assistants.create(
...     name="Job Posting Assistant",
...     instructions=(
...         "You are an AI assistant that processes job descriptions and extracts structured information. "
...         "For each job description provided, generate the following:\n\n"
...         "1. **New Summary:** Summarize the following job description into a single, concise sentence that captures the core responsibilities and purpose of the role.\n"
...         "2. **Qualifications - Required:** Extract and list the **minimum qualifications** required for this job, including mandatory education, certifications, work experience, and technical skills. Format it as a clear and concise bulleted list.\n"
...         "3. **Qualifications - Preferred:** Extract and list the **preferred qualifications** for this job, such as additional "
        "education, certifications, experience, and desirable skills that are not required "
        "but would be beneficial. Format the response as a concise bulleted list.\n"
...         "4. **Ideal Candidate:** Based on the job summary, describe the ideal candidate for this position. "
        "Include their key traits, work style, strengths, and how they would contribute "
        "to the success of the role. Write it in 2-3 well-structured sentences.\n\n"
        "When a job description is provided, return all four sections in a structured format."
    ),
    model="gpt-4-turbo"
)

assistant_id = assistant.id
print(f"Assistant ID: {assistant_id}")

# Step 2: Create a Thread for the Job Postings Batch
thread = client.beta.threads.create()
thread_id = thread.id
print(f"Thread ID: {thread_id}")

# Function to send job descriptions to the Assistant
def get_assistant_response(text):
    """Sends a job summary to the assistant and retrieves a structured response."""
    
    # Send message to the Assistant
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=text  # Only sending job description, since instructions are preloaded
    )

    # Run the assistant
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    # Wait for the response to be processed
    while True:
        run_status = client.beta.threads.runs.retrieve(run.id)
        if run_status.status == "completed":
            break
        time.sleep(1)  # Polling for completion

    # Fetch messages from the thread
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    
    # Return the latest assistant response
    return messages.data[0].content[0].text.value.strip()

# Process job descriptions and store structured results
new_columns = ["New Summary", "Qualifications - Required", "Qualifications - Preferred", "Ideal Candidate"]
df[new_columns] = df["SUMMARY"].apply(lambda text: pd.Series(get_assistant_response(str(text)).split("\n\n")))

# Save the results to a new CSV file
output_file = "Job_Postings.csv"
df.to_csv(output_file, index=False)

print(f"Processed job postings saved to {output_file}")
