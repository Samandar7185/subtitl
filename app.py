import streamlit as st
from subtitler import generate_subtitles, translate_subtitles, burn_subtitles
import os

st.set_page_config(page_title="O‘zbekcha Subtitl Tarjimon", page_icon="🎬", layout="centered")
st.markdown(
    """
    <style>
    .main {background-color: #f8fafc;}
    .stButton>button {background-color: #2563eb; color: white; border-radius: 8px;}
    .stDownloadButton>button {background-color: #059669; color: white; border-radius: 8px;}
    .stTextInput>div>div>input {border-radius: 8px;}
    .stTabs [data-baseweb="tab-list"] {justify-content: center;}
    </style>
    """, unsafe_allow_html=True
)
st.markdown("<h1 style='text-align:center; color:#2563eb;'>🎬 O‘zbekcha Subtitl Tarjimon</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b;'>Video uchun avtomatik subtitl, tarjima va tahrirlash platformasi!</p>", unsafe_allow_html=True)

SUPPORTED_LANGS = {
    "Inglizcha": "en",
    "Ruscha": "ru",
    "O‘zbekcha": "uz",
    "Turkcha": "tr",
    "Nemischa": "de",
    "Fransuzcha": "fr",
    "Ispancha": "es",
    "Arabcha": "ar",
    "Xitoycha": "zh-CN",
    "Yaponcha": "ja",
    "Koreyscha": "ko",
    "Hindcha": "hi"
}

tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Subtitl yaratish",
    "2️⃣ Tarjima qilish",
    "3️⃣ Subtitlni tahrirlash",
    "4️⃣ Videoga subtitl biriktirish"
])

with tab1:
    st.markdown("#### 📥 Videoni yuklang va subtitl yarating")
    uploaded_video = st.file_uploader("Videoni yuklang", type=["mp4", "mov", "avi"])
    if uploaded_video:
        with st.spinner("Video yuklanmoqda..."):
            with open("input_video.mp4", "wb") as f:
                f.write(uploaded_video.read())
        # st.video("input_video.mp4")  # Video avtomatik ijro qilinmaydi
        if st.button("Subtitl yaratish", use_container_width=True):
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            def progress_callback(p):
                progress_placeholder.progress(p, text=f"Subtitl yaratilmoqda...")
                status_placeholder.markdown(
                    f"<div style='text-align:center;font-size:18px;color:#2563eb;'>"
                    f"<b>Jarayon:</b> {p}%</div>", unsafe_allow_html=True)
            srt_path = generate_subtitles("input_video.mp4", progress_callback)
            progress_placeholder.progress(100, text="Subtitl yaratildi!")
            status_placeholder.markdown(
                "<div style='text-align:center;font-size:18px;color:#059669;'><b>Subtitl yaratildi! 100%</b></div>",
                unsafe_allow_html=True)
            if srt_path:
                st.success("✅ Subtitl yaratildi!")
                with open(srt_path, "r", encoding="utf-8") as f:
                    st.download_button("Subtitlni yuklab olish (.srt)", f, file_name="subtitle.srt", use_container_width=True)
                st.session_state["srt_path"] = srt_path
            else:
                st.error("Subtitl yaratishda xatolik.")

