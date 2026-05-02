import streamlit as st
from github import Github
from google import genai
import os

# 1. Sayfa Konfigürasyonu baslık ve diğer temel ayarlar
st.set_page_config(page_title="CTLWA")

# 2. oturum Yönetimi
if 'ready_post' not in st.session_state:
    st.session_state['ready_post'] = ""

# 3. görsel UI Düzenlemeler
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMarkdown { line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# 4. yan panelde sadece kritik erişim parametreleri için
with st.sidebar:
    st.title("Erişim Parametreleri")
    gh_token = st.text_input("GitHub Kişisel Erişim Jetonu (PAT)", type="password")
    gemini_key = st.text_input("Gemini API Anahtarı", type="password")

# --- TÜM FONKSİYONLAR ---

def get_commits(repo_path, token):
    """GitHub API üzerinden son işlem kayıtlarını çeker."""
    g = Github(token)
    repo = g.get_repo(repo_path)
    return [{"msg": c.commit.message, "files": [f.filename for f in c.files[:2]]} for c in repo.get_commits()[:5]]

def generate_post(data, api_key, tech, project_context):
    """Yapay zeka aracılığıyla profesyonel rapor metni oluşturur."""
    client = genai.Client(api_key=api_key)
    context = "\n".join([f"- {c['msg']}" for c in data])
    
    prompt = f"""
    Aşağıda belirtilen teknik detayları ve GitHub işlem kayıtlarını profesyonel bir rapor metnine dönüştürünüz.
    
    Teknik Envanter: {tech if tech else 'Belirtilmedi'}
    Proje Hedef ve Kapsamı: {project_context if project_context else 'Belirtilmedi'}
    
    İşlem Kayıtları:
    {context}
    
    Yazım Kuralları:
    - Dil tamamen resmi, ciddi ve profesyonel olmalıdır.
    - Metin, sunulan teknik envanter ve proje kapsamı ile doğrudan ilişkilendirilmelidir.
    - Yapılan güncellemelerin projenin genel hedefine nasıl hizmet ettiği vurgulanmalıdır.
    - Emoji veya gayriresmi ifadeler kullanılmamalıdır.
    """
    
    response = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return response.text

# --- ANA ARAYÜZ VE DASHBOARD EKRAN ---

st.title("CTLWA")
st.write("Proje detaylarını ve GitHub Repo yolunu girerek teknik analiz raporu oluşturabilmeye ve bunu da LinkedIn platformunda direkt yayınlamak için kullanılır")

repo_url = st.text_input("GitHub Depo Yolu (kullanıcıadı/repoyolu)", placeholder="kullanıcıadı/repoyolu")

col1, col2 = st.columns(2)
with col1:
    tech_stack = st.text_input("Kullanılan diller veya teknolojiler", placeholder="Örn: Python, Streamlit, SQL")
with col2:
    project_scope = st.text_input("Proje Hedefi / Kapsamı", placeholder="Örn: E-ticaret veri analitiği paneli")

if st.button("Verileri Analiz Et ve Raporla"):
    if not gh_token or not gemini_key or not repo_url:
        st.warning("Lütfen sistem erişimi için gerekli parametreleri yan menüden doldurunuz.")
    else:
        with st.spinner("Teknik veriler ve proje kapsamı analiz edilirken lütfen bekleyiniz..."):
            try:
                data = get_commits(repo_url, gh_token)
                result = generate_post(data, gemini_key, tech_stack, project_scope)
                st.session_state['ready_post'] = result
                st.success("Analiz süreci başarıyla tamamlanmıştır.")
            except Exception as e:
                st.error(f"Sistemsel bir hata meydana geldi: {e}")

# ---sonuc gösterim ---

if st.session_state['ready_post']:
    st.markdown("---")
    st.subheader("Hazırlanan Teknik Metin")
    
    st.markdown(st.session_state['ready_post'])
    
    st.markdown("---")
    st.caption("Raporlama işlemi tamamlanmıştır.")