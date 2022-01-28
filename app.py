import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime

import altair as alt

# Initialize connection.
client = pymongo.MongoClient(
    "mongodb+srv://root:root@cluster0.f9ndm.mongodb.net/covid?retryWrites=true&w=majority"
)
db = client.covid


def submit(data):
    ins = db.covidindia.insert_one(data)
    print(ins)


def update(data):
    ins = db.covidindia.insert_one(data)
    print(ins)


st.title("Covid-19 India Data")

# crud
st.header("Database")

expander = st.expander("Create")
with expander:
    form = st.form(key="annotation")

expander = st.expander("Update")
with expander:
    updateform = st.form(key="updateform")

expander = st.expander("Delete")
with expander:
    deleteform = st.form(key="deleteform")

with form:
    st.subheader("Add a new case")
    cols = st.columns(2)
    sno = cols[0].text_input("Sno:")
    state = cols[1].text_input("State:")
    indian = cols[0].number_input("Indian:", value=0, format="%d")
    foreign = cols[1].number_input("Foreign:", value=0, format="%d")
    cured = cols[0].number_input("Cured:", value=0, format="%d")
    deaths = cols[1].number_input("Deaths:", value=0, format="%d")
    confirmed = cols[0].number_input("Confirmed:", value=0, format="%d")
    date = cols[1].date_input("Date:")
    create_submitted = st.form_submit_button(label="Submit")
    data = {
        "Sno": sno,
        "Date": str(date),
        "State/UnionTerritory": state,
        "ConfirmedIndianNational": indian,
        "ConfirmedForeignNational": foreign,
        "Cured": cured,
        "Deaths": deaths,
        "Confirmed": confirmed,
    }

with updateform:
    st.subheader("Update an existing case")
    cols = st.columns((1, 1))
    sno_u = cols[0].text_input("Sno:")
    col_u = cols[0].selectbox(
        "Col",
        ("Cured", "Deaths", "Confirmed", "State/UnionTerritory"),
        key="kp",
    )
    val_u = cols[0].text_input("Val:")
    update_submitted = st.form_submit_button(label="Update")

with deleteform:
    st.subheader("Delete a case")
    cols = st.columns((1, 1))
    sno_d = cols[0].text_input("Sno:")
    delete_submitted = st.form_submit_button(label="Delete")

if create_submitted:
    st.success("Submitted!")
    submit(data)
    st.balloons()

if delete_submitted:
    st.success("Deleted!")
    db.covidindia.delete_one({"Sno": sno_d})
    st.balloons()

if update_submitted:
    st.success("Updated!")
    db.covidindia.update_one({"Sno": sno_u}, {"$set": {col_u: val_u}})
    st.balloons()


def get_data():
    items = db.covidindia.find({"State/UnionTerritory": "Karnataka"}).limit(50)
    items = list(items)
    return items


# plots
st.header("Plots")

st.subheader("Daily Cases")
count = db.covidindia.aggregate(
    pipeline=[
        {
            "$group": {
                "_id": "$Date",
                "confirmed": {"$sum": {"$toDouble": "$Confirmed"}},
                "cured": {"$sum": {"$toDouble": "$Cured"}},
            }
        }
    ]
)

value_df = pd.DataFrame(count).rename(columns={"_id": "date"}).dropna()
if st.checkbox("Show data", key="dg"):
    st.write(value_df)

c = (
    alt.Chart(value_df.melt("date"))
    .mark_line()
    .encode(
        x=alt.X("date", axis=alt.Axis(labelOverlap="greedy", grid=False)),
        y="value",
        color="variable",
    )
)
st.altair_chart(c, use_container_width=True)

# 2
deaths = db.covidindia.aggregate(
    pipeline=[
        {
            "$group": {
                "_id": "$Date",
                "deaths": {"$sum": {"$toDouble": "$Deaths"}},
            }
        }
    ]
)

value_df = pd.DataFrame(deaths).rename(columns={"_id": "date"}).dropna()
if st.checkbox("Show data", key="dsfs"):
    st.write(value_df)

c = (
    alt.Chart(value_df.melt("date"))
    .mark_line()
    .encode(
        x=alt.X("date", axis=alt.Axis(labelOverlap="greedy", grid=False)),
        y="value",
        color="variable",
    )
)
st.altair_chart(c, use_container_width=True)


st.subheader("Total cases of each State")
cases = db.covidindia.aggregate(
    pipeline=[
        {
            "$group": {
                "_id": "$State/UnionTerritory",
                "confirmed": {"$sum": {"$toDouble": "$Confirmed"}},
            }
        }
    ]
)

cases_df = pd.DataFrame(cases).rename(columns={"_id": "state"}).dropna()

if st.checkbox("Show data", key="c"):
    st.write(cases_df)
st.bar_chart(cases_df.set_index("state"), height=400)