with tab2:
    st.markdown("#### 🌐 Subtitlni istalgan tilga tarjima qiling")
    st.write("Subtitl faylini yuklang yoki avvalgi bosqichda yaratilgan/yuklangan fayldan foydalaning.")
    uploaded_srt = st.file_uploader("Subtitl (.srt) faylini yuklang", type=["srt"], key="srt_upload")
    srt_path = None
    if uploaded_srt:
        srt_path = "uploaded_subtitle.srt"
        with open(srt_path, "wb") as f:
            f.write(uploaded_srt.read())
    elif "srt_path" in st.session_state:
        srt_path = st.session_state["srt_path"]

    lang_name = st.selectbox("Tarjima tilini tanlang:", list(SUPPORTED_LANGS.keys()), index=0)
    lang = SUPPORTED_LANGS[lang_name]

    if srt_path:
        if st.button("Tarjima qilish", key="translate_btn", use_container_width=True):
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            def progress_callback(p):
                progress_placeholder.progress(p, text=f"Tarjima qilinmoqda...")
                status_placeholder.markdown(
                    f"<div style='text-align:center;font-size:18px;color:#2563eb;'>"
                    f"<b>Jarayon:</b> {p}%</div>", unsafe_allow_html=True)
            translated_path = translate_subtitles(srt_path, lang, progress_callback)
            progress_placeholder.progress(100, text="Tarjima tayyor!")
            status_placeholder.markdown(
                "<div style='text-align:center;font-size:18px;color:#059669;'><b>Tarjima tayyor! 100%</b></div>",
                unsafe_allow_html=True)
            if translated_path:
                with open(translated_path, "r", encoding="utf-8") as f:
                    st.download_button("Tarjima qilingan subtitl (.srt)", f, file_name=f"subtitle_{lang}.srt", use_container_width=True)
                st.session_state["translated_srt"] = translated_path
                st.success("✅ Tarjima tayyor!")
            else:
                st.error("Tarjimada xatolik.")
    else:
        st.info("Avval subtitl yarating yoki yuklang.")

with tab3:
    st.markdown("#### ✏️ Subtitl matnini onlayn tahrirlash va videoga bog‘lash")
    uploaded_edit_srt = st.file_uploader("Subtitl (.srt) faylini yuklang", type=["srt"], key="edit_srt_upload")
    srt_file = None
    if uploaded_edit_srt:
        srt_file = "uploaded_edit_subtitle.srt"
        with open(srt_file, "wb") as f:
            f.write(uploaded_edit_srt.read())
    elif "translated_srt" in st.session_state:
        srt_file = st.session_state["translated_srt"]
    elif "srt_path" in st.session_state:
        srt_file = st.session_state["srt_path"]
    if srt_file:
        with open(srt_file, "r", encoding="utf-8") as f:
            srt_text = f.read()
        edited_srt = st.text_area("Subtitl matni:", value=srt_text, height=300)
        st.download_button("Tahrirlangan subtitlni yuklab olish", edited_srt, file_name="edited_subtitle.srt", use_container_width=True)
        uploaded_edit_video = st.file_uploader("Videoni yuklang (ixtiyoriy, subtitlni video bilan biriktirish uchun)", type=["mp4", "mov", "avi"], key="edit_video_upload")
        if uploaded_edit_video:
            temp_video = "edited_video.mp4"
            with open(temp_video, "wb") as f:
                f.write(uploaded_edit_video.read())
            temp_srt = "edited_subtitle.srt"
            with open(temp_srt, "w", encoding="utf-8") as f:
                f.write(edited_srt)
            if st.button("Videoga subtitl qo‘shish", use_container_width=True):
                with st.spinner("Videoga subtitl qo‘shilmoqda..."):
                    out_path = burn_subtitles(temp_video, temp_srt)
                if out_path:
                    with open(out_path, "rb") as f:
                        st.download_button("Subtitlli videoni yuklab olish", f, file_name="video_with_subs.mp4", use_container_width=True)
                    st.success("✅ Tayyor!")
                else:
                    st.error("Videoga subtitl qo‘shishda xatolik.")
            os.remove(temp_srt)
            os.remove(temp_video)
    else:
        st.info("Subtitl faylini yuklang yoki avvalgi bosqichda yarating/yuklang.")

