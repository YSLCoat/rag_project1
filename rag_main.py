import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


API_KEY = os.getenv("GOOGLE_API_KEY")
DB_FAISS_PATH = "faiss_index"


class RagPipeline():
    def __init__(self, name, vector_store=None):
        self.name = name
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001", 
            temperature=0, 
            google_api_key=API_KEY
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", 
            google_api_key=API_KEY
        )

        if os.path.exists(DB_FAISS_PATH):
            print(f"Loading existing vector store from: {DB_FAISS_PATH}")
            # Load the vector store from disk
            # The `allow_dangerous_deserialization` flag is required for loading FAISS indexes.
            # This is safe here because we are the ones who created the file.
            vector_store = FAISS.load_local(
                DB_FAISS_PATH, 
                self.embeddings, 
                allow_dangerous_deserialization=True 
            )
        if vector_store is None:
            self.vector_store = self.build_vector_store()
        else: 
            self.vector_store=vector_store

    def chunk_documents(documents: list):
        print("\nSplitting translated documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        all_chunks = text_splitter.split_documents(documents)
        print(f"Total document chunks created: {len(all_chunks)}")

        return all_chunks
    
    def translate_documents(pdf_paths: list):
        llm_translator = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001", 
            temperature=0, 
            google_api_key=API_KEY
        )

        translated_documents = []

        for path in pdf_paths:
            print(f"\nProcessing document: {path}")
            loader = PyPDFLoader(path)
            documents = loader.load()
            print(f"Translating {len(documents)} pages via Gemini API. This may take a few minutes...")
            for i, doc in enumerate(documents):
                original_text = doc.page_content
                prompt_text = f"Translate the following Norwegian text to English. Do not add any commentary, preamble, or notes. Output only the translated English text.\n\nNORWEGIAN TEXT:\n{original_text}"
                translated_text = llm_translator.invoke(prompt_text).content         
                doc.page_content = translated_text
                print(f"  - Translated page {i + 1}/{len(documents)}")
            
            translated_documents.extend(documents)

        return translated_documents

    def build_vector_store(self, document_list):
        document_list = self.translate_documents(document_list)
        chunks = self.chunk_documents(document_list)

        print("Creating embeddings with Gemini and storing in FAISS vector store...")
        vector_store = FAISS.from_documents(chunks, self.embeddings)

        return vector_store

    def process_claim(self, claim):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 7})

        prompt_template = """
        You are a meticulous fact-checker. Your task is to verify the following claim based *only* on the provided context from translated political party policies.

        Analyze the context and determine if the claim is TRUE, FALSE, or UNVERIFIABLE.

        Provide a clear, one-word answer (TRUE, FALSE, or UNVERIFIABLE) followed by a brief, neutral explanation citing the relevant text from the context. Do not use any outside knowledge.

        CONTEXT:
        {context}

        CLAIM:
        {input}

        ANSWER:
        """

        prompt = ChatPromptTemplate.from_template(prompt_template)

        rag_chain = (
            {"context": retriever, "input": RunnablePassthrough()}
            | prompt
            | self.llm
        )

        print("\n--- Gemini-Powered Fact-Checking Application Ready ---")
        print(f"\nChecking Claim: '{claim}'")

        response = rag_chain.invoke(claim)
        return response.content