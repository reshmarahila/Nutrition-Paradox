import streamlit as st
import pandas as pd
import pymysql
from streamlit_option_menu import option_menu
import queue
import pyttsx3
import matplotlib.pyplot as plt
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# --- MySQL Connection ---
connection = pymysql.connect(
    host="localhost",
    user="rahila",
    password="12345",
    database="nutrition"
)
cursor = connection.cursor()

# --- Streamlit Page Setup ---
st.set_page_config(layout="wide")
st.markdown("<h3 style ='text-align: center; color: #8888BE;'>🌍🗺️ Nutrition Paradox: A Global View on Obesity and Malnutrition 💫</h3>", unsafe_allow_html=True)
st.divider()

# --- Sidebar Menu ---
with st.sidebar:
    selected = option_menu(
        menu_title='Obesity and Malnutrition',
        options=["Obesity", "Malnutrition", "Combined", "AI Assistant", "Overcome"],
        icons=["star", "star", "star", "robot", "check-circle"],
        menu_icon="map",
        default_index=0
    )

# --- Query Handling ---
option = []
q1 = ""

# --- Obesity Section ---
if selected == "Obesity":
    st.subheader("🍩 Obesity Table")
    option = st.selectbox("Select your query", [
        '1.Top regions with the highest average obesity levels in the most recent year(2022)',
        '2.Top 5 countries with highest obesity estimates',
        '3.Obesity trend in India over the years(Mean_estimate)',
        '4.Average obesity by gender',
        '5.Country count by obesity level category and age group'
    ])

    if option.startswith('1.'):
        q1 = """SELECT Region, AVG(Mean_Estimate) AS Avg_Obesity FROM obesity WHERE Year = 2022 GROUP BY Region ORDER BY Avg_Obesity DESC LIMIT 4;"""
    elif option.startswith('2.'):
        q1 = """SELECT Country, MAX(Mean_Estimate) AS Max_Obesity FROM obesity GROUP BY Country ORDER BY Max_Obesity DESC LIMIT 5;"""
    elif option.startswith('3.'):
        q1 = """SELECT Year, AVG(Mean_Estimate) AS Avg_Obesity FROM obesity WHERE Country = 'India' GROUP BY Year ORDER BY Year;"""
    elif option.startswith('4.'):
        q1 = """SELECT Gender, AVG(Mean_Estimate) AS Avg_Obesity FROM obesity GROUP BY Gender;"""
    elif option.startswith('5.'):
        q1 = """SELECT obesity_level, Age_Group, COUNT(DISTINCT Country) AS Country_Count FROM obesity GROUP BY obesity_level, Age_Group ORDER BY obesity_level, Age_Group;"""

# --- Malnutrition Section ---
elif selected == "Malnutrition":
    st.subheader("🧋 Malnutrition Table")
    option = st.selectbox("Select your query", [
        '1.Avg. malnutrition by age group',
        '2.Top 5 countries with highest malnutrition(mean_estimate)',
        '3.Malnutrition trend in African region over the years',
        '4.Gender-based average malnutrition',
        '5.Malnutrition level-wise (average CI_Width by age group)'
    ])

    if option.startswith('1.'):
        q1 = """SELECT Age_Group, AVG(Mean_Estimate) AS Avg_Malnutrition FROM malnutrition GROUP BY Age_Group ORDER BY Avg_Malnutrition DESC;"""
    elif option.startswith('2.'):
        q1 = """SELECT Country, MAX(Mean_Estimate) AS Max_Malnutrition FROM malnutrition GROUP BY Country ORDER BY Max_Malnutrition DESC LIMIT 5;"""
    elif option.startswith('3.'):
        q1 = """SELECT Year, AVG(Mean_Estimate) AS Avg_Malnutrition FROM malnutrition WHERE Region = 'Africa' GROUP BY Year ORDER BY Year;"""
    elif option.startswith('4.'):
        q1 = """SELECT Gender, AVG(Mean_Estimate) AS Avg_Malnutrition FROM malnutrition GROUP BY Gender;"""
    elif option.startswith('5.'):
        q1 = """SELECT malnutrition_level, Age_Group, AVG(CI_Width) AS Avg_CI_Width FROM malnutrition GROUP BY malnutrition_level, Age_Group ORDER BY malnutrition_level, Age_Group;"""