with tab4:
    st.markdown("#### 🎬 Videoga subtitl biriktirish")
    uploaded_video2 = st.file_uploader("Videoni yuklang", type=["mp4", "mov", "avi"], key="video_upload_attach")
    uploaded_srt2 = st.file_uploader("Subtitl (.srt) faylini yuklang", type=["srt"], key="srt_upload_attach")
    if uploaded_video2 and uploaded_srt2:
        video_path = "input_video_attach.mp4"
        srt_path = "input_subtitle_attach.srt"
        with open(video_path, "wb") as f:
            f.write(uploaded_video2.read())
        with open(srt_path, "wb") as f:
            f.write(uploaded_srt2.read())
        if st.button("Videoga subtitl biriktirish", use_container_width=True):
            with st.spinner("Videoga subtitl biriktirilmoqda..."):
                out_path = burn_subtitles(video_path, srt_path)
            if out_path:
                with open(out_path, "rb") as f:
                    st.download_button("Subtitlli videoni yuklab olish", f, file_name="video_with_subs.mp4", use_container_width=True)
                st.success("✅ Tayyor!")
            else:
                st.error("Videoga subtitl biriktirishda xatolik.")
    else:
        st.info("Video va subtitl faylini yuklang.")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#94a3b8;'>© 2024 O‘zbekcha Subtitl Tarjimon | <a href='https://github.com/' target='_blank'>GitHub</a></p>", unsafe_allow_html=True)

# Ishga tushurish bo'yicha ko'rsatma:
# 1. Terminal yoki Anaconda Prompt-ni oching.
# 2. Quyidagi buyruqni yozing va Enter bosing:
#    streamlit run app.py
# 3. Brauzerda ochilgan havola orqali interfeysdan foydalaning.

# Dastur uchun barcha kerakli kutubxonalarni o‘rnatish:
# 1. Terminal yoki Anaconda Prompt-ni oching.
# 2. Quyidagi buyruqlarni ketma-ket yozing va Enter bosing:

# pip install streamlit
# pip install openai-whisper
# pip install googletrans==4.0.0-rc1
# pip install moviepy
# pip install ffmpeg-python

# Whisper ishlashi uchun sizda ffmpeg ham o‘rnatilgan bo‘lishi kerak:
# Windows uchun: https://ffmpeg.org/download.html dan yuklab oling va o‘rnatib, ffmpeg.exe joylashgan papkani PATH ga qo‘shing.

# Agar "streamlit" topilmadi degan xatolik chiqsa, quyidagilarni bajaring:
# 1. Terminalda quyidagi buyruqni yozing va Enter bosing:
#    pip install streamlit
# 2. O‘rnatish tugagach, yana ishga tushiring:
#    streamlit run app.py

# Agar "ModuleNotFoundError: No module named 'whisper'" xatoligi chiqsa:
# 1. Terminalda quyidagini yozing va Enter bosing:
#    pip install openai-whisper
# 2. O‘rnatish tugagach, yana streamlit dasturini ishga tushiring.

# MUHIM: Python 3.13 da cgi moduli olib tashlangan va googletrans ishlamaydi!
# Tavsiya: Python 3.12 yoki 3.11 versiyasini o‘rnating va virtual environment yarating.
# Yoki, subtitler.py faylida googletrans o‘rniga deep-translator kutubxonasidan foydalaning:
# pip install deep-translator

# Agar deep-translator ishlatilsa, subtitler.py faylida quyidagicha o‘zgartiring:
# from deep_translator import GoogleTranslator
# ...
# translated = GoogleTranslator(source='auto', target=dest_lang).translate(block[2])

# DASTURNI ISHLATISH UCHUN QADAM-B-QADAM YO'RIQNOMA:

# 1. Python 3.12 yoki 3.11 versiyasini o‘rnating (https://www.python.org/downloads/).
#    Python 3.13 ishlamaydi! (googletrans ishlamaydi, deep-translator ishlaydi)

# 2. Windows-da "cmd" yoki "Anaconda Prompt" yoki "PowerShell" oching.

# 3. Dastur joylashgan papkaga o'ting:
#    cd C:\Users\Samxoji\Downloads\new

# 4. Quyidagi buyruqlarni birma-bir yozing va Enter bosing:

