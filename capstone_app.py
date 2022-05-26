#Imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from PIL import Image
import re
from matplotlib.ticker import MaxNLocator
import numpy as np


#Defining general properties
st.set_page_config(
    page_title= "🚴PCM🚴",
    page_icon = "🚴",
    layout="wide"
    )

#Data&Model load functions
def load_model():
    filename = "model_final.sav"
    loaded_model = pickle.load(open(filename,"rb"))
    return loaded_model

@st.cache()
def load_rider_data():
    riders = pd.read_csv("data_riders_normalized.csv").drop("Unnamed: 0", axis = 1)
    return riders

@st.cache()
def load_iw_data():
    info_weather = pd.read_csv("weather_info_inputs_normalized.csv").drop("Unnamed: 0", axis = 1)
    return info_weather


def load_pred_data():
    pred_data = pd.read_csv("pred_data.csv").drop("Unnamed: 0", axis = 1)
    return pred_data


# Layout
row1_col1, row1_col2 = st.columns((1,1))
row2_col1, row2_col2 = st.columns((1,1))
row3_col1, row3_col2 = st.columns((1,1))
row4_col1, row4_col2 = st.columns((1,1))
row1_col2.empty()


#data load
riders = load_rider_data()
info_weather = load_iw_data()
model = load_model()
pred_data = load_pred_data()

#Dataframes of single tours & list of team
tdf = info_weather.groupby("Tour").get_group("tdf").sort_values("Date")
gdi = info_weather.groupby("Tour").get_group("giro").sort_values("Date")
vae = info_weather.groupby("Tour").get_group("vuelta").sort_values("Date")

teams = list(riders["team"].unique())
teams.sort()


###Sidebar for user input
with st.sidebar:
    #title
    st.title("🚴 ProCycManager 🚴")

    #expander for description
    with st.expander('More Information'):
        st.write("""This app helps you to decide which rider should be the team leader of your team.
        Based on previous results you can check how the individual riders perform on certain stages or on the full course.
        Furthermore you can compare riders predicted performance on the stages.""")

    #tour selection
    course = st.radio("Tours:", ("Tour de France 🇫🇷","Giro d’Italia 🇮🇹","Vuelta a España 🇪🇸"), help="Select one of the 3 listed bicycle tours")

    #team selection
    team_sel = st.selectbox("Select your team:", teams, help="Select your team for login")

    #one or two rider selection
    one_two = st.radio("Check for one or two riders:",("1","2"))



    with st.form(key="form1"):

    #stage selection
        if course == "Tour de France 🇫🇷":
            tdf_stage_sel = st.selectbox("Full tour or stage?",tdf["stage"], help="Select one of the listed stages or select the whole tour")
            stage = tdf_stage_sel
        elif course == "Giro d’Italia 🇮🇹":
            gdi_stage_sel = st.selectbox("Full tour or stage?",gdi["stage"], help="Select one of the listed stages or select the whole tour")
            stage = gdi_stage_sel
        elif course == "Vuelta a España 🇪🇸":
            vae_stage_sel = st.selectbox("Full tour or stage?",vae["stage"], help="Select one of the listed stages or select the whole tour")
            stage = vae_stage_sel


        riderofteam = riders.groupby("team").get_group(team_sel)
        secriderofteam = riders.groupby("team").get_group(team_sel)

    #rider selection
        if one_two == "1":
            rider_sel = st.selectbox("Select a rider:", riderofteam, help="Select your rider")
        elif one_two == "2":
            rider_sel = st.selectbox("Select first rider:", riderofteam, help="Select your first rider")
            sec_rider_sel = st.selectbox("Select a second rider:", (secriderofteam), help="Select your second rider")

        submit_button = st.form_submit_button(label="Search")

    if submit_button:

