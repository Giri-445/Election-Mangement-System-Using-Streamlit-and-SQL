import streamlit as st
import sqlite3 as sq
import random as rd
import string
from datetime import  date, datetime, timedelta
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont


conn=sq.connect('Election_database.db')
c=conn.cursor()
logos=["Car","Sun","Lotus","Leaf","Crown"]
st.set_page_config(
    page_title="Election Commission of India",
    
    )


def main():

    logo_image = Image.open("eci_logo.png")

    st.title("----Election Commission Of India ---")
    st.image(logo_image, width=100) 
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Vote", "Add Voter", "Add Candidate", "Add Party", "View Result","Add Constituency"])
    voter_id=None

    with tab1:
        st.header("Welcome to Polling...")
        voter_id = st.text_input("Voter", placeholder="Enter your Voter Id..")

        if voter_id:
            voter_details = fetch_voter_details(voter_id)
            if voter_details:
                name, constituency, booth_number = voter_details
                st.write(f"Welcome, {name}!..")
                st.write(f'Your Constituency: {constituency}')
                st.write(f"Booth Number: {booth_number}")
                st.write("\n")

                parties_details = fetch_party_details(constituency)
                if parties_details:
                    party_candidates = {party_name: candidate_name for party_name, candidate_name in parties_details}
                    voted_party = st.selectbox("Choose a Party to Vote:", list(party_candidates.keys()))


                    if voted_party:
                        st.write(f"Candidate: {party_candidates[voted_party]}")  # Print candidate name
                        selected_logo=fetch_party_logo(voted_party)
                        st.write("Symbol:",selected_logo)
                        logoo=selected_logo+".png"
                        logooo="logo/"+logoo
                        st.image(logooo,caption="Symbol of the Party")
                        vote_button=st.button("Vote...!")
                        if vote_button:
                            poll=election_result(constituency, voted_party, party_candidates[voted_party], voter_id)
                            if poll=="Success":
                                vote=party_voter_voted(voter_id,voted_party)
                                if vote:
                                    st.success("Voted Successfully..")

                            elif poll=="Failed":
                                st.error("Error: This voter has already voted.")
            else:
                st.warning("Invalid Voter...")
                            

    with tab2:
        st.header("Welcome, to the Add Voter Section..")
        st.write("Please fill the details to add a new voter:")
        name = st.text_input("Name")
        default_date = date(2000, 1, 1) 
        hundred_years_ago = datetime.today() - timedelta(days=365*100)
        birthdate = st.date_input("Enter your date of birth:", value = default_date, min_value=hundred_years_ago, format="DD/MM/YYYY")


        age=calculate_age(birthdate)
        if age>=18:
            st.success("Eligible to Vote..")
            con_details=fetch_constituency_details()
            constituency = st.selectbox("Choose Your Constituency:",con_details)
            booth_number = st.text_input("Booth Number")
            gender=st.radio("Gender:",["Male","Female","Transgender"])
            photo = st.file_uploader("Upload Passport Size Photo:", type=None, accept_multiple_files=False)

            add_button = st.button("Add Voter")
            if add_button and name and constituency and booth_number and gender and photo:
                voter_id, voter_id_card = add_voter(name, constituency, booth_number, birthdate, gender, photo)
                st.success(f"Voter added successfully! Voter ID: {voter_id}")
                st.image(voter_id_card, use_column_width=500, caption="Generated Voter ID Card")
    
                if st.button("Download Voter ID Card"):
        
                    voter_id_card_path = "generated_voter_id_card.jpg"
                    voter_id_card.save(voter_id_card_path)
                    with open(voter_id_card_path, "rb") as f:
                        id_card_bytes = f.read()

                    st.download_button(
                        label="Click here to download",
                        data=open(voter_id_card_path, "rb").read(),
                        file_name="generated_voter_id_card.jpg",
                        mime="image/jpeg"
                        )

        else:
            st.error("Not Eligible to Vote..")


    

    with tab3:
        st.write("Enroll Candiate...")
        name=st.text_input("Name" ,placeholder="Enter your Name...")

        party=st.selectbox("Choose your Party", fetch_party_name())
        con=fetch_constituency_details()
        constituency=st.selectbox("Choose Your Constituency:",con,key="12")
        add_button=st.button("Add Candiate")

        if add_button and name and constituency and party:
            a=add_candiate(name,constituency,party)

            if a=="Success":
                st.success("Candiate Enrolled Successfully..")
            else:
                st.error("Failed to Enroll")

    with tab4:
        st.write("Enroll Party...")
        name=st.text_input("Party Name",placeholder="Enter Your Party Name..")
        selected_logo = st.selectbox("Select a logo", logos)
        words = name.split()
        acronym = ''.join(word[0].upper() for word in words)
        if acronym: 
            st.write(f"<span style='font-size:25px'><b>The Party Shortly Knowns as:</b> {acronym}</span>", unsafe_allow_html=True)

        principle=st.text_input("Principle",placeholder="Enter the Principle of the Party..")
        leader_name=st.text_input("Leader Name:", placeholder="Enter the Name of the Leader:")
        ap=st.button("Add Party")

        if name and selected_logo and principle and leader_name and acronym and ap:
            party=add_party(name,acronym,selected_logo,principle,leader_name)
            if party:
                st.write("Your Party Id is",party)
                st.success("Party Enrolled Successfully..")
            else:
                st.error("Failed to Enroll... Logo is already taken..")


    with tab5:
        if view_election_result():
            st.success("Election Result....")


    with tab6:
        st.header("Constituency")
        name=st.text_input("Enter the Constituency")
        if st.button("Add Constituency"):
            if add_constituency(name)=="Success":
                st.success("Successfully Added..")

            else:
                st.warning("Already Enrolled..")
            




