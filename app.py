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

  # Variável para capturar prompt (seja via botão ou via caixa de texto)
  user_query = None

  if document_text.strip() and len(st.session_state.messages) == 0:
    st.markdown("#### ⚡ Sugestões Rápidas de Interação:")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
      if st.button("📄 Resumir Documento"):
        user_query = "Faça um resumo detalhado e estruturado deste documento."
    with col_b:
      if st.button("🔍 Extrair Pontos-Chave"):
        user_query = "Quais são os principais pontos e conclusões do texto?"
    with col_c:
      if st.button("❓ Elaborar Quiz"):
        user_query = (
            "Elabore 3 perguntas de múltipla escolha com base no texto"
            " fornecido."
        )

  # Exibir histórico de mensagens armazenadas
  for message in st.session_state.messages:
    avatar_icon = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar_icon):
      st.markdown(message["content"])

  # Caixa de input padrão do Streamlit (sempre visível)
  chat_input_val = st.chat_input("Digite sua dúvida ou comando...")

  # Define qual foi a mensagem enviada (prioriza a caixa de texto, se preenchida, ou o botão clicado)
  if chat_input_val:
    user_query = chat_input_val

  if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar="👤"):
      st.markdown(user_query)

    if document_text.strip():
      system_prompt = (
          "Você é um assistente RAG especializado e académico. Responda à"
          " pergunta baseando-se estritamente no documento anexado. Caso a"
          " informação não conste no texto, informe educadamente.\n\nCONTEÚDO"
          f" DO DOCUMENTO:\n{document_text}"
      )
    else:
      system_prompt = (
          "Você é um assistente virtual inteligente e altamente qualificado."
      )

    messages_payload = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
      messages_payload.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant", avatar="🤖"):
      with st.spinner("A processar informações via Microsoft Foundry..."):
        try:
          response = client.chat.completions.create(
              model=DEPLOYMENT_NAME,
              messages=messages_payload,
              temperature=0.3,
          )
          assistant_response = response.choices[0].message.content
        except Exception as e:
          assistant_response = f"❌ Erro na comunicação com o serviço: {e}"

      st.markdown(assistant_response)

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )

with tab2:
  st.markdown("### 📊 Painel de Demonstração e Estatísticas")
  st.markdown(
      "Esta aba apresenta uma visão geral do funcionamento lógico e do"
      " ecossistema implementado."
  )

  col_1, col_2 = st.columns(2)

  with col_1:
    st.markdown(
        """
        <div class="demo-box">
            <h4>🧠 O que é RAG?</h4>
            <p>Retrieval-Augmented Generation combina a capacidade criativa dos Modelos de Linguagem com uma base de dados externa (o seu PDF/TXT).</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

  with col_2:
    st.markdown(
        """
        <div class="demo-box">
            <h4>⚙️ Integração Microsoft Foundry</h4>
            <p>O sistema consome endpoints seguros do Azure AI Services através do modelo