# --- Combined Section ---
elif selected == "Combined":
    st.subheader("🔗 Combined Tables")
    option = st.selectbox("Select your query", [
        '1.Obesity vs malnutrition comparison by country(any 5 countries)',
        '2.Gender-based disparity in both obesity and malnutrition',
        '3.Region-wise avg estimates side-by-side(Africa and America)',
        '4.Countries with obesity up & malnutrition down',
        '5.Age-wise trend analysis'
    ])

    if option.startswith('1.'):
        q1 = """SELECT o.Country, o.Year, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition FROM obesity o JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender AND o.Age_Group = m.Age_Group WHERE o.Country IN ('India', 'Brazil', 'Nigeria', 'United States', 'China') GROUP BY o.Country, o.Year ORDER BY o.Country, o.Year;"""
    elif option.startswith('2.'):
        q1 = """SELECT o.Gender, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition FROM obesity o JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender AND o.Age_Group = m.Age_Group GROUP BY o.Gender;"""
    elif option.startswith('3.'):
        q1 = """SELECT o.Region, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition FROM obesity o JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender AND o.Age_Group = m.Age_Group WHERE o.Region IN ('Africa', 'America') GROUP BY o.Region;"""
    elif option.startswith('4.'):
        q1 = """SELECT o.Country, MAX(o.Mean_Estimate) - MIN(o.Mean_Estimate) AS Obesity_Change, MAX(m.Mean_Estimate) - MIN(m.Mean_Estimate) AS Malnutrition_Change FROM obesity o JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender AND o.Age_Group = m.Age_Group GROUP BY o.Country HAVING Obesity_Change > 0 AND Malnutrition_Change < 0 ORDER BY Obesity_Change DESC;"""
    elif option.startswith('5.'):
        q1 = """SELECT o.Age_Group, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition FROM obesity o JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender AND o.Age_Group = m.Age_Group GROUP BY o.Age_Group ORDER BY Avg_Obesity DESC;"""

# --- Execute Query ---
if q1:
    cursor.execute(q1)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=columns)
    st.dataframe(df)

