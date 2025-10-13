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

        if not os.path.exists(DB_FAISS_PATH):
            raise FileNotFoundError(f"CRITICAL ERROR: The FAISS vector store was not found at path: {DB_FAISS_PATH}. Please ensure it is included in the Docker image.")
        
        print(f"Loading existing vector store from: {DB_FAISS_PATH}")
        # Load the vector store from disk
        self.vector_store = FAISS.load_local(
            DB_FAISS_PATH, 
            self.embeddings, 
            allow_dangerous_deserialization=True 
        )

    def chunk_documents(self, documents: list):
        print("\nSplitting translated documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        all_chunks = text_splitter.split_documents(documents)
        print(f"Total document chunks created: {len(all_chunks)}")

        return all_chunks
    
    def prepare_documents(self, pdf_paths: list, translate_documents: bool = False):
        llm_translator = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001", 
            temperature=0, 
            google_api_key=API_KEY
        )

        processed_documents = []

        for path in pdf_paths:
            print(f"\nProcessing document: {path}")
            loader = PyPDFLoader(path)
            documents = loader.load()

            if translate_documents:
                print(f"Translating {len(documents)} pages via Gemini API. This may take a few minutes...")
                for i, doc in enumerate(documents):
                    original_text = doc.page_content
                    prompt_text = f"Translate the following Norwegian text to English. Do not add any commentary, preamble, or notes. Output only the translated English text.\n\nNORWEGIAN TEXT:\n{original_text}"
                    translated_text = llm_translator.invoke(prompt_text).content         
                    doc.page_content = translated_text
                    print(f"  - Translated page {i + 1}/{len(documents)}")
                
                processed_documents.extend(documents)
            else:
                processed_documents.extend(documents)

        return processed_documents

    def build_vector_store(self, document_list):
        document_list = self.prepare_documents(document_list) 
        chunks = self.chunk_documents(document_list)

        print("Creating embeddings with Gemini and storing in FAISS vector store...")
        vector_store = FAISS.from_documents(chunks, self.embeddings)

        print(f"Saving vector store to disk at: {DB_FAISS_PATH}")
        vector_store.save_local(DB_FAISS_PATH)

        return vector_store

    def process_claim(self, claim):
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 7})

        prompt_template = """
        Du er en grunding fakta-sjekker. Din oppgave er å verifisere følgende påstander kun ved å basere deg på informasjonen som blir gitt tilgjengelig for deg. Denne informasjonen er hentet fra
        de ulike politiske partiene sine partiprogrammer.

        Analyser innholdet i påstanden og avgjør om påstanden er SANN PÅSTAND, FALSK PÅSTAND, eller IKKE MULIG Å AVGJØRE

        Hvis det er gitt flere påstander må disse analyseres hver for seg. 

        Svar med et tydelig svar per påstand (SANN PÅSTAND, FALSK PÅSTAND eller IKKE MULIG Å AVGJØRE) etterfulgt av en forklaring i sammenheng av den tilgjengelige informasjonen du har. Ikke bruk noen som helst kunnskap utenfor det som er hentet
        fra de politiske programmene.

        KONTEKST:
        {context}

        PÅSTAND:
        {input}

        SVAR:
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