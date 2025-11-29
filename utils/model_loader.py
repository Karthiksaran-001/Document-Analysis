import os 
import warnings
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_groq.chat_models import ChatGroq
from dotenv import load_dotenv
from utils.config_loader import load_config
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import DocumentException
warnings.filterwarnings("ignore")


class ModelLoader:
    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config=load_config()
        log.info("Configuration loaded successfully", config_keys=list(self.config.keys()))

    def _validate_env(self):
        """
        Validate necessary environment variables.
        Ensure API keys exist.
        """
        required_vars=["GOOGLE_API_KEY","GROQ_API_KEY"]
        self.api_keys={key:os.getenv(key) for key in required_vars}
        missing = [k for k, v in self.api_keys.items() if not v]
        if missing:
            log.error("Missing environment variables", missing_vars=missing)
            raise DocumentException("Missing environment variables")
        log.info("Environment variables validated", available_keys=[k for k in self.api_keys if self.api_keys[k]]) 

    def load_embeddings(self):
        """
        Load and return the embedding model.
        """
        try:
            log.info("Loading embedding model...")
            model_name = self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(model=model_name)
        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise DocumentException("Failed to load embedding model")
        
    def load_llm(self):
        """
        Load and return the LLM model.
        Load LLM dynamically based on provider in config.
        """
        try:
            llm_block = self.config["llm"]
            log.info("Loading LLM...")
            # Default groq
            provider_key = os.getenv("LLM_PROVIDER", "google")  

            if provider_key not in llm_block:
                log.error("LLM provider not found in config", provider_key=provider_key)
                raise ValueError(f"Provider '{provider_key}' not found in config")

            llm_config = llm_block[provider_key]
            provider = llm_config.get("provider")
            model_name = llm_config.get("model_name")
            temperature = llm_config.get("temperature", 0.2)
            max_tokens = llm_config.get("max_output_tokens", 2048)
            
            log.info("Loading LLM", provider=provider, model=model_name, temperature=temperature, max_tokens=max_tokens)

            if provider == "google":
                llm=ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
                return llm

            elif provider == "groq":
                llm=ChatGroq(
                    model=model_name,
                    api_key=self.api_keys["GROQ_API_KEY"], #type: ignore
                    temperature=temperature,
                )
                return llm
                
            else:
                log.error("Unsupported LLM provider", provider=provider)
                raise ValueError(f"Unsupported LLM provider: {provider}")
            
        except Exception as e:
            log.error("Error loading LLM model", error=str(e))
            raise DocumentException("Failed to load LLM model") 

# if __name__ == "__main__":
#     obj = ModelLoader()
#     embedding = obj.load_embeddings()
#     vector = embedding.embed_query("Supply chain optimization")
#     print(f"Embedding Shape : {len(vector)}")
#     llm = obj.load_llm()
#     message = llm.invoke("Hello,How afre you?")
#     print(f"LLM Message:\n{message}")