# --- AI Assistant Section ---
elif selected == "AI Assistant":
    st.subheader("🤖 AI Assistant (Flan-T5 + Chat + Multilingual + Graphs + Voice)")

    from transformers import T5Tokenizer, T5ForConditionalGeneration
    from langdetect import detect

    @st.cache_resource
    def load_model():
        tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
        model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")
        return tokenizer, model

    tokenizer, model = load_model()

    # Session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Example questions
    example_questions = [
        "Show the obesity trend in India over the years",
        "Top 5 countries with highest malnutrition",
        "Compare Africa and America on obesity and malnutrition",
        "Average obesity by gender",
        "Malnutrition trend in African region over the years",
        "Obesity levels by age group in 2022",
        "Top regions with highest obesity in 2022"     
    ]
    selected_example = st.selectbox("💡 Choose a question:", [""] + example_questions)
    default_input = selected_example if selected_example else ""
    user_input = st.text_input("Ask a question or follow-up:", value=default_input)

    if st.button("Send"):
        st.session_state.chat_history.append(("User", user_input))
        query = ""
        chart_type = None
        x_col, y_col = None, None
        user_text = user_input.lower()

        # --- Match question to SQL query ---
        if "obesity" in user_text and "trend" in user_text and "india" in user_text:
            query = """SELECT Year, AVG(Mean_Estimate) AS Avg_Obesity FROM obesity WHERE Country = 'India' GROUP BY Year ORDER BY Year;"""
            chart_type = "line"
            x_col, y_col = "Year", "Avg_Obesity"

        elif "top" in user_text and "malnutrition" in user_text and "countries" in user_text:
            query = """SELECT Country, MAX(Mean_Estimate) AS Max_Malnutrition FROM malnutrition GROUP BY Country ORDER BY Max_Malnutrition DESC LIMIT 5;"""
            chart_type = "bar"
            x_col, y_col = "Country", "Max_Malnutrition"

        elif "compare" in user_text and "africa" in user_text and "america" in user_text:
            query = """SELECT o.Region, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition
                       FROM obesity o JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender AND o.Age_Group = m.Age_Group
                       WHERE o.Region IN ('Africa', 'America') GROUP BY o.Region;"""
            chart_type = "bar"
            x_col, y_col = "Region", ["Avg_Obesity", "Avg_Malnutrition"]

        elif "average" in user_text and "obesity" in user_text and "gender" in user_text:
            query = """SELECT Gender, AVG(Mean_Estimate) AS Avg_Obesity FROM obesity GROUP BY Gender;"""
            chart_type = "bar"
            x_col, y_col = "Gender", "Avg_Obesity"

        elif "malnutrition" in user_text and "trend" in user_text and "africa" in user_text:
            query = """SELECT Year, AVG(Mean_Estimate) AS Avg_Malnutrition FROM malnutrition WHERE Region = 'Africa' GROUP BY Year ORDER BY Year;"""
            chart_type = "line"
            x_col, y_col = "Year", "Avg_Malnutrition"

        elif "obesity" in user_text and "age group" in user_text and "2022" in user_text:
            query = """SELECT Age_Group, AVG(Mean_Estimate) AS Avg_Obesity FROM obesity WHERE Year = 2022 GROUP BY Age_Group ORDER BY Avg_Obesity DESC;"""
            chart_type = "bar"
            x_col, y_col = "Age_Group", "Avg_Obesity"

        elif "gender" in user_text and "malnutrition" in user_text and "region" in user_text:
            query = """SELECT Region, Gender, AVG(Mean_Estimate) AS Avg_Malnutrition FROM malnutrition GROUP BY Region, Gender ORDER BY Region;"""
            chart_type = "bar"
            x_col, y_col = "Region", "Avg_Malnutrition"

        elif "rising obesity" in user_text and "stable malnutrition" in user_text:
            query = """SELECT o.Country FROM obesity o JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender AND o.Age_Group = m.Age_Group
                       GROUP BY o.Country HAVING MAX(o.Mean_Estimate) - MIN(o.Mean_Estimate) > 5 AND MAX(m.Mean_Estimate) - MIN(m.Mean_Estimate) < 2;"""
            chart_type = "bar"
            x_col, y_col = "Country", None

        elif "top" in user_text and "regions" in user_text and "obesity" in user_text and "2022" in user_text:
            query = """SELECT Region, AVG(Mean_Estimate) AS Avg_Obesity FROM obesity WHERE Year = 2022 GROUP BY Region ORDER BY Avg_Obesity DESC LIMIT 4;"""
            chart_type = "bar"
            x_col, y_col = "Region", "Avg_Obesity"

        elif "high obesity" in user_text and "high malnutrition" in user_text:
            query = """SELECT o.Country, AVG(o.Mean_Estimate) AS Avg_Obesity, AVG(m.Mean_Estimate) AS Avg_Malnutrition
                       FROM obesity o JOIN malnutrition m ON o.Country = m.Country AND o.Year = m.Year AND o.Gender = m.Gender AND o.Age_Group = m.Age_Group
                       GROUP BY o.Country HAVING Avg_Obesity > 25 AND Avg_Malnutrition > 20 ORDER BY Avg_Obesity DESC;"""
            chart_type = "bar"
            x_col, y_col = "Country", ["Avg_Obesity", "Avg_Malnutrition"]

        # --- Execute query if matched ---
        if query:
            cursor.execute(query)
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=columns)

            st.markdown("**📊 Data Table:**")
            st.dataframe(df)

            # --- Plot graph ---
            st.markdown("**📈 Visualization:**")
            fig, ax = plt.subplots()
            if chart_type == "line":
                ax.plot(df[x_col], df[y_col], marker='o')
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{y_col} over {x_col}")
            elif chart_type == "bar":
                if isinstance(y_col, list):
                    df.plot(x=x_col, y=y_col, kind='bar', ax=ax)
                    ax.set_title("Obesity vs Malnutrition")
                elif y_col:
                    ax.bar(df[x_col], df[y_col], color='skyblue')
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f"{y_col} by {x_col}")
                else:
                    ax.bar(df[x_col], range(len(df)), color='skyblue')
                    ax.set_xlabel(x_col)
                    ax.set_title(f"{x_col} list")
            st.pyplot(fig)

            # --- Generate explanation using Flan-T5 ---
            summary = df.to_markdown(index=False)
            prompt = f"Summarize this data in simple terms:\n{summary}"

            input_ids = tokenizer(prompt, return_tensors="pt").input_ids
            output_ids = model.generate(input_ids, max_length=512, pad_token_id=tokenizer.eos_token_id)
            reply = tokenizer.decode(output_ids[0], skip_special_tokens=True)

            # Check for empty or invalid output
            if not reply.strip() or reply.strip().count("''") > 10:
                reply = "Sorry, I couldn't generate a meaningful summary. Try rephrasing your question or checking the data."

            st.markdown(f"**🧠 AI Explanation:** {reply}")

            # --- Speak the response ---
            try:
                engine = pyttsx3.init()
                engine.say(reply)
                engine.runAndWait()
            except Exception as e:
                st.warning("Text-to-speech failed. Make sure pyttsx3 is installed.")

        else:
            fallback = "I'm not sure how to answer that yet. Try asking about obesity trends or regional comparisons."
            st.session_state.chat_history.append(("AI", fallback))
            st.warning(fallback)

    # Display chat history
    st.markdown("### 🗨️ Conversation")
    for speaker, message in st.session_state.chat_history:
        st.markdown(f"**{speaker}:** {message}")

