import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(
    page_title="YCC 도서 공유",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #f5f5f5;
    width: 220px !important;
}

.stButton > button {
    border-radius: 0px;
    border: none;
    background-color: #d9d9d9;
    color: black;
    padding: 0.5rem 1rem;
    width: 100%;
    font-size: 17px;
}

.block-container {
    padding-top: 4rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------- 데이터 ----------------
books_df = pd.read_csv("books.csv")
books = books_df.to_dict(orient="records")

problems_df = pd.read_csv("problems.csv")
problems = problems_df.to_dict(orient="records")

# ---------------- 세션 상태 ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

if "selected_problem" not in st.session_state:
    st.session_state.selected_problem = None

# ---------------- 사이드바 ----------------
with st.sidebar:

    st.markdown("## 메뉴")

    if st.button("도서", use_container_width=True):
        st.session_state.page = "books"

    if st.button("문제집", use_container_width=True):
        st.session_state.page = "problems"

# =====================================================
# 홈
# =====================================================
if st.session_state.page == "home":

    st.markdown(
        """
        # 📚 YCC 도서 공유 시스템

        ### 선후배가 함께 만드는 도서 공유 플랫폼

        책과 문제집을 자유롭게 공유하고  
        필요한 자료를 쉽게 대여해보세요.
        """
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("## 📖 도서")

        st.write(
            "다양한 분야의 도서를 검색하고 대여할 수 있습니다."
        )

        if st.button(
            "도서 보러가기",
            use_container_width=True
        ):

            st.session_state.page = "books"

            st.rerun()

    with col2:

        st.markdown("## 📘 문제집")

        st.write(
            "과목별 문제집을 검색하고 대여할 수 있습니다."
        )

        if st.button(
            "문제집 보러가기",
            use_container_width=True
        ):

            st.session_state.page = "problems"

            st.rerun()

    st.divider()

    st.info(
        "💡 원하는 자료가 없다면 선배들에게 기증받아 함께 공유해보세요!"
    )

# =====================================================
# 도서 목록
# =====================================================
elif st.session_state.page == "books":

    st.title("📚 도서 목록")

    search = st.text_input("🔍 검색")

    sort_option = st.selectbox(
        "정렬",
        options=["기본", "가나다순", "최신순"],
        index=0
    )

    filtered_books = books.copy()

    # 검색
    if search:

        filtered_books = [
            b for b in filtered_books
            if search.lower() in b["title"].lower()
            or search.lower() in b["info"].lower()
        ]

    # 정렬
    if sort_option == "가나다순":

        filtered_books = sorted(
            filtered_books,
            key=lambda x: x["title"]
        )

    elif sort_option == "최신순":

        filtered_books = sorted(
            filtered_books,
            key=lambda x: x["title"],
            reverse=True
        )

    # 검색 결과 없음
    if len(filtered_books) == 0:

        st.info("📚 해당 도서를 찾을 수 없습니다.")

    else:

        cols = st.columns(4)

        for i, book in enumerate(filtered_books):

            with cols[i % 4]:

                st.image(book["image"])

                st.caption(f"👤 {book['info']}")

                if st.button(
                    book["title"],
                    key=f"book{i}"
                ):

                    st.session_state.selected_book = book
                    st.session_state.page = "book_detail"

                    st.rerun()

# =====================================================
# 도서 상세 페이지
# =====================================================
elif st.session_state.page == "book_detail":

    book = st.session_state.selected_book

    if st.button("← 목록으로"):

        st.session_state.page = "books"

        st.rerun()

    col1, col2 = st.columns([1,2])

    with col1:
        st.image(book["image"], width=300)

    with col2:

        st.title(book["title"])

        st.write(f"✍ 저자: {book['writer']}")
        st.write(f"📂 계열: {book['category']}")
        st.write(f"📖 설명: {book['desc']}")

        if book["status"] == "available":

            renter = st.text_input(
                "반번호 이름 입력",
                key="book_renter"
            )

            if st.button("대여하기"):

                if renter:

                    for b in books:

                        if b["title"] == book["title"]:
                            b["status"] = "rented"

                    pd.DataFrame(books).to_csv(
                        "books.csv",
                        index=False
                    )

                    rental = {
                        "name": renter,
                        "item": book["title"],
                        "time": datetime.now()
                    }

                    try:

                        rentals = pd.read_csv(
                            "rentals.csv"
                        )

                    except:

                        rentals = pd.DataFrame(
                            columns=[
                                "name",
                                "item",
                                "time"
                            ]
                        )

                    rentals.loc[len(rentals)] = rental

                    rentals.to_csv(
                        "rentals.csv",
                        index=False
                    )

                    st.success(
                        f"✅ {renter}님, 대여가 완료되었습니다!"
                    )

                    time.sleep(3)

                    st.rerun()

        else:
            st.error("🚫 대여 불가")

# =====================================================
# 문제집 목록
# =====================================================
elif st.session_state.page == "problems":

    st.title("📘 문제집 목록")

    subject_filter = st.selectbox(
        "과목 선택",
        ["전체"] + list(problems_df["subject"].unique())
    )

    search = st.text_input(
        "🔍 검색",
        key="problem_search"
    )

    sort_option = st.selectbox(
        "정렬",
        options=["기본", "가나다순", "최신순"],
        index=0,
        key="problem_sort"
    )

    filtered = problems.copy()

    # 과목 필터
    if subject_filter != "전체":

        filtered = [
            p for p in filtered
            if p["subject"] == subject_filter
        ]

    # 검색
    if search:

        filtered = [
            p for p in filtered
            if search.lower() in p["type"].lower()
            or search.lower() in p["subject"].lower()
        ]

    # 정렬
    if sort_option == "가나다순":

        filtered = sorted(
            filtered,
            key=lambda x: x["type"]
        )

    elif sort_option == "최신순":

        filtered = sorted(
            filtered,
            key=lambda x: x["type"],
            reverse=True
        )

    # 검색 결과 없음
    if len(filtered) == 0:

        st.info("📘 해당 문제집을 찾을 수 없습니다.")

    else:

        cols = st.columns(4)

        for i, p in enumerate(filtered):

            with cols[i % 4]:

                st.image(p["image"])

                st.caption(f"📚 {p['subject']}")

                if st.button(
                    p["type"],
                    key=f"problem{i}"
                ):

                    st.session_state.selected_problem = p
                    st.session_state.page = "problem_detail"

                    st.rerun()

# =====================================================
# 문제집 상세 페이지
# =====================================================
elif st.session_state.page == "problem_detail":

    p = st.session_state.selected_problem

    if st.button("← 목록으로"):

        st.session_state.page = "problems"

        st.rerun()

    col1, col2 = st.columns([1,2])

    with col1:
        st.image(p["image"], width=300)

    with col2:

        st.title(p["type"])

        st.write(f"📚 과목: {p['subject']}")
        st.write(f"📅 개정년도: {p['year']}")

        if p["status"] == "available":

            renter = st.text_input(
                "반번호 이름 입력",
                key="problem_renter"
            )

            if st.button(
                "대여하기",
                key="rent_problem"
            ):

                if renter:

                    for item in problems:

                        if item["type"] == p["type"]:
                            item["status"] = "rented"

                    pd.DataFrame(problems).to_csv(
                        "problems.csv",
                        index=False
                    )

                    rental = {
                        "name": renter,
                        "item": p["type"],
                        "time": datetime.now()
                    }

                    try:

                        rentals = pd.read_csv(
                            "rentals.csv"
                        )

                    except:

                        rentals = pd.DataFrame(
                            columns=[
                                "name",
                                "item",
                                "time"
                            ]
                        )

                    rentals.loc[len(rentals)] = rental

                    rentals.to_csv(
                        "rentals.csv",
                        index=False
                    )

                    st.success(
                        f"✅ {renter}님, 대여가 완료되었습니다!"
                    )

                    time.sleep(3)

                    st.rerun()

        else:
            st.error("🚫 대여 불가")
