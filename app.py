from openai import AzureOpenAI
import pypdf
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Assistente IA | Microsoft Foundry RAG",
    page_icon="✨",
    layout="wide",
)

# ==========================================
# 1. INTERFACE E ESTILO (CSS CUSTOMIZADO AVANÇADO)
# ==========================================
st.markdown(
    """
    <style>
    /* Estilos globais e fontes */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Container Principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 900px;
    }

    /* Cabeçalho atraente */
    .hero-container {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.3);
    }
    .hero-container h1 {
        color: white;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    .hero-container p {
        color: #e2e8f0;
        font-size: 1.05rem;
        margin: 0;
    }

    /* Estilização da barra lateral */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        padding-top: 1rem;
    }

    /* Cartões informativos na sidebar */
    .info-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
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

# ==========================================
# CABEÇALHO VISUAL
# ==========================================
st.markdown(
    """
    <div class="hero-container">
        <h1>✨ Assistente Inteligente com RAG</h1>
        <p>Explore os seus documentos PDF e TXT com inteligência artificial avançada da Microsoft Foundry.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 3. UPLOAD DE ARQUIVOS E SISTEMA RAG (SIDEBAR)
# ==========================================
st.sidebar.markdown("### 🎛️ Painel de Controlo")
st.sidebar.markdown(
    "Carregue um documento para habilitar o contexto inteligente."
)

uploaded_file = st.sidebar.file_uploader(
    "Escolha um arquivo PDF ou TXT", type=["pdf", "txt"]
)

document_text = ""

if uploaded_file is not None:
  file_extension = uploaded_file.name.split(".")[-1].lower()

  if file_extension == "txt":
    document_text = uploaded_file.getvalue().decode("utf-8")
    st.sidebar.success(f"📄 TXT Ativo: **{uploaded_file.name}**")

  elif file_extension == "pdf":
    try:
      reader = pypdf.PdfReader(uploaded_file)
      extracted_text = []
      for page in reader.pages:
        text = page.extract_text()
        if text:
          extracted_text.append(text)
      document_text = "\n".join(extracted_text)
      st.sidebar.success(f"📑 PDF Ativo: **{uploaded_file.name}**")
    except Exception as e:
      st.sidebar.error(f"Erro ao ler PDF: {e}")

  # Métrica de contexto na barra lateral
  word_count = len(document_text.split())
  st.sidebar.metric(
      label="Volume da Base de Conhecimento", value=f"{word_count} palavras"
  )
else:
  st.sidebar.info(
      "💡 Dica: Nenhum documento carregado. O bot funcionará no modo geral."
  )

# ==========================================
# 4. LÓGICA DE CHAT E HISTÓRICO
# ==========================================

if "messages" not in st.session_state:
  st.session_state.messages = []

# Sugestões rápidas de perguntas se houver documento carregado
if document_text.strip() and len(st.session_state.messages) == 0:
  st.markdown("##### ⚡ Sugestões de perguntas rápidas:")
  col1, col2, col3 = st.columns(3)
  suggested_prompt = None

  with col1:
    if st.button("📄 Resumir o documento"):
      suggested_prompt = (
          "Faça um resumo completo e estruturado dos pontos principais deste"
          " documento."
      )
  with col2:
    if st.button("❓ Quais os tópicos centrais?"):
      suggested_prompt = (
          "Quais são os principais tópicos e objetivos abordados no texto?"
      )
  with col3:
    if st.button("🔍 Explicar termos técnicos"):
      suggested_prompt = (
          "Identifique e explique os termos técnicos ou conceitos mais"
          " importantes presentes no documento."
      )

  if suggested_prompt:
    st.session_state.messages.append(
        {"role": "user", "content": suggested_prompt}
    )
    st.rerun()

# Exibir histórico de mensagens
for message in st.session_state.messages:
  avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
  with st.chat_message(message["role"], avatar=avatar):
    st.markdown(message["content"])

# Caixa de input do chat
if prompt := st.chat_input(
    "Escreva a sua pergunta sobre o documento ou assunto..."
):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user", avatar="🧑‍💻"):
    st.markdown(prompt)

  # Montagem do prompt do sistema com RAG
  if document_text.strip():
    system_prompt = (
        "Você é um assistente RAG especializado, rigoroso e prestativo. Responda"
        " à pergunta do utilizador baseando-se estritamente e exclusivamente no"
        " contexto do documento fornecido abaixo. Se a resposta não constar no"
        " documento, informe educadamente que a informação não está presente"
        " no material.\n\nCONTEÚDO DO DOCUMENTO:\n"
        f"{document_text}"
    )
  else:
    system_prompt = (
        "Você é um assistente virtual inteligente, prestativo e profissional."
    )

  messages_payload = [{"role": "system", "content": system_prompt}]
  for msg in st.session_state.messages:
    messages_payload.append({"role": msg["role"], "content": msg["content"]})

  with st.chat_message("assistant", avatar="🤖"):
    with st.spinner("A analisar documento e a gerar resposta..."):
      try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME, messages=messages_payload, temperature=0.3
        )
        assistant_response = response.choices[0].message.content
      except Exception as e:
        assistant_response = f"❌ Ocorreu um erro ao comunicar com a API: {e}"

    st.markdown(assistant_response)

  st.session_state.messages.append(
      {"role": "assistant", "content": assistant_response}
  )
