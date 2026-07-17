import streamlit as st
import json
import os
import random
import pandas as pd
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="VocaCard - 3D 플래시카드 단어장",
    page_icon="🎴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants & Paths
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DATA_DIR, "words.json")

# Default Word List
DEFAULT_WORDS = [
    {"word": "serendipity", "meaning": "뜻밖의 발견, 의외의 기쁨", "example": "Finding this cozy bookstore was pure serendipity.", "starred": False},
    {"word": "ephemeral", "meaning": "수명이 짧은, 덧없는", "example": "Cherry blossoms are beautiful but ephemeral.", "starred": False},
    {"word": "resilient", "meaning": "회복력 있는, 탄력 있는", "example": "She is a resilient girl who overcomes any hardship.", "starred": False},
    {"word": "luminous", "meaning": "빛나는, 반짝이는", "example": "The watch has luminous hands that glow in the dark.", "starred": False},
    {"word": "eloquent", "meaning": "유창한, 설득력 있는", "example": "His eloquent speech moved the entire audience.", "starred": False},
    {"word": "pragmatic", "meaning": "실용적인", "example": "We need to find a pragmatic solution to this problem.", "starred": False},
    {"word": "mellifluous", "meaning": "달콤한, 감미로운", "example": "The singer has a mellifluous voice.", "starred": False},
    {"word": "solitude", "meaning": "고독, 외로움 (긍정적인 의미)", "example": "He enjoyed the peace and solitude of the forest.", "starred": False}
]