def create_database():
    conn = sq.connect('election_database.db')
    c = conn.cursor()




    c.execute('''CREATE TABLE IF NOT EXISTS voters (
                voter_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                constituency TEXT NOT NULL,
                booth_number TEXT NOT NULL,
                dob text not null,
                gender text not null,
                photo blob,
                voter_id_card blob,
                party_voted TEXT
                
              
            )''')


    c.execute('''CREATE TABLE IF NOT EXISTS parties (
                    party_id text primary key,
                    acronym text not null,
                    name TEXT NOT NULL,
                    logo TEXT NOT NULL UNIQUE,

                    principle TEXT,
                    leader_name TEXT NOT NULL
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS candidates (
                    name TEXT NOT NULL,
                    constituency TEXT NOT NULL,
                    party TEXT NOT NULL

                )''')
    

    c.execute(''' CREATE TABLE IF NOT EXISTS result(
                    constituency text not null,
                    party text not null,
                    candidate_name text not null,
                    voter_id text not null unique
                )''')
    

    c.execute(''' CREATE TABLE IF NOT EXISTS constituency (
                    name text not null unique,
                    winner text
                )''')
    conn.commit()
    conn.close()

create_database()





def add_voter(name, constituency, booth_number, dob, gender, photo):
    voter_id = generate_voter_id()
    voter_id_card_img = generate_id_card(name, constituency, booth_number, dob, gender,voter_id, photo)

 
    photo_data = photo.read()

    
    import io
    voter_id_card_byte_io = io.BytesIO()
    voter_id_card_img.save(voter_id_card_byte_io, format='JPEG')
    voter_id_card_byte_io.seek(0)
    voter_id_card_data = voter_id_card_byte_io.read()

    c.execute("INSERT INTO voters (voter_id, name, constituency, booth_number, dob, gender, photo, voter_id_card) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (voter_id, name, constituency, booth_number, dob, gender, photo_data, voter_id_card_data))
    
    conn.commit()
    
    return voter_id, voter_id_card_img


def calculate_age(birthdate):
    today = datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def generate_voter_id(length=6):
   
    characters = string.ascii_letters + string.digits
    vo=''.join(rd.choices(characters, k=length))
    return vo.upper()

def fetch_voter_details(voter_id):
    c.execute("SELECT name, constituency, booth_number FROM voters WHERE voter_id=?", (voter_id,))
    return c.fetchone()

def fetch_party_details(constituency):
    c.execute("""
        SELECT party AS party_name, c.name AS candidate_name
        FROM candidates c
        WHERE c.constituency=?
    """, (constituency,))

    return c.fetchall()


def fetch_constituency_details():
    c.execute(""" select name from constituency """)
    names=c.fetchall()
    return [name[0] for name in names] 

def fetch_party_name():
    c.execute(""" select name from parties """)
    names=c.fetchall()
    return [name[0] for name in names]



def add_constituency(name):
    try:
        c.execute(""" Insert into constituency(name) values(?)""",(name,) )
        conn.commit()
        return "Success"
    except:
        return "Failed"


import time

def election_result(constituency, party, candidate_name, voter_id):
    try:

        if not check_already_voted(voter_id):
   
            c.execute("INSERT INTO result (constituency, party, candidate_name, voter_id) VALUES (?, ?, ?, ?)",
                      (constituency, party, candidate_name, voter_id))
            conn.commit()
            return "Success"
        else:
            return "Failed"

    except sqlite3.IntegrityError as e:
        # Handle unique constraint violation error
        return f"Error: {e}"

def check_already_voted(voter_id):
    c.execute("SELECT * FROM result WHERE voter_id=?", (voter_id,))
    result = c.fetchone()
    return result is not None



def party_voter_voted(voter_id, voted_party):
    c.execute("UPDATE voters set  party_voted=? where voter_id=?",(voted_party, voter_id,))
    conn.commit()
    return 1


def fetch_party_logo(party):
    c.execute("SELECT logo FROM parties WHERE name=?", (party,))
    result = c.fetchone()
    if result:
        return result[0]  # Return only the logo
    else:
        return None




def generate_party_id(length=6):
   
    characters = string.ascii_letters + string.digits
    vo=''.join(rd.choices(characters, k=length))
    return vo.upper()
        
def check_party_logo(logo):
    c.execute("SELECT * from parties where logo=?", (logo,))
    return c.fetchone()

def add_party(name,acronym, logo , principle, leader_name):
    logo_available=check_party_logo(logo)
    if logo_available:
        st.write("Logo Is not available.... Choose other Logo..")
        return 0 
    else:
        
        party_id=generate_party_id()
        c.execute("INSERT INTO parties (party_id,acronym ,name, logo ,principle, leader_name ) VALUES (?, ?, ?, ?, ?, ?)", (party_id,acronym, name, logo, principle, leader_name))
        conn.commit()
        return party_id
    

def add_candiate(name,constituency,party):
    c.execute("INSERT INTO candidates (name, constituency, party) VALUES (?, ?, ?)", (name, constituency, party))
    conn.commit()
    return "Success"




def view_election_result():
    st.header("Election Results")

    # Query the database to retrieve election results
    c.execute("""
        SELECT constituency, party, candidate_name, COUNT(*) AS vote_count
        FROM result
        GROUP BY constituency, party, candidate_name
        ORDER BY constituency, vote_count DESC
    """)
    election_results = c.fetchall()

    if election_results:
        # Create empty lists to store data for plotting
        constituencies = []
        parties = []
        vote_counts = []

        
        for result in election_results:
            constituency, party, candidate_name, vote_count = result
            constituencies.append(constituency)
            parties.append(party)
            vote_counts.append(vote_count)
            st.success(f"{constituency} ----> {candidate_name} ({party}) ----> {vote_count}")

        # Plot the election results using a bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(election_results))
        ax.bar(x, vote_counts, align='center')
        ax.set_xticks(x)
        ax.set_xticklabels(parties, rotation=45, ha='right')
        ax.set_xlabel('Parties')
        ax.set_ylabel('Vote Count')
        ax.set_title('Election Results by Party')
        st.pyplot(fig)

        # Find the party with the most constituency wins
        party_wins = {party: parties.count(party) for party in set(parties)}
        most_wins_party = max(party_wins, key=party_wins.get)

        st.success("Election results retrieved successfully.")
        st.success(f"The party with the most constituency wins: {most_wins_party} ({party_wins[most_wins_party]} constituencies)")
    else:
        st.warning("No election results found.")



def generate_id_card(name, constituency, booth_number, dob, gender,voter_id, photo):
    photo = Image.open(photo)
    id_card = Image.open("voter_idcard_template.jpg")

    # Resize the photo to fit a specific region on the ID card
    photo_width, photo_height = 200, 250  # Define the size of the region for pasting the photo
    photo = photo.resize((photo_width, photo_height))

    # Paste the resized photo onto the ID card template
    id_card.paste(photo, (140, 240))

    # Initialize drawing context
    draw = ImageDraw.Draw(id_card)

    # Load a font
    font_path = "arial.ttf" 
    try:
        font = ImageFont.truetype(font_path, 20)
    except OSError:
    # Fallback to a default font if the specified font is not available
        font = ImageFont.load_default()

    draw.text((320,170), voter_id, fill="black", font=font)

    # Write details on the image
    draw.text((80, 520), f"Name: {name}", fill="black", font=font)
    draw.text((80, 560), f"D.O.B: {dob}", fill="black", font=font)
    draw.text((80, 600), f"Gender: {gender}", fill="black", font=font)
    draw.text((80, 640), f"Voter_Id: {voter_id}", fill="black", font=font)


    return id_card



st.markdown(
    """
    <style>
    .stButton>button {
        float: left;
    }
    </style>
    """,
    unsafe_allow_html=True
)






if __name__ == "__main__":
    main()








    








