"""
Streamlit Chat Interface for BookLeaf Author Support Bot.
Provides: chat bubbles, confidence visualization, escalation banners, identity sidebar.
Spec Reference: Section 9.1
"""
import streamlit as st
import requests

API_URL = "http://localhost:8000"

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="BookLeaf Author Support",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# Custom CSS — Sleek appearance per spec
# ============================================================
st.markdown("""
<style>
    .stChatMessage { border-radius: 12px; padding: 12px; margin-bottom: 8px; }
    .stChatMessage.user { background-color: #f0f2f6; border-left: 4px solid #4a90e2; }
    .stChatMessage.assistant { background-color: #e8f4f8; border-left: 4px solid #50c878; }
    .escalation-banner {
        background-color: #ffebee;
        border-left: 4px solid #e53935;
        padding: 10px;
        border-radius: 8px;
        color: #c62828;
        font-weight: 600;
    }
    .confidence-high { color: #2e7d32; font-weight: bold; }
    .confidence-low  { color: #c62828; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# Header
# ============================================================
st.title("📚 BookLeaf Author Support")
st.caption("Ask about your book status, royalties, author copy, or add-on services")

# ============================================================
# Sidebar — Identity Inputs
# ============================================================
with st.sidebar:
    st.header("🔐 Your Details")
    st.caption("Fill in your email or phone so we can look up your specific book status.")

    user_email = st.text_input(
        "Registered Email",
        placeholder="sara.johnson@xyz.com",
        help="The email you used when registering with BookLeaf",
    )
    user_phone = st.text_input(
        "WhatsApp / Phone",
        placeholder="+91 9876543210",
        help="Your registered phone number with country code",
    )
    user_name = st.text_input(
        "Dashboard Name",
        placeholder="Sara J.",
        help="Your name as it appears on the dashboard",
    )
    user_instagram = st.text_input(
        "Instagram Handle",
        placeholder="@sarapoetry23",
        help="Your Instagram handle if you contacted us from there",
    )

    st.divider()
    st.markdown("**Privacy Note:** Your details are only used to retrieve your book status.")

# ============================================================
# Chat State Initialization
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ============================================================
# Render Chat History
# ============================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("meta"):
            meta = msg["meta"]
            cols = st.columns([1, 1, 1])

            with cols[0]:
                conf = meta.get("confidence", 0)
                color_class = "confidence-high" if conf >= 0.8 else "confidence-low"
                st.markdown(
                    f"<span class='{color_class}'>Confidence: {conf:.0%}</span>",
                    unsafe_allow_html=True,
                )

            with cols[1]:
                if meta.get("escalated"):
                    st.markdown(
                        "<span class='escalation-banner'>🚨 Escalated to Human</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.caption(f"Intent: `{meta.get('intent', 'unknown')}`")

            with cols[2]:
                if meta.get("author_found"):
                    st.caption("✅ Author matched")
                elif not meta.get("escalated"):
                    st.caption("❓ New author")

# ============================================================
# Chat Input Handler
# ============================================================
if prompt := st.chat_input("Ask about your book, royalties, or publishing status..."):
    # Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Call backend API and render assistant response
    with st.chat_message("assistant"):
        with st.spinner("Looking up your information..."):
            try:
                payload = {
                    "channel": "web",
                    "message": prompt,
                    "user_email": user_email if user_email else None,
                    "user_phone": user_phone if user_phone else None,
                    "user_name": user_name if user_name else None,
                    "user_instagram": user_instagram if user_instagram else None,
                }

                res = requests.post(f"{API_URL}/chat", json=payload, timeout=30)
                data = res.json()

                response_text = data.get("response", "Sorry, something went wrong.")
                st.write(response_text)

                meta = {
                    "confidence": data.get("confidence", 0),
                    "intent": data.get("intent", "unknown"),
                    "escalated": data.get("escalated", False),
                    "author_found": data.get("author_found", False),
                }

                # Render confidence badge + escalation status + author match
                cols = st.columns([1, 1, 1])
                with cols[0]:
                    conf = meta["confidence"]
                    color_class = "confidence-high" if conf >= 0.8 else "confidence-low"
                    st.markdown(
                        f"<span class='{color_class}'>Confidence: {conf:.0%}</span>",
                        unsafe_allow_html=True,
                    )

                with cols[1]:
                    if meta["escalated"]:
                        st.markdown(
                            "<span class='escalation-banner'>🚨 Escalated to Human</span>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.caption(f"Intent: `{meta['intent']}`")

                with cols[2]:
                    if meta["author_found"]:
                        st.caption("✅ Author matched")
                    elif not meta["escalated"]:
                        st.caption("❓ New author")

                # Persist message with metadata for history rendering
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "meta": meta,
                })

            except requests.exceptions.ConnectionError:
                err = "Cannot connect to the backend. Make sure it is running on port 8000."
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})

            except Exception as e:
                err = f"An error occurred: {str(e)}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