# Style definitions (Custom CSS)
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Noto+Sans+KR:wght@300;400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #a855f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    .stButton>button {
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
    }
    
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #6366f1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
    """, unsafe_allow_html=True)

# File DB Operations
def load_db():
    if not os.path.exists(DB_FILE):
        save_db(DEFAULT_WORDS)
        return DEFAULT_WORDS
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"데이터 파일을 불러오는 중 오류 발생 (기본 데이터를 로드합니다): {e}")
        return DEFAULT_WORDS

def save_db(data):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"데이터 파일 저장 오류: {e}")

# HTML/CSS/JS 3D Flashcard Renderer
def render_3d_flashcard(word, meaning, example, index, total):
    # CSS & HTML template for 3D flip card
    # Front: Gradient Indigo-Purple, Back: Glassmorphic Dark Blue/Grey
    example_section = f'''
    <div class="example-box">
        <div class="example-title">Example Sentence</div>
        <div class="example-text">"{example}"</div>
    </div>
    ''' if example and example.strip() else ''

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Noto+Sans+KR:wght@400;700&display=swap');
    
    body {{
        margin: 0;
        padding: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: transparent;
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
    }}
    
    .scene {{
        width: 100%;
        max-width: 550px;
        height: 340px;
        perspective: 1200px;
    }}
    
    .card {{
        width: 100%;
        height: 100%;
        position: relative;
        transform-style: preserve-3d;
        transition: transform 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
    }}
    
    .card.is-flipped {{
        transform: rotateY(180deg);
    }}
    
    .card-face {{
        position: absolute;
        width: 100%;
        height: 100%;
        backface-visibility: hidden;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        padding: 2.5rem;
        user-select: none;
    }}
    
    .card-face-front {{
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .card-face-back {{
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
        transform: rotateY(180deg);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }}
    
    .badge {{
        align-self: flex-start;
        background: rgba(255, 255, 255, 0.15);
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .card-face-back .badge {{
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }}
    
    .main-text-container {{
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        margin: 1.5rem 0;
    }}
    
    .word-text {{
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        text-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }}
    
    .meaning-text {{
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        color: #f8fafc;
    }}
    
    .example-box {{
        width: 100%;
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #6366f1;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        box-sizing: border-box;
        text-align: left;
    }}
    
    .example-title {{
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }}
    
    .example-text {{
        font-size: 0.95rem;
        font-style: italic;
        color: #cbd5e1;
        line-height: 1.4;
    }}
    
    .footer-instruction {{
        text-align: center;
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.6);
        letter-spacing: 0.02em;
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ opacity: 0.4; }}
        50% {{ opacity: 0.8; }}
        100% {{ opacity: 0.4; }}
    }}
    
    .progress-tag {{
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.4);
        align-self: flex-end;
    }}
    </style>
    </head>
    <body>
        <div class="scene">
            <div class="card" id="cardElement" onclick="toggleFlip()">
                <!-- Front Side -->
                <div class="card-face card-face-front">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="badge">Spelling</span>
                        <span class="progress-tag">{index + 1} / {total}</span>
                    </div>
                    <div class="main-text-container">
                        <h1 class="word-text">{word}</h1>
                    </div>
                    <div class="footer-instruction">클릭하여 뜻 보기 🔄</div>
                </div>
                
                <!-- Back Side -->
                <div class="card-face card-face-back">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="badge">Meaning</span>
                        <span class="progress-tag">{index + 1} / {total}</span>
                    </div>
                    <div class="main-text-container">
                        <div class="meaning-text">{meaning}</div>
                        {example_section}
                    </div>
                    <div class="footer-instruction">클릭하여 단어 보기 🔄</div>
                </div>
            </div>
        </div>
        
        <script>
            function toggleFlip() {{
                const card = document.getElementById('cardElement');
                card.classList.toggle('is-flipped');
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=360)

# Initialize Session States
if "words" not in st.session_state:
    st.session_state.words = load_db()
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "study_order" not in st.session_state:
    st.session_state.study_order = list(range(len(st.session_state.words)))
if "is_shuffled" not in st.session_state:
    st.session_state.is_shuffled = False
if "quiz_active" not in st.session_state:
    st.session_state.quiz_active = False
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_count" not in st.session_state:
    st.session_state.quiz_count = 0
if "quiz_choices" not in st.session_state:
    st.session_state.quiz_choices = []
if "quiz_correct_word" not in st.session_state:
    st.session_state.quiz_correct_word = None
if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = False
if "quiz_user_choice" not in st.session_state:
    st.session_state.quiz_user_choice = None

# In case DB is updated, refresh orders
def sync_db_state():
    save_db(st.session_state.words)
    # Ensure current index doesn't overshoot
    if st.session_state.current_index >= len(st.session_state.words):
        st.session_state.current_index = max(0, len(st.session_state.words) - 1)
    
    # Rebuild study order if needed
    if not st.session_state.is_shuffled:
        st.session_state.study_order = list(range(len(st.session_state.words)))
    else:
        # Keep shuffled but filter to match list size
        st.session_state.study_order = [i for i in st.session_state.study_order if i < len(st.session_state.words)]
        # Add any missing new indices
        for i in range(len(st.session_state.words)):
            if i not in st.session_state.study_order:
                st.session_state.study_order.append(i)

# Main UI layout
inject_custom_css()

# Header Section
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<h1 class="main-title">⚡ VocaCard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">뜻과 스펠링이 양면에 적힌 나만의 3D 플래시카드 단어장</p>', unsafe_allow_html=True)

with col2:
    total_w = len(st.session_state.words)
    starred_w = sum(1 for w in st.session_state.words if w.get("starred", False))
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-top: 10px;">
        <div class="metric-card" style="flex: 1; padding: 0.8rem;">
            <div class="metric-value" style="font-size: 1.5rem;">{total_w}</div>
            <div class="metric-label" style="font-size: 0.7rem;">전체 단어</div>
        </div>
        <div class="metric-card" style="flex: 1; padding: 0.8rem;">
            <div class="metric-value" style="font-size: 1.5rem; color: #eab308;">{starred_w}</div>
            <div class="metric-label" style="font-size: 0.7rem;">중요 단어</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎴 플래시카드 학습", "✍️ 단어장 관리", "🎮 퀴즈 모드", "💾 백업 & 복원"])

# ----------------- TAB 1: STUDY MODE -----------------
with tab1:
    if len(st.session_state.words) == 0:
        st.info("단어장이 비어 있습니다! '단어장 관리' 탭에서 단어를 추가하거나 아래 버튼을 눌러 기본 단어장을 불러오세요.")
        if st.button("기본 단어장 불러오기", key="load_defaults"):
            st.session_state.words = DEFAULT_WORDS.copy()
            sync_db_state()
            st.rerun()
    else:
        # Settings inside tab
        col_ctrl1, col_ctrl2 = st.columns([2, 1])
        with col_ctrl1:
            starred_only = st.checkbox("⭐ 중요 단어만 모아보기", value=False)
        
        # Filter indices based on settings
        if starred_only:
            valid_indices = [i for i, w in enumerate(st.session_state.words) if w.get("starred", False)]
            if len(valid_indices) == 0:
                st.warning("중요(⭐) 표시된 단어가 없습니다. 카드 앞면의 별표를 누르거나 관리 탭에서 설정해보세요!")
                valid_indices = list(range(len(st.session_state.words)))
                starred_only = False
        else:
            valid_indices = list(range(len(st.session_state.words)))
            
        # Re-arrange based on shuffle setting
        if st.session_state.is_shuffled:
            active_order = [i for i in st.session_state.study_order if i in valid_indices]
            # Handle corner case where active_order is empty but valid_indices is not
            if not active_order:
                active_order = valid_indices
        else:
            active_order = valid_indices

        # Ensure active current index is valid
        if st.session_state.current_index >= len(active_order):
            st.session_state.current_index = 0
            
        # Select active word
        active_idx = active_order[st.session_state.current_index] if active_order else 0
        word_item = st.session_state.words[active_idx]
        
        # Star toggle above the card
        col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
        with col_s2:
            st.write("") # Spacer
            # Dynamic star button
            is_starred = word_item.get("starred", False)
            star_label = "⭐ 중요 단어 해제" if is_starred else "☆ 중요 단어로 표시"
            if st.button(star_label, use_container_width=True):
                st.session_state.words[active_idx]["starred"] = not is_starred
                sync_db_state()
                st.rerun()

        # Render Card
        col_c1, col_c2, col_c3 = st.columns([1, 4, 1])
        with col_c2:
            render_3d_flashcard(
                word=word_item["word"],
                meaning=word_item["meaning"],
                example=word_item.get("example", ""),
                index=st.session_state.current_index,
                total=len(active_order)
            )
            
            # Progress bar
            progress_pct = (st.session_state.current_index + 1) / len(active_order) if active_order else 0
            st.progress(progress_pct)
        
        # Navigation controls
        col_nav1, col_nav2, col_nav3, col_nav4 = st.columns(4)
        
        with col_nav1:
            if st.button("⬅️ 이전 단어", use_container_width=True, disabled=st.session_state.current_index == 0):
                st.session_state.current_index -= 1
                st.rerun()
                
        with col_nav2:
            if st.button("다음 단어 ➡️", use_container_width=True, disabled=st.session_state.current_index == len(active_order) - 1):
                st.session_state.current_index += 1
                st.rerun()
                
        with col_nav3:
            shuffle_label = "🔁 순서대로 보기" if st.session_state.is_shuffled else "🔀 단어 섞기"
            if st.button(shuffle_label, use_container_width=True):
                st.session_state.is_shuffled = not st.session_state.is_shuffled
                if st.session_state.is_shuffled:
                    random.shuffle(st.session_state.study_order)
                st.session_state.current_index = 0
                st.rerun()
                
        with col_nav4:
            if st.button("🔄 처음부터", use_container_width=True):
                st.session_state.current_index = 0
                st.rerun()

# ----------------- TAB 2: MANAGE WORDS -----------------
with tab2:
    st.subheader("📝 새 단어 추가")
    with st.form("add_word_form", clear_on_submit=True):
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            new_word = st.text_input("영어 단어 (Spelling) *", placeholder="example")
        with col_in2:
            new_meaning = st.text_input("뜻 (Meaning) *", placeholder="예시, 본보기")
            
        new_example = st.text_area("예문 (Example Sentence) - 선택 사항", placeholder="This is a good example of modern design.", height=68)
        
        submitted = st.form_submit_button("단어장 추가하기", use_container_width=True)
        if submitted:
            if not new_word.strip() or not new_meaning.strip():
                st.error("영어 단어와 뜻은 필수 입력 항목입니다!")
            else:
                st.session_state.words.append({
                    "word": new_word.strip(),
                    "meaning": new_meaning.strip(),
                    "example": new_example.strip(),
                    "starred": False
                })
                sync_db_state()
                st.success(f"'{new_word.strip()}' 단어가 추가되었습니다!")
                st.rerun()
                
    st.markdown("---")
    st.subheader("🔍 단어 목록 및 검색")
    
    if len(st.session_state.words) == 0:
        st.info("저장된 단어가 없습니다.")
    else:
        # Convert to dataframe for better visualization and tabular action
        df = pd.DataFrame(st.session_state.words)
        # Re-arrange column names for representation
        df_display = df.copy()
        df_display.columns = ["단어 (Word)", "뜻 (Meaning)", "예문 (Example)", "중요 (Starred)"]
        
        # Search input
        search_query = st.text_input("🔍 검색어 입력 (영어 또는 뜻)", "")
        if search_query:
            filtered_df = df_display[
                df_display["단어 (Word)"].str.contains(search_query, case=False, na=False) |
                df_display["뜻 (Meaning)"].str.contains(search_query, case=False, na=False)
            ]
        else:
            filtered_df = df_display
            
        st.dataframe(filtered_df, use_container_width=True)
        
        # Word operations (Delete)
        st.subheader("🗑️ 단어 삭제")
        words_to_delete = st.multiselect("삭제할 단어를 선택하세요", [w["word"] for w in st.session_state.words])
        if st.button("선택한 단어 삭제", type="primary"):
            if words_to_delete:
                st.session_state.words = [w for w in st.session_state.words if w["word"] not in words_to_delete]
                sync_db_state()
                st.success(f"선택한 단어 {len(words_to_delete)}개가 삭제되었습니다.")
                st.rerun()
            else:
                st.warning("삭제할 단어를 선택하세요.")

        # Batch Operations
        st.subheader("⚠️ 초기화")
        col_reset1, col_reset2 = st.columns(2)
        with col_reset1:
            if st.button("⚠️ 모든 데이터 삭제 (비우기)", use_container_width=True, type="secondary"):
                st.session_state.words = []
                sync_db_state()
                st.session_state.current_index = 0
                st.success("단어장이 완전히 비워졌습니다.")
                st.rerun()
        with col_reset2:
            if st.button("🔄 기본 단어장 복구", use_container_width=True):
                st.session_state.words = DEFAULT_WORDS.copy()
                sync_db_state()
                st.session_state.current_index = 0
                st.success("기본 단어장으로 리셋되었습니다.")
                st.rerun()

# ----------------- TAB 3: QUIZ MODE -----------------
with tab3:
    st.subheader("🎮 퀴즈 타임!")
    st.write("단어장에 등록된 단어로 4지선다형 객관식 퀴즈를 진행합니다.")
    
    if len(st.session_state.words) < 4:
        st.warning("퀴즈를 진행하기 위해서는 최소 4개 이상의 단어가 단어장에 등록되어 있어야 합니다. (현재: {}개)".format(len(st.session_state.words)))
    else:
        # Quiz state initial setup helper
        def prepare_new_question():
            correct_item = random.choice(st.session_state.words)
            st.session_state.quiz_correct_word = correct_item
            
            # Select 3 other random items for choices
            other_items = [w for w in st.session_state.words if w["word"] != correct_item["word"]]
            wrong_choices = random.sample(other_items, 3)
            
            choices = [correct_item["meaning"]] + [w["meaning"] for w in wrong_choices]
            random.shuffle(choices)
            
            st.session_state.quiz_choices = choices
            st.session_state.quiz_answered = False
            st.session_state.quiz_user_choice = None
            
        # Quiz Stats Area
        q_col1, q_col2, q_col3 = st.columns([1, 1, 1])
        with q_col1:
            st.metric("푼 문제 수", st.session_state.quiz_count)
        with q_col2:
            st.metric("맞춘 문제 수", st.session_state.quiz_score)
        with q_col3:
            accuracy = (st.session_state.quiz_score / st.session_state.quiz_count * 100) if st.session_state.quiz_count > 0 else 0.0
            st.metric("정답률", f"{accuracy:.1f}%")
            
        if not st.session_state.quiz_active:
            if st.button("🚀 퀴즈 시작하기", use_container_width=True, type="primary"):
                st.session_state.quiz_active = True
                st.session_state.quiz_score = 0
                st.session_state.quiz_count = 0
                prepare_new_question()
                st.rerun()
        else:
            # Quiz is active
            correct_word = st.session_state.quiz_correct_word
            
            st.markdown(f"""
            <div style="background-color: rgba(99, 102, 241, 0.1); border-radius: 15px; padding: 2rem; text-align: center; margin-bottom: 2rem; border: 1px solid rgba(99, 102, 241, 0.3);">
                <div style="font-size: 1rem; color: #94a3b8; margin-bottom: 0.5rem; text-transform: uppercase;">다음 단어의 뜻은 무엇일까요?</div>
                <div style="font-size: 3.5rem; font-weight: 800; color: white; letter-spacing: -0.01em;">{correct_word['word']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Create choices buttons
            cols_choice = st.columns(2)
            for i, choice in enumerate(st.session_state.quiz_choices):
                col_i = cols_choice[i % 2]
                with col_i:
                    # Logic when a choice is clicked
                    if not st.session_state.quiz_answered:
                        if st.button(choice, key=f"btn_{i}", use_container_width=True):
                            st.session_state.quiz_answered = True
                            st.session_state.quiz_user_choice = choice
                            st.session_state.quiz_count += 1
                            if choice == correct_word["meaning"]:
                                st.session_state.quiz_score += 1
                            st.rerun()
                    else:
                        # After answer is submitted, show color codes
                        is_correct_choice = (choice == correct_word["meaning"])
                        is_user_choice = (choice == st.session_state.quiz_user_choice)
                        
                        if is_correct_choice:
                            st.button(f"🟢 {choice}", key=f"btn_{i}", use_container_width=True, type="primary", disabled=True)
                        elif is_user_choice:
                            st.button(f"🔴 {choice}", key=f"btn_{i}", use_container_width=True, disabled=True)
                        else:
                            st.button(choice, key=f"btn_{i}", use_container_width=True, disabled=True)

            # Feedback message
            if st.session_state.quiz_answered:
                if st.session_state.quiz_user_choice == correct_word["meaning"]:
                    st.success("🎉 정답입니다!")
                else:
                    st.error(f"❌ 틀렸습니다! 정답은 '{correct_word['meaning']}' 입니다.")
                
                # Show example on the answer reveal if available
                if correct_word.get("example"):
                    st.info(f"💡 **예문**: {correct_word['example']}")
                    
                # Action Buttons
                col_act1, col_act2 = st.columns(2)
                with col_act1:
                    if st.button("다음 문제 ➡️", use_container_width=True, type="primary"):
                        prepare_new_question()
                        st.rerun()
                with col_act2:
                    if st.button("퀴즈 종료", use_container_width=True):
                        st.session_state.quiz_active = False
                        st.rerun()

# ----------------- TAB 4: BACKUP & RESTORE -----------------
with tab4:
    st.subheader("💾 데이터 백업 및 복원")
    st.write("단어 데이터를 내보내거나 가져옵니다. 단어장을 CSV 파일로 보관할 수 있습니다.")
    
    col_bk1, col_bk2 = st.columns(2)
    
    with col_bk1:
        st.markdown("### 📤 내보내기 (Backup)")
        st.write("현재 단어장을 CSV 파일로 다운로드합니다.")
        if len(st.session_state.words) > 0:
            df_export = pd.DataFrame(st.session_state.words)
            # Create CSV
            csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="📥 단어장 다운로드 (CSV)",
                data=csv_data,
                file_name="vocacard_backup.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("단어장이 비어 있어 내보낼 수 없습니다.")
            
    with col_bk2:
        st.markdown("### 📥 가져오기 (Restore)")
        st.write("CSV 파일을 업로드하여 단어장에 추가하거나 덮어씁니다.")
        uploaded_file = st.file_uploader("단어장 백업 파일 (CSV) 선택", type=["csv"])
        
        if uploaded_file is not None:
            try:
                # Load uploaded file
                df_import = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                
                # Check column consistency
                required_cols = {"word", "meaning"}
                if not required_cols.issubset(df_import.columns):
                    st.error("올바르지 않은 파일 형식입니다. 'word'와 'meaning' 열이 반드시 필요합니다.")
                else:
                    # Align other columns
                    if "example" not in df_import.columns:
                        df_import["example"] = ""
                    if "starred" not in df_import.columns:
                        df_import["starred"] = False
                        
                    # Handle NaN values
                    df_import = df_import.fillna("")
                    
                    st.dataframe(df_import.head(5), use_container_width=True)
                    
                    import_mode = st.radio("가져오기 방식 선택", ["기존 단어장에 추가", "기존 단어장 지우고 새로 쓰기"])
                    
                    if st.button("가져오기 적용", use_container_width=True, type="primary"):
                        new_words_list = df_import[["word", "meaning", "example", "starred"]].to_dict('records')
                        
                        # Convert types
                        for w in new_words_list:
                            w["starred"] = bool(w["starred"])
                            w["word"] = str(w["word"])
                            w["meaning"] = str(w["meaning"])
                            w["example"] = str(w["example"])
                            
                        if import_mode == "기존 단어장에 추가":
                            st.session_state.words.extend(new_words_list)
                        else:
                            st.session_state.words = new_words_list
                            
                        sync_db_state()
                        st.success(f"성공적으로 {len(new_words_list)}개의 단어를 가져왔습니다!")
                        st.rerun()
            except Exception as e:
                st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

# Sidebar details
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1546410531-bb4caa6b424d?auto=format&fit=crop&q=80&w=400", use_container_width=True)
    st.markdown("### 💡 학습 팁")
    st.info("""
    1. **3D 플래시카드**: 카드를 클릭하면 입체적으로 회전하며 뜻과 예문을 보여줍니다.
    2. **중요(⭐) 표시**: 자주 틀리거나 외우기 힘든 단어는 별표를 해두고 별도로 모아볼 수 있습니다.
    3. **정기 퀴즈**: 퀴즈 모드를 통해 내가 확실히 외웠는지 점검해 보세요.
    4. **데이터 보존**: 입력한 단어는 로컬 파일(`words.json`)에 바로 저장되어 브라우저를 닫아도 지워지지 않습니다.
    """)
    st.markdown("---")
    st.caption("Developed with ❤️ using Streamlit")