# pip install streamlit
# pip install openai-whisper
# pip install deep-translator
# pip install moviepy
# pip install ffmpeg-python

# 5. ffmpeg dasturini yuklab oling va o‘rnating:
#    https://ffmpeg.org/download.html
#    O‘rnatilgandan so‘ng, ffmpeg.exe joylashgan papkani Windows PATH ga qo‘shing.

# 6. Dastur fayllari tayyor bo‘lsa, quyidagicha ishga tushiring:
#    C:\Users\Samxoji\AppData\Roaming\Python\Python313\Scripts\streamlit.exe run app.py

# 7. Brauzerda ochilgan oynada dasturdan foydalaning.

# 8. Agar xatolik chiqsa, xabar bering yoki xatolik matnini menga yuboring.

# DASTURNI INTERNETDA (ONLAYN) ISHLATISH YO'LLARI:

# 1. Streamlit Cloud (bepul, eng oson):
#    - https://streamlit.io/cloud saytiga kiring.
#    - GitHub akkauntingiz bilan tizimga kiring.
#    - Dastur fayllarini (app.py, subtitler.py va boshqalar) GitHub reposiga yuklang.
#    - Streamlit Cloud’da yangi app yarating va GitHub-dagi repozitoriy manzilini kiriting.
#    - Deploy tugmasini bosing, dastur onlayn ochiladi.

# 2. Alternativa: PythonAnywhere, Heroku, yoki boshqa cloud serverlar.
#    - Lekin, ffmpeg va og‘ir kutubxonalar uchun Streamlit Cloud eng qulay.

# Eslatma:
# - Onlayn ishlatishda fayl yo‘llari va ffmpeg yo‘li avtomatik aniqlanadi, odatda faqat `"ffmpeg"` deb yozish yetarli.
# - Onlayn serverlarda ba’zi og‘ir AI modellar (masalan, whisper) ishlamasligi yoki sekin ishlashi mumkin.

# Qadamlar:
# 1. GitHub’da yangi repozitoriy yarating.
# 2. app.py, subtitler.py va requirements.txt fayllarini yuklang.
# 3. requirements.txt faylida quyidagilar bo‘lishi kerak:
#    streamlit
#    openai-whisper
#    deep-translator
#    moviepy
#    ffmpeg-python

# 4. Streamlit Cloud’da deploy qiling.

# "Your app is in the oven" yozuvi Streamlit Cloud (yoki Streamlit) dastur yuklanayotganda chiqadi.
# Bu normal holat – dastur yuklanishi va ishga tushishi uchun biroz vaqt ketadi.
# Dastur yuklanib bo‘lgach, interfeys ochiladi va foydalanishingiz mumkin bo‘ladi.
# Agar bu yozuv uzoq vaqt turib qolsa:
# 1. Internet tezligini tekshiring.
# 2. Fayllarda xatolik yo‘qligini va requirements.txt to‘g‘ri ekanini tekshiring.
# 3. Dastur loglarida (Streamlit Cloud sahifasida) xatolik bo‘lsa, shu chatga yuboring – yordam beraman.
#    deep-translator
#    moviepy
#    ffmpeg-python

# 4. Streamlit Cloud’da deploy qiling.

# "Your app is in the oven" yozuvi Streamlit Cloud (yoki Streamlit) dastur yuklanayotganda chiqadi.
# Bu normal holat – dastur yuklanishi va ishga tushishi uchun biroz vaqt ketadi.
# Dastur yuklanib bo‘lgach, interfeys ochiladi va foydalanishingiz mumkin bo‘ladi.
# Agar bu yozuv uzoq vaqt turib qolsa:
# 1. Internet tezligini tekshiring.
# 2. Fayllarda xatolik yo‘qligini va requirements.txt to‘g‘ri ekanini tekshiring.
# 3. Dastur loglarida (Streamlit Cloud sahifasida) xatolik bo‘lsa, shu chatga yuboring – yordam beraman.