elif selected == "Overcome":
    st.subheader("🌍 Global Strategies to Tackle the Nutritional Paradox")

    st.markdown("### 🥗 Promote Healthy, Affordable Diets")
    st.markdown("- Improve access to fruits, vegetables, and protein-rich foods.")
    st.markdown("- Subsidize nutritious food, reduce costs of staples, and discourage ultra-processed foods.")

    st.markdown("### 👶 Strengthen Maternal & Child Nutrition")
    st.markdown("- Ensure proper nutrition during the first 1,000 days of life (pregnancy → age 2).")
    st.markdown("- Expand breastfeeding, fortified foods, and school meal programs.")

    st.markdown("### ⚖️ Implement Double-Duty Policies")
    st.markdown("- Tax sugary drinks and junk food.")
    st.markdown("- Use revenue to fund nutrition education and undernutrition programs.")
    st.markdown("- Encourage food labeling to help consumers make healthier choices.")

    st.markdown("### 💸 Address Social & Economic Inequalities")
    st.markdown("- Support low-income families with food security programs.")
    st.markdown("- Invest in rural agriculture and sustainable food supply chains.")

    st.markdown("### 📚 Raise Awareness & Education")
    st.markdown("- Promote nutrition education in schools, workplaces, and communities.")
    st.markdown("- Encourage physical activity and healthy lifestyle campaigns.")

    st.markdown("### 📊 Global Monitoring & Research")
    st.markdown("- Use WHO and UN data to track nutrition trends.")
    st.markdown("- Share best practices across countries and regions.")

    st.markdown("✅ **In short:** Balanced food systems, strong policies, education, and equity-focused interventions can reduce hunger and prevent obesity.")


