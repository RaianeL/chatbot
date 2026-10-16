from openai import AzureOpenAI
import pypdf
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="ChatBot RAG - Microsoft Foundry", page_icon="🤖", layout="wide"
)

# ==========================================
# 1. INTERFACE E ESTILO (CSS CUSTOMIZADO)
# ==========================================
st.markdown(
    """
    <style>
    /* Borda estilizada e elegante ao redor da área principal do app */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        background-color: #ffffff;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    /* Estilização do título */
    h1 {
        color: #1e293b;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Estilização da barra lateral */
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
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

# Inicialização do cliente Azure OpenAI (compatível com a plataforma Microsoft Foundry)
client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version="2024-02-01",
    azure_endpoint=AZURE_ENDPOINT,
)

# Cabeçalho da Aplicação
st.title("🤖 ChatBot Inteligente com RAG")
st.markdown(
    "Bem-vindo! Utilize o chat abaixo para conversar ou envie um documento"
    " (**PDF** ou **TXT**) na barra lateral para realizar perguntas baseadas no"
    " conteúdo dele."
)

# ==========================================
# 3. UPLOAD DE ARQUIVOS E SISTEMA RAG
# ==========================================
st.sidebar.header("📁 Base de Conhecimento (RAG)")
uploaded_file = st.sidebar.file_uploader(
    "Envie um arquivo de texto ou PDF", type=["pdf", "txt"]
)

document_text = ""

if uploaded_file is not None:
  file_extension = uploaded_file.name.split(".")[-1].lower()

  if file_extension == "txt":
    # Leitura de arquivo TXT
    document_text = uploaded_file.getvalue().decode("utf-8")
    st.sidebar.success(
        f"Arquivo TXT **{uploaded_file.name}** carregado com sucesso!"
    )

  elif file_extension == "pdf":
    # Leitura de arquivo PDF usando pypdf
    try:
      reader = pypdf.PdfReader(uploaded_file)
      extracted_text = []
      for page in reader.pages:
        text = page.extract_text()
        if text:
          extracted_text.append(text)
      document_text = "\n".join(extracted_text)
      st.sidebar.success(
          f"Arquivo PDF **{uploaded_file.name}** carregado com sucesso!"
      )
    except Exception as e:
      st.sidebar.error(f"Erro ao processar o arquivo PDF: {e}")

# ==========================================
# 4. LÓGICA DE CHAT E HISTÓRICO
# ==========================================

# Inicializa o histórico de mensagens no session_state
if "messages" not in st.session_state:
  st.session_state.messages = []

# Exibe o histórico de mensagens na interface
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# Captura a entrada do usuário
if prompt := st.chat_input("Digite sua dúvida aqui..."):
  # Adiciona mensagem do usuário ao histórico
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Monta o prompt do sistema integrando o RAG (se houver arquivo carregado)
  if document_text.strip():
    system_prompt = (
        "Você é um assistente RAG especializado. Responda à pergunta do usuário"
        " baseando-se estritamente no seguinte contexto extraído do documento"
        " fornecido. Se a resposta não estiver clara no contexto, informe"
        " educadamente que o documento não contém essa informação.\n\n---"
        f" CONTEXTO ---\n{document_text}\n--------------"
    )
  else:
    system_prompt = (
        "Você é um assistente virtual prestativo, inteligente e profissional."
    )

  # Constrói a lista de mensagens para enviar à API
  messages_payload = [{"role": "system", "content": system_prompt}]
  for msg in st.session_state.messages:
    messages_payload.append({"role": msg["role"], "content": msg["content"]})

  # Gera a resposta do assistente usando a API do Microsoft Foundry
  with st.chat_message("assistant"):
    message_placeholder = st.empty()
    message_placeholder.markdown("Pensando...")
    try:
      response = client.chat.completions.create(
          model=DEPLOYMENT_NAME, messages=messages_payload, temperature=0.3
      )
      assistant_response = response.choices[0].message.content
      message_placeholder.markdown(assistant_response)
    except Exception as e:
      assistant_response = (
          f"❌ Ocorreu um erro ao se comunicar com o modelo: {e}"
      )
      message_placeholder.markdown(assistant_response)

  # Adiciona a resposta do assistente ao histórico
  st.session_state.messages.append(
      {"role": "assistant", "content": assistant_response}
  )
