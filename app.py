import streamlit as st
import pandas as pd
import easyocr
import cv2
import io
import numpy as np
import mysql.connector
from PIL import Image

st.set_page_config(layout="wide")

selected = st.sidebar.radio("Select Option", ['Data Extraction', 'Alter and Drop'])

if selected == 'Data Extraction':
    card = st.file_uploader("Upload the card", type=["png"])
    
    
    if card is not None:
        st.write('\n')
        st.write('\n')
        st.write('\n')
        pil_image = Image.open(card)
        st.image(pil_image,)
        with st.spinner("Getting details for you"):   
            def detail(card):
                image = Image.open(card)

                numpy_image = np.asarray(image)
                reader = easyocr.Reader(['en'])
                results = reader.readtext(numpy_image)
                return results

            txt = []
            results = detail(card)
            image = Image.open(card)

            numpy_image = np.asarray(image)
            for i in results:
                bbox = i[0]
                cv2.rectangle(numpy_image, (int(bbox[0][0]), int(bbox[0][1])),
                            (int(bbox[2][0]), int(bbox[2][1])), (0, 255, 0), 2)
                cv2.putText(numpy_image, i[1], (int(bbox[3][0]), int(bbox[3][1]) + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                txt.append(i[1])
            st.image(numpy_image)
            name = txt[0]
            designation = txt[1]
            txt.remove(txt[0])
            txt.remove(txt[0])

            done  = []
            address = []
            number = []
            email = []
            website = []
            for i in txt:
                if "-" in i:
                    
                    done.append(i)
                    number.append(i)
                elif "@" in i:
                    email.append(i)
                    done.append(i)
                elif any(char.isdigit() for char in i):
                    address.append(i)
                    done.append(i)

                elif 'www' in i or "WWW" in i or ".com" in i:
                    website.append(i)
                    
                    done.append(i)

            #if bttn:
            with st.form("Details"):
                sname = st.text_input("Name : ", name)
                sdesignation = st.text_input("Designation : ", designation)
                snumber = st.text_input("Number", ",".join(number))
                swebsite = st.text_input("Website", ",".join(website))
                semail = st.text_input("Email : ", ",".join(email))

                saddress = st.text_input("Address", ",".join(address))

                txt = [i for i in txt if i not in done]

                scampanyname = st.text_input("Company Name", " ".join(txt))
                image = Image.open(card)
                with io.BytesIO() as output:
                    image = image.convert("RGB")
                    image.save(output, format="JPEG")
                    image_data = output.getvalue()
                
                simagedata = image_data
                ttn = st.form_submit_button("Save the details")
        try:
            if ttn:
                config = {
                    'host': 'localhost',
                    'user': 'root',
                    'password': 'mysql123',
                    'database': 'bizcardz'
                    }
                conn = mysql.connector.connect(**config)
                cursor = conn.cursor()
                
                create_query = '''create table if not exists cards( Name varchar(255),
                                                                    Designation varchar(255),
                                                                    Number varchar(255) PRIMARY KEY,
                                                                    Website varchar(255),
                                                                    Email varchar(255),
                                                                    Address varchar(255),
                                                                    Company_Name varchar(255),
                                                                    Image_data LONGBLOB)
                                    '''
                cursor.execute(create_query)
                
                insert_query = '''insert into cards values (%s,%s,%s,%s,%s,%s,%s,%s)'''
                values = (sname, sdesignation, snumber, swebsite, semail, saddress, scampanyname, simagedata)
                cursor.execute(insert_query, values)
                conn.commit()
                st.success("Data successfully stored to Mysql")
                cursor.execute("select * from cards")
                x = cursor.fetchall()
                st.dataframe(pd.DataFrame(x))
            
                conn.commit()
                cursor.close()
                conn.close()
        except :
            st.success("Data already exists")
        

elif selected == 'Alter and Drop':
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'mysql123',
        'database': 'bizcardz'
    }
    with mysql.connector.connect(**config) as conn:
        with conn.cursor() as cursor:
            cursor.execute("select Name,Designation,Company_Name,Number,Website,Email,Address,Image_data from cards")
            a = cursor.fetchall()
            details = pd.DataFrame(a, columns=['Name', 'Designation', 'Company_Name', 'Number', 'Website', 'Email', 'Address', 'Image_data'])
            st.dataframe(details)

            namlist = details['Name'].to_list()

            col1,col2 = st.columns(2)
            with col1:
                st.header("Alter details")
                
                nm = st.selectbox("Select one name",details['Name'].tolist())
                

                with st.form("Details"):
                    fname = st.text_input("Name", details[details['Name'] == nm]['Name'].iloc[0])
                    fdesignation = st.text_input('Designation', details[details['Name'] == nm]['Designation'].iloc[0])
                    fcompanyname = st.text_input('Company_Name', details[details['Name'] == nm]['Company_Name'].iloc[0])
                    fnumber = st.text_input('Number', details[details['Name'] == nm]['Number'].iloc[0])
                    fwebsite = st.text_input('Website', details[details['Name'] == nm]['Website'].iloc[0])
                    femail = st.text_input('Email', details[details['Name'] == nm]['Email'].iloc[0])
                    faddress = st.text_input('Address', details[details['Name'] == nm]['Address'].iloc[0])
                    fimagedata = details[details['Name'] == nm]['Image_data'].iloc[0]
                    crt = st.form_submit_button("Save details")

                if crt:
                    query = ''' UPDATE cards SET Name=%s, Designation=%s, Number=%s, Website=%s, Email=%s, Address=%s, Company_Name=%s, Image_data=%s WHERE Name=%s '''
                    values = (fname, fdesignation, fnumber, fwebsite, femail, faddress, fcompanyname, fimagedata, nm)
                    cursor.execute(query, values)
                    conn.commit()
                    cursor.execute("select * from cards")
                    x = cursor.fetchall()
                    st.dataframe(pd.DataFrame(x))

            with col2:
                st.header("Delete details")
                nm = st.selectbox("Select name",details['Name'].tolist())

                if st.button("Delete details"):
                    query = '''delete from cards where Name = %s'''
                    values = (nm,)
                    cursor.execute(query,values)
                    conn.commit()
                    cursor.execute("select * from cards")
                    x = cursor.fetchall()
                    st.dataframe(pd.DataFrame(x))
