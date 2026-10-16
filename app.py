from openai import AzureOpenAI
import pypdf
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="ChatBot RAG - Microsoft Foundry", page_icon="🤖", layout="centered"
)

# ==========================================
# 1. INTERFACE E ESTILO (CSS CUSTOMIZADO)
# ==========================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 800px;
    }
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
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
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

if "messages" not in st.session_state:
  st.session_state.messages = []

for message in st.session_state.messages:
  avatar = "👤" if message["role"] == "user" else "🤖"
  with st.chat_message(message["role"], avatar=avatar):
    st.markdown(message["content"])

if prompt := st.chat_input("Escreva sua mensagem aqui..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user", avatar="👤"):
    st.markdown(prompt)

  if document_text.strip():
    system_prompt = (
        "Você é um assistente RAG especializado e prestativo. Responda à"
        " pergunta do usuário baseando-se estritamente no contexto do documento"
        " enviado. Se a resposta não constar no contexto, informe que o"
        " documento não possui essa informação.\n\nCONTEÚDO DO"
        f" DOCUMENTO:\n{document_text}"
    )
  else:
    system_prompt = (
        "Você é um assistente virtual inteligente, amigável e profissional."
    )

  messages_payload = [{"role": "system", "content": system_prompt}]
  for msg in st.session_state.messages:
    messages_payload.append({"role": msg["role"], "content": msg["content"]})

  with st.chat_message("assistant", avatar="🤖"):
    with st.spinner("Analisando e gerando resposta..."):
      try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME, messages=messages_payload, temperature=0.3
        )
        assistant_response = response.choices[0].message.content
      except Exception as e:
        assistant_response = f"❌ Ocorreu um erro na API: {e}"

    st.markdown(assistant_response)

  st.session_state.messages.append(
      {"role": "assistant", "content": assistant_response}
  )
