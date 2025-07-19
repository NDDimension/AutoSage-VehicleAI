# --- AutoSage App Initialization ---

# 1. Load environment variables
from dotenv import load_dotenv

load_dotenv()

# 2. Import required libraries
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# 3. Configure Google Generative AI with API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# 4. Getting Gemini Response
def get_gemini_response(input_prompt, image):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input_prompt, image[0]])
    return response.text


# 5. Function to read the image and set the image format for Gemini Pro model Input
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No image file uploaded")


# 6. Input prompt for Gemini
input_prompt = """
You are an automobile expert tasked with providing a detailed overview of any vehicle.
The information should be presented in a structured format as follows:

Brand: Name of the vehicle brand.  
Model: Specific model of the vehicle.  
Launch Year: Since when the vehicle is available in the market.  
Key Features: Include the engine capacity, type (e.g., scooter, motorcycle, sedan, SUV), and top 3 special features (e.g., ABS, digital display, storage capacity, safety features).  
Mileage: Provide the average mileage in km/l (kilometers per liter).  
Average Price in INR: Mention the price range of the vehicle model in Indian Rupees.  
Other Details: Include information on maintenance costs, additional benefits, and any unique selling points.  
Approximate Resale Value: Estimate the resale value of the vehicle after 10 years in Indian Rupees.
"""


# 7. Helper functions for formatting summary
def extract_line(text, keyword):
    for line in text.split("\n"):
        if keyword.lower() in line.lower():
            return "- " + line.strip()
    return "- ❓ Info not found"


def format_vehicle_summary(raw_text):
    return f"""
### 🚘 **Vehicle Overview**

---

#### 🔷 **Basic Information**
{extract_line(raw_text, "Brand")}
{extract_line(raw_text, "Model")}
{extract_line(raw_text, "Launch Year")}

---

#### ⚙️ **Key Features**
{extract_line(raw_text, "Engine Capacity")}
{extract_line(raw_text, "Type")}
{extract_line(raw_text, "Top 3 Special Features")}

---

#### ⛽ **Mileage**
{extract_line(raw_text, "Mileage")}

---

#### 💰 **Average Price (INR)**
{extract_line(raw_text, "Average Price")}

---

#### 🔧 **Other Details**
{extract_line(raw_text, "Maintenance Costs")}
{extract_line(raw_text, "Additional Benefits")}
{extract_line(raw_text, "Unique Selling Points")}

---

#### 🔁 **Approximate Resale Value**
{extract_line(raw_text, "Resale")}
"""


# --- Streamlit App UI ---

st.set_page_config(page_title="AutoSage - Vehicle Intelligence", layout="centered")

st.markdown(
    "<h1 style='text-align: center; color: #4A90E2;'>🚗 AutoSage App</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center;'>Upload a vehicle image to get detailed specifications, features, and insights.</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

# 🔁 Session State
if "raw_response" not in st.session_state:
    st.session_state.raw_response = None

if "image_data" not in st.session_state:
    st.session_state.image_data = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 📤 File Upload Section
uploaded_file = st.file_uploader(
    "Upload an image of the vehicle", type=["jpg", "jpeg", "png"]
)

# 📸 Image Display
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Vehicle Image", use_container_width=True)

    # 🔍 Tell me button
    if st.button("🔍 Tell me about this vehicle"):
        try:
            image_data = input_image_setup(uploaded_file)
            st.session_state.image_data = image_data  # 🔑 Store image for chat use
            response = get_gemini_response(input_prompt, image_data)
            st.session_state.raw_response = response

            st.markdown("### 📝 Raw AI Response:")
            st.success(response)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # 📄 Summarize button
    if st.session_state.raw_response and st.button("📄 Summarize"):
        formatted = format_vehicle_summary(st.session_state.raw_response)
        st.markdown("---")
        st.markdown("### ✅ Summarized Vehicle Overview:")
        st.markdown(formatted, unsafe_allow_html=True)

    # 💬 Chat section
    if st.session_state.raw_response:
        st.markdown("---")
        st.markdown("### 💬 Ask More About the Vehicle")

        user_input = st.chat_input("Ask anything about this vehicle...")

        if user_input:
            if st.session_state.image_data:
                context = (
                    input_prompt + "\n\nVehicle Info:\n" + st.session_state.raw_response
                )
                followup_prompt = f"{context}\n\nUser: {user_input}\nAutoSage:"
                try:
                    ai_reply = get_gemini_response(
                        followup_prompt, st.session_state.image_data
                    )
                    st.session_state.chat_history.append(("You", user_input))
                    st.session_state.chat_history.append(("AutoSage", ai_reply))
                except Exception as e:
                    st.error(f"❌ Chat error: {str(e)}")
            else:
                st.warning(
                    "Please click 'Tell me about this vehicle' first to initialize data."
                )

        # 💬 Render chat history
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)

else:
    st.info("📌 Please upload an image to begin.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: var(--dark); opacity: 0.7; margin-top: 2rem;">
        <p><b>Made with ❤️ by Dhanraj Sharma</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)
