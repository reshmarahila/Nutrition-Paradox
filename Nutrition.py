import streamlit as st
import pandas as pd
import pymysql
from streamlit_option_menu import option_menu

connection = pymysql.connect(

                            host = "localhost", # IP address of your server
                            user = "rahila",
                            password = "12345",
                            database = "nutrition"
                           
                    )
cursor = connection.cursor()

st.set_page_config(layout="wide")
st.markdown("<h3 style ='text-align: centre; color: #8888BE;'>🌍🗺️ Nutrition Paradox: A Global View on Obesity and Malnutrition 💫</h1>", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    selected = option_menu(
        menu_title="Obesity and Malnutrition",
        options=["Obesity", "Malnutrition", "Combined"],
        icons = ["star", "star", "star"],
        menu_icon= "map",
        default_index=0              
)

option=[]
q1 = []

if selected == "Obesity":
    st.subheader("🍩 Obesity Table")
    option = st.selectbox(
        "Select your query", [
            '1.Top regions with the highest average obesity levels in the most recent year(2022)',
            '2.Top 5 countries with highest obesity estimates',
            '3.Obesity trend in India over the years(Mean_estimate)',
            '4.Average obesity by gender',
            '5.Country count by obesity level category and age group',
            '6.Top 5 countries least reliable countries(with highest CI_Width) and Top 5 most consistent countries (smallest average CI_Width)',
            '7.Average obesity by age group',
            '8.Top 10 Countries with consistent low obesity (low average + low CI)over the years',
            '9.Countries where female obesity exceeds male by large margin (same year)',
            '10.Global average obesity percentage per year'
        ])

    if option == '1.Top regions with the highest average obesity levels in the most recent year(2022)':
        q1 = """
        SELECT Region, AVG(Mean_Estimate) AS Avg_Obesity
        FROM obesity
        WHERE Year = 2022
        GROUP BY Region
        ORDER BY Avg_Obesity DESC
        LIMIT 4;
        """

    elif option == '2.Top 5 countries with highest obesity estimates':
        q1 = """
        SELECT Country, MAX(Mean_Estimate) AS Max_Obesity
        FROM obesity
        GROUP BY Country
        ORDER BY Max_Obesity DESC
        LIMIT 5;
        """

    elif option == '3.Obesity trend in India over the years(Mean_estimate)':
        q1 = """
       SELECT Year, AVG(Mean_Estimate) AS Avg_Obesity
        FROM obesity
        WHERE Country = 'India'
        GROUP BY Year
        ORDER BY Year;
        """

    elif option == '4.Average obesity by gender':
        q1 = """
        SELECT Gender, AVG(Mean_Estimate) AS Avg_Obesity
        FROM obesity
        GROUP BY Gender;
        """

    elif option == '5.Country count by obesity level category and age group':
        q1 = """
        SELECT obesity_level, Age_Group, COUNT(DISTINCT Country) AS Country_Count
        FROM obesity
        GROUP BY obesity_level, Age_Group
        ORDER BY obesity_level, Age_Group;
        """

    elif option == '6.Top 5 countries least reliable countries(with highest CI_Width) and Top 5 most consistent countries (smallest average CI_Width)':
        q1 = """
        SELECT Country, AVG(CI_Width) AS Avg_CI_Width
        FROM obesity
        GROUP BY Country
        ORDER BY Avg_CI_Width DESC
        LIMIT 5;
        """

    elif option == '7.Average obesity by age group':
        q1 = """
        SELECT Age_Group, AVG(Mean_Estimate) AS Avg_Obesity
        FROM obesity
        GROUP BY Age_Group
        ORDER BY Avg_Obesity DESC;
        """

    elif option == '8.Top 10 Countries with consistent low obesity (low average + low CI)over the years':
        q1 = """
        SELECT Country, AVG(Mean_Estimate) AS Avg_Obesity, AVG(CI_Width) AS Avg_CI_Width
        FROM obesity
        GROUP BY Country
        HAVING Avg_Obesity < 25 AND Avg_CI_Width < 5
        ORDER BY Avg_Obesity ASC, Avg_CI_Width ASC
        LIMIT 10; 
        """

    elif option == '9.Countries where female obesity exceeds male by large margin (same year)':
        q1 = """
        SELECT o1.Country, o1.Year,
       o1.Mean_Estimate AS Female_Obesity,
       o2.Mean_Estimate AS Male_Obesity,
       (o1.Mean_Estimate - o2.Mean_Estimate) AS Difference
        FROM obesity o1
        JOIN obesity o2
        ON o1.Country = o2.Country AND o1.Year = o2.Year
        WHERE o1.Gender = 'Female' AND o2.Gender = 'Male'
        AND (o1.Mean_Estimate - o2.Mean_Estimate) > 5
        ORDER BY Difference DESC;
        """

    elif option == '10.Global average obesity percentage per year':
        q1 = """
        SELECT Year, AVG(Mean_Estimate) AS Global_Avg_Obesity
        FROM obesity
        GROUP BY Year
        ORDER BY Year;
        """


    if q1:
        cursor.execute(q1)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(df)

elif selected == "Malnutrition":
    st.subheader("🧋 Malnutrition Table")
    option = st.selectbox(
        "Select your query", [
            '1.Avg. malnutrition by age group',
            '2.Top 5 countries with highest malnutrition(mean_estimate)',
            '3.Malnutrition trend in African region over the years',
            '4.Gender-based average malnutrition',
            '5.Malnutrition level-wise (average CI_Width by age group)',
            '6.Yearly malnutrition change in specific countries(India, Nigeria, Brazil)',
            '7.Regions with lowest malnutrition average',
            '8.Countries with increasing malnutrition',
            '9.Min/Max malnutrition levels year-wise comparison',
            '10.High CI_Width flags for monitoring(CI_width > 5)'
        ])

    if option == '1.Avg. malnutrition by age group':
        q1 = """
        SELECT Age_Group, AVG(Mean_Estimate) AS Avg_Malnutrition
        FROM malnutrition
        GROUP BY Age_Group
        ORDER BY Avg_Malnutrition DESC;
        """

    elif option == '2.Top 5 countries with highest malnutrition(mean_estimate)':
        q1 = """
        SELECT Country, MAX(Mean_Estimate) AS Max_Malnutrition
        FROM malnutrition
        GROUP BY Country
        ORDER BY Max_Malnutrition DESC
        LIMIT 5;
        """

    elif option == '3.Malnutrition trend in African region over the years':
        q1 = """
        SELECT Year, AVG(Mean_Estimate) AS Avg_Malnutrition
        FROM malnutrition
        WHERE Region = 'Africa'
        GROUP BY Year
        ORDER BY Year;
        """

    elif option == '4.Gender-based average malnutrition':
        q1 = """
        SELECT Gender, AVG(Mean_Estimate) AS Avg_Malnutrition
        FROM malnutrition
        GROUP BY Gender;
        """

    elif option == '5.Malnutrition level-wise (average CI_Width by age group)':
        q1 = """
        SELECT malnutrition_level, Age_Group, AVG(CI_Width) AS Avg_CI_Width
        FROM malnutrition
        GROUP BY malnutrition_level, Age_Group
        ORDER BY malnutrition_level, Age_Group;
        """

    elif option == '6.Yearly malnutrition change in specific countries(India, Nigeria, Brazil)':
        q1 = """
        SELECT Country, Year, AVG(Mean_Estimate) AS Avg_Malnutrition
        FROM malnutrition
        WHERE Country IN ('India', 'Nigeria', 'Brazil')
        GROUP BY Country, Year
        ORDER BY Country, Year;
        """

    elif option == '7.Regions with lowest malnutrition average':
        q1 = """
        SELECT Region, AVG(Mean_Estimate) AS Avg_Malnutrition
        FROM malnutrition
        GROUP BY Region
        ORDER BY Avg_Malnutrition ASC
        LIMIT 4;
        """

    elif option == '8.Countries with increasing malnutrition':
        q1 = """
        SELECT Country,
        MIN(Mean_Estimate) AS Min_Estimate,
        MAX(Mean_Estimate) AS Max_Estimate,
        (MAX(Mean_Estimate) - MIN(Mean_Estimate)) AS Increase
        FROM malnutrition
        GROUP BY Country
        HAVING Increase > 0
        ORDER BY Increase DESC;
        """

    elif option == '9.Min/Max malnutrition levels year-wise comparison':
        q1 = """
        SELECT Year,
        MIN(Mean_Estimate) AS Min_Malnutrition,
        MAX(Mean_Estimate) AS Max_Malnutrition
        FROM malnutrition
        GROUP BY Year
        ORDER BY Year;
        """

    elif option == '10.High CI_Width flags for monitoring(CI_width > 5)':
        q1 = """
        SELECT Country, Year, Gender, Age_Group, CI_Width, Mean_Estimate
        FROM malnutrition
        WHERE CI_Width > 5
        ORDER BY CI_Width DESC;
        """


    if q1:
        cursor.execute(q1)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(df)

elif selected == "Combined":
    st.subheader("🔗 Combined Tables")
    option = st.selectbox(
        "Select your query", [
            '1.Obesity vs malnutrition comparison by country(any 5 countries)',
            '2.Gender-based disparity in both obesity and malnutrition',
            '3.Region-wise avg estimates side-by-side(Africa and America)',
            '4.Countries with obesity up & malnutrition down',
            '5.Age-wise trend analysis'
        ])

    if option == '1.Obesity vs malnutrition comparison by country(any 5 countries)':
        q1 = """
        SELECT o.Country, o.Year, o.Gender, o.Age_Group,
        o.Mean_Estimate AS Obesity_Estimate,
        m.Mean_Estimate AS Malnutrition_Estimate
        FROM obesity o
        JOIN malnutrition m
        ON o.Country = m.Country
        AND o.Year = m.Year
        AND o.Gender = m.Gender
        AND o.Age_Group = m.Age_Group
        WHERE o.Country IN ('India', 'Brazil', 'Nigeria', 'USA', 'Kenya')
        ORDER BY o.Country, o.Year;
        """

    elif option == '2.Gender-based disparity in both obesity and malnutrition':
        q1 = """
        SELECT o.Gender,
        AVG(o.Mean_Estimate) AS Avg_Obesity,
        AVG(m.Mean_Estimate) AS Avg_Malnutrition,
        (AVG(o.Mean_Estimate) - AVG(m.Mean_Estimate)) AS Disparity
        FROM obesity o
        JOIN malnutrition m
        ON o.Country = m.Country
        AND o.Year = m.Year
        AND o.Gender = m.Gender
        AND o.Age_Group = m.Age_Group
        GROUP BY o.Gender;

        """

    elif option == '3.Region-wise avg estimates side-by-side(Africa and America)':
        q1 = """
        SELECT o.Region,
        AVG(o.Mean_Estimate) AS Avg_Obesity,
        AVG(m.Mean_Estimate) AS Avg_Malnutrition
        FROM obesity o
        JOIN malnutrition m
        ON o.Country = m.Country
        AND o.Year = m.Year
        AND o.Gender = m.Gender
        AND o.Age_Group = m.Age_Group
        WHERE o.Region IN ('Africa', 'Americas')
        GROUP BY o.Region;
        """

    elif option == '4.Countries with obesity up & malnutrition down':
        q1 = """
        SELECT o.Country,
        MAX(o.Mean_Estimate) - MIN(o.Mean_Estimate) AS Obesity_Change,
        MAX(m.Mean_Estimate) - MIN(m.Mean_Estimate) AS Malnutrition_Change
        FROM obesity o
        JOIN malnutrition m
        ON o.Country = m.Country
        AND o.Year = m.Year
        GROUP BY o.Country
        ORDER BY Obesity_Change DESC;
        """

    elif option == '5.Age-wise trend analysis':
        q1 = """
        SELECT o.Age_Group,
        AVG(o.Mean_Estimate) AS Avg_Obesity,
        AVG(m.Mean_Estimate) AS Avg_Malnutrition
        FROM obesity o
        JOIN malnutrition m
        ON o.Country = m.Country
        AND o.Year = m.Year
        AND o.Gender = m.Gender
        AND o.Age_Group = m.Age_Group
        GROUP BY o.Age_Group
        ORDER BY o.Age_Group;
        """
    
    if q1:
        cursor.execute(q1)
        data = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(df)