#Output

    #Show picture of selected route
        if course == "Tour de France 🇫🇷":
            tdf = Image.open("tdf_map_cut.jpeg")
            row2_col2.image(tdf, width=380)

        elif course == "Giro d’Italia 🇮🇹":
            gdi = Image.open("gdi_map.jpeg")
            row2_col2.image(gdi, width=380)

        elif course == "Vuelta a España 🇪🇸":
            vae = Image.open("vae_map_cut.jpeg")
            row2_col2.image(vae, width=380)

    #charts data preperation
        c1_data = info_weather[info_weather["stage"] != "GC"].reset_index()

        for i in range(0, len(c1_data)):
            x = str(re.findall(r'\b\d+\b', c1_data["stage"][i]))
            x = x.replace("[", "")
            x = x.replace("]", "")
            x = x.replace("'", "")
            c1_data["stage"][i] = x


        if course == "Tour de France 🇫🇷":
            tour = "tdf"
        elif course == "Giro d’Italia 🇮🇹":
            tour = "giro"
        elif course == "Vuelta a España 🇪🇸":
            tour = "vuelta"


        tour_name = c1_data[c1_data["Tour"] == tour]
        tour_name.stage = tour_name.stage.astype(int)
        tour_name = tour_name.sort_values("stage")

    #temperature chart
        fig, ax = plt.subplots(figsize=(16,10), dpi= 50)
        ax.plot(tour_name["stage"], tour_name["tmin"], marker = 'o',label = "Minimal temperature", color="green")
        ax.plot(tour_name["stage"], tour_name["tavg"],marker = 'o', label = "Maximal temperature", color="orange")
        ax.plot(tour_name["stage"], tour_name["tmax"],marker = 'o',label = "Maximal temperature", color="red")

        ax.tick_params(axis='x', labelsize=19)
        ax.tick_params(axis='y', labelsize=19)
        ax.set_ylabel("Temperature in °C", fontsize=19)
        ax.set_xlabel("Stage", fontsize=19)
        ax.set_xticks(np.arange(1, 22, 1))
        ax.legend(loc=2, prop={'size': 15})

        row3_col1.subheader("Temperature profile:")
        row3_col1.pyplot(fig, use_container_width=True)

    #vertical profile chart
        fig, ax = plt.subplots(figsize=(16,10), dpi= 50)
        ax.plot(tour_name["stage"], tour_name["Vert. meters"],label = "Vertical meters", color="blue")
        ax.tick_params(axis='x', labelsize=19)
        ax.tick_params(axis='y', labelsize=19)
        ax.set_xlabel("Stage", fontsize=19)
        ax.set_ylabel("Vertical meters", fontsize=19)
        ax.fill_between(tour_name["stage"],tour_name["Vert. meters"],0, color='blue', alpha=.5)
        ax.legend(loc=2, prop={'size': 15})
        ax.set_xticks(np.arange(1, 22, 1))
        row3_col2.subheader("Vertical meters profile:")
        row3_col2.pyplot(fig, use_container_width=True)

    #model
        X_1 = info_weather[info_weather["stage"]==stage]
        X_1 = pd.DataFrame(X_1[["tavg", "tmin", "tmax", "pres", "Distance", "ProfileScore", "Vert. meters"]])

        sbheader= row2_col1.header(f"{course}")
        sbheader= row2_col1.subheader(f"{stage}")

        X_2 = riders[riders["Rider"]==rider_sel]
        X_2 = pd.DataFrame(X_2[["Climber", "Sprint", "Time trial", "GC", "Weight", "Age_y"]])


        if one_two =="1":

            df_stats = pd.concat([X_1.reset_index(level = 0),X_2.reset_index(level = 0)], axis=1)
            df_stats['CPS'] = df_stats['Climber']*df_stats['ProfileScore']

            df_stats['SPS'] = -df_stats['Sprint']*df_stats['ProfileScore']

            df_stats['PTPS'] = (df_stats['CPS'] + df_stats['SPS'])

            df_stats['Distance'] = df_stats['Distance'].str.replace(' km','').astype(float)

            df = df_stats.dropna()

            X = df[['Climber','Sprint','Time trial','GC','Weight','Age_y','Vert. meters','Distance', 'ProfileScore','PTPS','tavg','tmin', 'tmax','pres']]
            X.insert(0, 'const', 1.0)
            #table2 = row3_col1.table(X)

            y_predict_lin = model.predict(X)


            score = round(y_predict_lin[0],2)


            sbheader1= row2_col1.subheader(f"{rider_sel}s score:  {score}")




        elif one_two == "2":

            #score for rider 1
            df_stats = pd.concat([X_1.reset_index(level = 0),X_2.reset_index(level = 0)], axis=1)
            df_stats['CPS'] = df_stats['Climber']*df_stats['ProfileScore']

            df_stats['SPS'] = -df_stats['Sprint']*df_stats['ProfileScore']

            df_stats['PTPS'] = (df_stats['CPS'] + df_stats['SPS'])

            df_stats['Distance'] = df_stats['Distance'].str.replace(' km','').astype(float)

            df = df_stats.dropna()

            X = df[['Climber','Sprint','Time trial','GC','Weight','Age_y','Vert. meters','Distance', 'ProfileScore','PTPS','tavg','tmin', 'tmax','pres']]
            X.insert(0, 'const', 1.0)
            #table2 = row3_col1.table(X)

            y_predict_lin = model.predict(X)


            score = round(y_predict_lin[0],2)



            #score for rider 2
            X_3 = riders[riders["Rider"]==sec_rider_sel]
            X_3 = pd.DataFrame(X_3[["Climber", "Sprint", "Time trial", "GC", "Weight", "Age_y"]])

            df_stats2 = pd.concat([X_1.reset_index(level = 0),X_3.reset_index(level = 0)], axis=1)
            df_stats2['CPS'] = df_stats2['Climber']*df_stats2['ProfileScore']

            df_stats2['SPS'] = -df_stats2['Sprint']*df_stats2['ProfileScore']

            df_stats2['PTPS'] = (df_stats2['CPS'] + df_stats2['SPS'])

            df_stats2['Distance'] = df_stats2['Distance'].str.replace(' km','').astype(float)

            df2 = df_stats2.dropna()

            X2 = df2[['Climber','Sprint','Time trial','GC','Weight','Age_y','Vert. meters','Distance', 'ProfileScore','PTPS','tavg','tmin', 'tmax','pres']]
            X2.insert(0, 'const', 1.0)
            #table2 = row3_col1.table(X)

            y_predict_lin2 = model.predict(X2)


            score2 = round(y_predict_lin2[0],2)



            sbheader1= row2_col1.subheader(f"{rider_sel}s score:  {score}")
            sbheader2= row2_col1.subheader(f"{sec_rider_sel}s score:  {score2}")



        #table of best fitting riders for stage
        grouped_team = pred_data.groupby("team").get_group(team_sel)
        grouped_stage = grouped_team.groupby("stage").get_group(stage)
        grouped_stage = grouped_stage.sort_values(["predicted_fit"],ascending=False).reset_index(drop=True)
        grouped_stage = grouped_stage.head(5)
        grouped_stage = grouped_stage.set_index("Rider")
        grouped_stage = grouped_stage["predicted_fit"]


        row2_col1.subheader(f"Top 5 riders for {stage}")
        row2_col1.dataframe(grouped_stage)















