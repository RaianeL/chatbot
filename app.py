from openai import AzureOpenAI
import pypdf
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Assistente IA | Microsoft Foundry RAG",
    page_icon="🎓",
    layout="wide",
)

# ==========================================
# 1. CONFIGURAÇÃO DA API (MICROSOFT FOUNDRY)
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
# 2. INTERFACE E ESTILO (CSS CUSTOMIZADO)
# ==========================================
st.markdown(
    """
    <style>
    .stApp { background-color: #f4f6f9; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 5rem; max-width: 1000px; }
    .hero-banner { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 2rem; border-radius: 16px; color: white; text-align: center; margin-bottom: 1.5rem; box-shadow: 0 4px 20px rgba(30, 58, 138, 0.2); }
    .hero-banner h1 { color: white; font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem; }
    .hero-banner p { color: #e2e8f0; font-size: 1.1rem; margin: 0; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .demo-box { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 1.2rem; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 1rem; }
    </style>
""",
    unsafe_allow_html=True,
)

# Cabeçalho Principal
st.markdown(
    """
    <div class="hero-banner">
        <h1>🎓 Plataforma Académica de ChatBot com RAG</h1>
        <p>Desenvolvido com Python, Streamlit e Microsoft Foundry (Azure AI Services)</p>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 3. BARRA LATERAL (PAINEL DE CONTROLO)
# ==========================================
with st.sidebar:
  st.image(
      "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=400&auto=format&fit=crop",
      caption="Inteligência Artificial & RAG",
      use_container_width=True,
  )

  st.markdown("### 🎛️ Painel de Controlo")
  uploaded_file = st.file_uploader(
      "Envie sua Base de Conhecimento", type=["pdf", "txt"]
  )

  document_text = ""

  if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension == "txt":
      document_text = uploaded_file.getvalue().decode("utf-8")
      st.success(f"📄 TXT Carregado: {uploaded_file.name}")
    elif file_extension == "pdf":
      try:
        reader = pypdf.PdfReader(uploaded_file)
        extracted_text = []
        for page in reader.pages:
          text = page.extract_text()
          if text:
            extracted_text.append(text)
        document_text = "\n".join(extracted_text)
        st.success(f"📑 PDF Carregado: {uploaded_file.name}")
      except Exception as e:
        st.error(f"Erro ao ler PDF: {e}")

    word_count = len(document_text.split())
    st.metric(label="Total de Palavras no Contexto", value=f"{word_count}")
  else:
    st.info(
        "💡 Nenhum documento carregado. O bot atuará em modo livre de"
        " conversação."
    )

  st.markdown("---")
  st.markdown("🛠️ **Detalhes Técnicos:**")
  st.text(f"Modelo: {DEPLOYMENT_NAME}")
  st.text("API: Azure OpenAI / Foundry")

# ==========================================
# 4. ABAS DE NAVEGAÇÃO E LÓGICA DO CHAT
# ==========================================
tab1, tab2 = st.tabs(["💬 Chat Interativo", "📊 Demonstração e Estatísticas"])

with tab1:
  if "messages" not in st.session_state:
    st.session_state.messages = []

  if document_text.strip() and len(st.session_state.messages) == 0:
    st.markdown("#### ⚡ Sugestões Rápidas de Interação:")
    col_a, col_b, col_c = st.columns(3)
    quick_prompt = None
    with col_a:
      if st.button("📄 Resumir Documento"):
        quick_prompt = (
            "Faça um resumo detalhado e estruturado deste documento."
        )
    with col_b:
      if st.button("🔍 Extrair Pontos-Chave"):
        quick_prompt = "Quais são os principais pontos e conclusões do texto?"
    with col_c:
      if st.button("❓ Elaborar Quiz"):
        quick_prompt = (
            "Elabore 3 perguntas de múltipla escolha com base no texto"
            " fornecido."
        )
