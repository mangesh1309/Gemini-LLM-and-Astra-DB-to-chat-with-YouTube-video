# YouChat-AI


1. **User-Friendly User Interface:**
![Screenshot 2024-07-25 221530](https://github.com/user-attachments/assets/ef15bc8b-e539-45f5-9f24-5424a06dc5ef)

2. **Input Video Link: Video title and thumbnail image extracted using python**
![Screenshot 2024-07-25 221626](https://github.com/user-attachments/assets/35051cad-1d27-4d5e-b170-0665c8963402)

3. **Output: The query knowledge present in the provided video**
![Screenshot 2024-07-25 222116](https://github.com/user-attachments/assets/85d164ac-9b2b-47cf-8d52-6581959088ba)

4. **Output: The query knowledge not present in the provided video**
![Screenshot 2024-07-25 221918](https://github.com/user-attachments/assets/8e550118-ab14-4e84-97fb-a1285da65808)

## Overview

YouChat AI is a Streamlit application designed to process YouTube video transcripts and answer user queries based on the video's content. It leverages various technologies, including the YouTube Transcript API, LangChain, Google Generative AI, and Astra DB, to create a conversational agent capable of responding to user questions about video content.

## Features

- **Transcript Extraction:** Extracts video transcripts from YouTube.
- **Text Chunking:** Splits large transcripts into manageable chunks.
- **Document Storage:** Stores processed text chunks in Astra DB for retrieval.
- **Conversational AI:** Uses a generative AI model to answer user queries based on video content.
- **Streamlit UI:** Provides an interactive user interface for processing videos and querying content.
- **Document Management:** Includes functionality for deleting stored documents.

## Prerequisites

- Python 3.7 or higher
- Required Python packages (listed in requirements.txt)
- Google API key
- Astra DB credentials

## Installation

1. **Clone this repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install the required Python packages:**

    ```bash
    pip install -r requirements.txt
    ```

3. **Set up environment variables** by creating a `.env` file in the root directory with the following content:

    ```env
    GOOGLE_API_KEY=<your-google-api-key>
    ASTRA_DB_APPLICATION_TOKEN=<your-astra-db-application-token>
    ASTRA_DB_API_ENDPOINT=<your-astra-db-api-endpoint>
    COLLECTION_NAME=<your-collection-name>
    DATABASE_ID=<your-database-id>
    ASTRA_DB_REGION=<your-astra-db-region>
    ASTRA_DB_NAMESPACE_ID=<your-astra-db-namespace-id>
    ```

## Usage

1. **Start the Streamlit Application:**

    ```bash
    streamlit run <script-name>.py
    ```

2. **In the Streamlit UI:**
   - **Enter YouTube Video URL:** Input the URL of the YouTube video you want to process.
   - **Process Video:** Click the "Process Video" button to extract and process the video's transcript.
   - **Enter Your Query:** Input a query related to the video content.
   - **Get Response:** Click the "Get Response" button to get answers based on the video's content.

3. **Manage Documents:**
   - **Quit or Change Video:** Click the button to delete all documents related to the current video from Astra DB and clear the session state.
