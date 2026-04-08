import streamlit as st
import pandas as pd
import re

# Load data
df = pd.read_csv("demoartists.csv")

# Clean columns
df.columns = df.columns.str.strip().str.lower()

# Clean price column
df['price'] = (
    df['price']
    .astype(str)
    .str.replace(r"[^\d.]", "", regex=True)
)
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df.dropna(subset=['price'])

st.set_page_config(page_title="Artist Search Tool", layout="wide")

st.title("🎤 Artist Search Tool")

# -------- SESSION STATE FOR SHORTLIST -------- #
if "shortlist" not in st.session_state:
    st.session_state.shortlist = []

# -------- AI SEARCH -------- #

st.subheader("🧠 Smart Search")
query = st.text_input("Type requirement (e.g. Bollywood singer under 1 lakh for wedding)")

ai_budget = None
ai_genre = None
ai_perf = None

if query:
    query_lower = query.lower()

    # Extract budget
    match = re.search(r'(\d+)', query_lower)
    if match:
        ai_budget = int(match.group(1)) * 1000 if int(match.group(1)) < 1000 else int(match.group(1))

    # Match genre
    for g in df['genre'].dropna().unique():
        if g.lower() in query_lower:
            ai_genre = g

    # Match performance type
    for p in df['performance_type'].dropna().unique():
        if p.lower() in query_lower:
            ai_perf = p

# -------- FILTERS -------- #

budget = st.slider(
    "Max Budget",
    0,
    int(df['price'].max()),
    int(df['price'].max()) if not ai_budget else min(ai_budget, int(df['price'].max()))
)

genre = st.multiselect(
    "Genre",
    sorted(df['genre'].dropna().unique()),
    default=[ai_genre] if ai_genre else None
)

performance_type = st.multiselect(
    "Performance Type",
    sorted(df['performance_type'].dropna().unique()),
    default=[ai_perf] if ai_perf else None
)

performer_type = st.multiselect(
    "Performer Type",
    sorted(df['performer_type'].dropna().unique())
)

name_search = st.text_input("Search Artist Name")

# -------- FILTER LOGIC -------- #

filtered = df[df['price'] <= budget]

if genre:
    filtered = filtered[filtered['genre'].isin(genre)]

if performance_type:
    filtered = filtered[filtered['performance_type'].isin(performance_type)]

if performer_type:
    filtered = filtered[filtered['performer_type'].isin(performer_type)]

if name_search:
    filtered = filtered[
        filtered['name'].str.contains(name_search, case=False, na=False)
    ]

# -------- RESULTS -------- #

st.write(f"### Results ({len(filtered)})")

for i, row in filtered.iterrows():
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(f"""
        ---
        ### 🎤 {row['name']}
        **💰 Price:** ₹{int(row['price'])}  
        **🎶 Genre:** {row['genre']}  
        **🎭 Performance Type:** {row['performance_type']}  
        **👤 Performer Type:** {row['performer_type']}  
        **🔗 Profile:** {row['profile']}
        """)

    with col2:
        if st.button("➕ Add", key=i):
            st.session_state.shortlist.append(row)

# -------- SHORTLIST -------- #

st.sidebar.title("⭐ Shortlisted Artists")

if st.session_state.shortlist:
    shortlist_df = pd.DataFrame(st.session_state.shortlist)

    st.sidebar.write(shortlist_df[['name', 'price']])

    csv = shortlist_df.to_csv(index=False).encode('utf-8')

    st.sidebar.download_button(
        "📥 Download Shortlist",
        csv,
        "shortlist.csv",
        "text/csv"
    )
else:
    st.sidebar.write("No artists shortlisted yet.")