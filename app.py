from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_astradb import AstraDBVectorStore

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain.schema import Document
import streamlit as st

import yt_dlp

from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vstore = AstraDBVectorStore(
    collection_name=os.getenv("COLLECTION_NAME"),
    embedding=embedding,
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
)
print("Astra vector store configured")


def get_transcript(video_link):
    try:
        # Extract video ID from the URL
        video_id = video_link.split("v=")
        if len(video_id) != 2:
            raise ValueError("No Transcript Found for this Video")
        video_id = video_id[1]

        print(f"Video ID: {video_id}")

        # Get transcript for the video
        text = YouTubeTranscriptApi.get_transcript(video_id)

        # Concatenate all transcript segments
        result = " ".join([i["text"] for i in text])

        return result

    except Exception as e:
        print(f"An error occurred: {e}")


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


def get_documents(text_chunks):
    documents = [Document(page_content=chunk) for chunk in text_chunks]
    return documents


def insert_documents(documents):
    inserted_ids = vstore.add_documents(documents)
    print(f"\nInserted {len(inserted_ids)} documents.")
    return inserted_ids


def get_conversational_chain():
    retriever = vstore.as_retriever(search_kwargs={"k": 3})

    PRODUCT_BOT_TEMPLATE = """
    Your are an expert in analysing the transcript of the YouTube video.
    You are supposed to provide the responses to the user queries from the provided video only.
    If the response knowledge is not present in the video, just say that the video does not provide any knowledge about your query. Don't give any outside results.
    Answer in detail as much as you can with context to the video only.
    While responding, please make sure the response is relevant to the user query.
    CONTEXT:
    {context}

    QUESTION: {question}

    YOUR ANSWER:

    """

    prompt = ChatPromptTemplate.from_template(PRODUCT_BOT_TEMPLATE)

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def get_response(chain, query):
    resp = chain.invoke(query)
    return resp


def get_video_info(url):
    if not url:
        return "No title found", "No thumbnail found"

    ydl_opts = {
        'quiet': True,  # Suppress output
        'skip_download': True,  # Skip downloading video
        'force_generic_extractor': True,  # Use a generic extractor
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'No title found')
            thumbnail_url = info_dict.get('thumbnail', 'No thumbnail found')
            return title, thumbnail_url
    except yt_dlp.utils.DownloadError as e:
        st.error(f"Error extracting video information: {e}")
        return "No title found", "No thumbnail found"


if "idsx" not in st.session_state:
    st.session_state.idsx = []

if "video_link" not in st.session_state:
    st.session_state.video_link = ""

if "query" not in st.session_state:
    st.session_state.query = ""

# Streamlit UI
st.set_page_config(page_title="YouChat AI", layout="wide", page_icon="🧑‍💻")

st.title("YouChat AI")
st.sidebar.header("Video Details")

# STEP 1: Get YoutTube Video URL
video_link = st.sidebar.text_input("Enter YouTube Video URL", st.session_state.video_link)
title, thumbnail = get_video_info(video_link)

if st.sidebar.button("Process Video"):
    if video_link:
        with st.spinner('Processing video...'):
            # STEP 2: Extract Video Transcript
            text = get_transcript(video_link)

            if text:
                # STEP 3: Divide Long Transcript into Smaller Chunks
                chunks = get_text_chunks(text)
                documents = get_documents(chunks)
                st.sidebar.success("Video processing done. You can now start querying.")
                st.sidebar.image(thumbnail)
                st.sidebar.subheader(title)

                # STEP 4: Convert Chunks into Embeddings and Push onto Vector Database(Astra DB)
                inserted_ids = insert_documents(documents)
                st.session_state.idsx.extend(inserted_ids)
                st.session_state.video_link = video_link  # Update session state with the video link

            else:
                st.sidebar.error("Sorry! Could not process the video")

# STEP 5: User Query Input
query = st.text_input("Enter your query", st.session_state.query)

if st.button("Get Response"):
    if query:
        st.sidebar.success("Video processing done. You can now start querying.")
        st.sidebar.image(thumbnail)
        st.sidebar.subheader(title)
        with st.spinner('Getting response...'):
            # STEP 6: Load Generative Model and Query for Response
            chain = get_conversational_chain()
            ans = get_response(chain, query)
            st.write("### Response")
            st.write(ans)
            st.session_state.query = query  # Update session state with the query


import requests


def delete_document(database_id, region, namespace_id, collection_id, document_id, token):
    """Deletes a document from Astra DB

    Args:
        database_id: UUID of your database
        region: Cloud region where your database lives
        namespace_id: Namespace name
        collection_id: Name of the document collection
        document_id: ID of the document to delete
        token: Astra DB application token
    """

    url = f"https://{database_id}-{region}.apps.astra.datastax.com/api/rest/v2/namespaces/{namespace_id}/collections/{collection_id}/{document_id}"
    headers = {
        "X-Cassandra-Token": token
    }

    response = requests.delete(url, headers=headers)

    if response.status_code == 204:
        print("Document deleted successfully")
    else:
        print(f"Error deleting document: {response.text}")


if st.button("Quit or Change Video", type="primary"):
    for doc_id in st.session_state.idsx:
        try:
            delete_document(
                database_id=os.getenv("DATABASE_ID"),
                region=os.getenv("ASTRA_DB_REGION"),
                namespace_id=os.getenv("ASTRA_DB_NAMESPACE_ID"),
                collection_id=os.getenv("COLLECTION_NAME"),
                document_id=doc_id,
                token=os.getenv("ASTRA_DB_APPLICATION_TOKEN")
            )
            st.sidebar.success(f"Document with ID {doc_id} deleted successfully.")
        except Exception as e:
            st.sidebar.error(f"Error deleting document with ID {doc_id}: {e}")

    st.session_state.idsx.clear()
    st.session_state.video_link = ""  # Clear the video link
    st.session_state.query = ""  # Clear the query

    # Force a rerun with an empty state
    st.experimental_rerun()
