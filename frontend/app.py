# streamlit 실행 및 login, signup 기능
import sys
from pathlib import Path
import bcrypt
import psycopg
import streamlit as st

# 프로젝트 루트 경로
ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 기존 DB 설정 재사용
from backend.database.db import DATABASE_URL, SQL_DIR

# 1. Streamlit 기본 설정
st.set_page_config(
    page_title="축구 승부 예측 서비스",
    page_icon="⚽",
    layout="wide"
)

# 기본 사이드바 숨기기
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }

        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

@st.dialog("회원가입")
def signup_dialog():

    st.subheader("새 계정 만들기")

    username = st.text_input("아이디").strip()
    nickname = st.text_input("닉네임").strip()
    password = st.text_input("비밀번호", type="password")
    password_check = st.text_input("비밀번호 확인", type="password")

    if st.button("회원가입", use_container_width=True, key="signup_submit"):

        if not username or not nickname or not password or not password_check:
            st.warning("모든 항목을 입력해주세요.")

        elif password != password_check:
            st.warning("비밀번호가 일치하지 않습니다.")

        else:
            try:
                # 1. 비밀번호 암호화
                password_hash = bcrypt.hashpw(
                    password.encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")

                # 2. 기존 회원가입 SQL 파일 읽기
                sql_path = SQL_DIR / "insert_users.sql"

                with open(sql_path, "r", encoding="utf-8") as file:
                    sql = file.read()

                # 3. DB 저장
                with psycopg.connect(DATABASE_URL) as conn:
                    conn.execute(
                        sql,
                        (username, nickname, password_hash)
                    )

                st.success("회원가입이 완료되었습니다!")

            except psycopg.errors.UniqueViolation:
                st.error("이미 사용 중인 아이디 또는 닉네임입니다.")

            except Exception as e:
                st.error(f"회원가입 오류: {e}")

# 2. 로그인 처리
def login_user(username, password):

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL을 확인해주세요.")

    # 기존 login_user.sql 파일 읽기
    sql_path = SQL_DIR / "login_user.sql"
    with open(sql_path, "r", encoding="utf-8") as file:
        sql = file.read()

    # DB 조회
    with psycopg.connect(DATABASE_URL) as conn:
        user = conn.execute(
            sql,
            (username,)
        ).fetchone()

    # 아이디가 존재하지 않는 경우
    if user is None:
        return None

    # DB에 저장된 비밀번호 해시
    password_hash = user[3]

    # 비밀번호 검증
    if bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    ):

        return {
            "user_id": str(user[0]),
            "username": user[1],
            "nickname": user[2]
        }

    return None

# 3. 로그인 상태 초기화
if "login_user" not in st.session_state:
    st.session_state.login_user = None

if "guest" not in st.session_state:
    st.session_state.guest = False

# 4. 로그인 성공 화면
if st.session_state.login_user:
    st.title("로그인 성공")
    st.success(
        f"{st.session_state.login_user['nickname']}님 환영합니다!"
    )

    if st.button("로그아웃"):
        st.session_state.login_user = None
        st.rerun()

    st.stop()

# 5. 비회원 화면
if st.session_state.guest:
    st.title("비회원으로 입장했습니다.")

    if st.button("로그인 화면으로 돌아가기"):
        st.session_state.guest = False
        st.rerun()

    st.stop()

# 6. 좌우 화면 분할
left, right = st.columns(
    [1.25, 1],
    gap="large"
)

# 7. 왼쪽 : 서비스 소개
with left:
    st.caption("YOUR CLUB. YOUR GAME.")
    st.title("경기가 끝나도,")
    st.title("우리의 축구는 계속된다.")
    st.write(
        "내 팀의 소식부터 경기 예측까지, "
        "축구의 모든 순간을 함께하세요."
    )

    st.write("")
    st.subheader("THIS IS YOUR HOME.")
    st.write("PREMIER LEAGUE")
    st.info(
        "이 영역에는 추후 축구장 이미지와 "
        "서비스 소개 콘텐츠를 추가할 예정입니다."
    )

# 8. 오른쪽 : 로그인 UI
with right:
    st.caption("KICK OFF")
    st.header("반가워요, 축구 팬!")
    st.caption("로그인하고 축구의 모든 순간을 즐겨보세요.")

    # 로그인 입력
    with st.form("login_form"):
        username = st.text_input(
            "아이디",
            placeholder="아이디를 입력하세요"
        )

        password = st.text_input(
            "비밀번호",
            type="password",
            placeholder="비밀번호를 입력하세요"
        )

        login_btn = st.form_submit_button(
            "로그인",
            use_container_width=True
        )

    # 로그인 버튼 이벤트
    if login_btn:
        if not username.strip() or not password:
            st.warning("아이디와 비밀번호를 확인해주세요.")
        else:
            try:
                user = login_user(
                    username.strip(),
                    password
                )
                if user:
                    st.session_state.login_user = user
                    st.rerun()
                else:
                    st.error(
                        "아이디 또는 비밀번호가 올바르지 않습니다."
                    )
            except Exception as e:
                st.error(f"로그인 처리 오류: {e}")

    # 9. 비회원 / 회원가입 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "비회원 로그인",
            use_container_width=True
        ):
            st.session_state.guest = True
            st.rerun()

    with col2:
        if st.button(
            "회원가입",
            use_container_width=True
        ):
            signup_dialog()

    # 10. 기타 안내
    st.write("")
    st.caption("아이디 찾기  |  비밀번호 찾기")
    st.caption(
        "※ 아이디 및 비밀번호 찾기는 추후 구현 예정입니다."
    )
