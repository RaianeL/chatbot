from openai import AzureOpenAI
import pypdf
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="ChatBot RAG - Microsoft Foundry", page_icon="🤖", layout="centered"
)

# ==========================================
# 1. INTERFACE E ESTILO (CSS CUSTOMIZADO AVANÇADO)
# ==========================================
st.markdown(
    """
    <style>
    /* Estilização geral do fundo e fontes */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Centralização e limite de largura da área principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 800px;
    }

    /* Estilo do cabeçalho */
    h1 {
        color: #0f172a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    
    p.subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Estilização da barra lateral */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Mensagens do chat customizadas */
    [data-testid="stChatMessage"] {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 2. CONFIGURAÇÃO DA API (MICROSOFT FOUNDRY)
# ==========================================
AZURE_API_KEY = (
    "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
)
AZURE_ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
DEPLOYMENT_NAME = "gpt-4.1-mini"

# Inicialização do cliente Azure OpenAI
client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=AZURE_ENDPOINT,
)

# Cabeçalho da Aplicação
st.title("🤖 Assistente Virtual Inteligente")
st.markdown(
    '<p class="subtitle">Plataforma Acadêmica de Conversação com Suporte a RAG'
    " (PDF/TXT)</p>",
    unsafe_allow_html=True,
)

# ==========================================
# 3. UPLOAD DE ARQUIVOS E SISTEMA RAG
# ==========================================
st.sidebar.header("📁 Base de Conhecimento")
st.sidebar.markdown(
    "Envie um documento para que o bot utilize as informações nas respostas."
)
uploaded_file = st.sidebar.file_uploader(
    "Selecione um arquivo PDF ou TXT", type=["pdf", "txt"]
)

document_text = ""

if uploaded_file is not None:
  file_extension = uploaded_file.name.split(".")[-1].lower()

  if file_extension == "txt":
    document_text = uploaded_file.getvalue().decode("utf-8")
    st.sidebar.success(
        f"✅ TXT carregado: **{uploaded_file.name}**", icon="📄"
    )

  elif file_extension == "pdf":
    try:
      reader = pypdf.PdfReader(uploaded_file)
      extracted_text = []
      for page in reader.pages:
        text = page.extract_text()
        if text:
          extracted_text.append(text)
      document_text = "\n".join(extracted_text)
      st.sidebar.success(
          f"✅ PDF carregado: **{uploaded_file.name}**", icon="📑"
      )
    except Exception as e:
      st.sidebar.error(f"Erro ao processar PDF: {e}")

# ==========================================
# 4. LÓGICA DE CHAT E HISTÓRICO
# ==========================================

# Inicializa o histórico de mensagens no session_state
if "messages" not in st.session_state:
  st.session_state.messages = []

# Exibe o histórico de mensagens na interface com avatares customizados
for message in st.session_state.messages:
  avatar = "👤" if message["role"] == "user" else "🤖"
  with st.chat_message(message["role"], avatar=avatar):
    st.markdown(message["content"])

# Captura a entrada do usuário na caixa de chat inferior
if prompt := st.chat_input("Escreva sua mensagem aqui..."):
  # Adiciona mensagem do usuário ao histórico
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user", avatar="👤"):
    st.
