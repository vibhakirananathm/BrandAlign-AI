

import streamlit as st
import sqlite3
import hashlib
import secrets
# Database connection
conn = sqlite3.connect("brandalign.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS brand_guidelines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT,
    approved_terms TEXT,
    prohibited_terms TEXT,
    brand_tone TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password_hash TEXT,
   salt TEXT,
role TEXT DEFAULT 'Brand Owner'
)
""")
conn.commit()
# Add user ownership to existing brand database
columns = [
    row[1] for row in cursor.execute(
        "PRAGMA table_info(brand_guidelines)"
    ).fetchall()
]

user_columns = [
    row[1] for row in cursor.execute(
        "PRAGMA table_info(users)"
    ).fetchall()
]

if "role" not in user_columns:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Brand Owner'"
    )

conn.commit()

conn.commit()
saved = cursor.execute(
    "SELECT brand_name, approved_terms, prohibited_terms, brand_tone "
    "FROM brand_guidelines ORDER BY id DESC LIMIT 1"
).fetchone()

st.set_page_config(
    page_title="BrandAlign AI",
    page_icon="🛡️",
    layout="wide"
)

# PASSWORD SECURITY
def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("BrandAlign AI - Secure Login")

    choice = st.radio("Choose an option", ["Login", "Register"])
    role = st.selectbox(
    "Select your role",
    ["Brand Owner", "Reviewer", "Admin"]
)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Create Account"):
            if email and password:
                salt = secrets.token_hex(16)
                password_hash = hash_password(password, salt)

                try:
                    cursor.execute(
                        "INSERT INTO users (email, password_hash, salt, role) VALUES (?, ?, ?, ?)",
                       (email.lower(), password_hash, salt, role)
                    )
                    conn.commit()
                    st.success("Account created! Now select Login.")
                except sqlite3.IntegrityError:
                    st.error("This email is already registered.")
            else:
                st.warning("Enter email and password.")

    else:
        if st.button("Login"):
            user = cursor.execute(
                "SELECT id, password_hash, salt, role FROM users WHERE email = ?",
                (email.lower(),)
            ).fetchone()

            if user and hash_password(password, user[1]) == user[0]:
                st.session_state["authenticated"] = True
                st.session_state["user_role"] = user[3]
                st.rerun()
            else:
                st.error("Invalid email or password.")

    st.stop()
    

st.title("🛡️ BrandAlign AI")
st.subheader("Intelligent Brand Identity Protection")

st.write(
    "Register your brand guidelines before checking "
    "your marketing content."
)

st.divider()

st.header("1. Brand Guidelines")

brand_name = st.text_input(
    "Company / Brand Name",
    value=saved[0] if saved else "",
    placeholder="NAYAVI"
)

approved_terms = st.text_area(
    "Approved Terms",
    value=saved[1] if saved else "",
    placeholder="Enter approved words, separated by commas"
)

prohibited_terms = st.text_area(
    "Prohibited Terms",
    value=saved[2] if saved else "",
    placeholder="Enter prohibited words, separated by commas"
)

brand_tone = st.selectbox(
    "Approved Brand Tone",
    ["Professional", "Friendly", "Formal", "Casual"],
    index=["Professional", "Friendly", "Formal", "Casual"].index(saved[3])
    if saved and saved[3] in ["Professional", "Friendly", "Formal", "Casual"]
    else 0
)

if st.button("Save Brand Guidelines"):
    if brand_name.strip():
        st.session_state["brand_name"] = brand_name
        st.session_state["approved_terms"] = approved_terms
        st.session_state["prohibited_terms"] = prohibited_terms
        st.session_state["brand_tone"] = brand_tone
        st.session_state["brand_tone"] = brand_tone

        st.success("Brand guidelines saved successfully!")
    else:
        st.warning("Please enter your brand name.")

st.divider()

st.header("2. Content Submission")

content = st.text_area(
    "Enter marketing content to check",
    placeholder="Paste your advertisement, caption or marketing text here..."
)

st.info("Your brand guidelines will be used to evaluate submitted content.")

st.divider()
st.header("3. Brand Compliance Check")

if st.button("Check Compliance"):
    if not content.strip():
        st.warning("Please enter marketing content.")
    else:
        prohibited = [
            word.strip().lower()
            for word in st.session_state.get("prohibited_terms", "").split(",")
            if word.strip()
        ]

        found_issues = [
            word for word in prohibited
            if word in content.lower()
        ]

        if found_issues:
            st.error("Compliance issues detected!")
            st.write("Prohibited terms found:")

            for word in found_issues:
                st.write(f"- {word}")

                if word == "100% success":
                    st.info("Suggestion: Use 'Designed to deliver quality results'.")
                elif word == "cheapest ever":
                    st.info("Suggestion: Use 'Affordable and value-focused'.")
                else:
                    st.info("Suggestion: Review this claim and use verified wording.")
        else:
            st.success("No prohibited terms detected!")

            st.divider()
st.header("4. Human Review and Approval")

decision = st.radio(
    "Review the submitted content:",
    ["Approve Content", "Reject Content", "Request Changes"]
)

if st.button("Submit Final Decision"):
    if decision == "Approve Content":
        st.success("Content approved by the reviewer!")
    elif decision == "Reject Content":
        st.error("Content rejected by the reviewer.")
    else:
        st.warning("Changes requested. Please revise the content.")




