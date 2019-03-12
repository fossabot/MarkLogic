import os
import io
import random
import json
import requests
from io import StringIO
from project.api.models import decode_auth_token, MLStatus
from project.linearSVC import matchSport
from project import db

#pass user ID (Auth token) and FileNames => output list of lists? dictionary?
#need duplicates to help confidence to matching to a sport
def extract_columns(app, auth_token, file_names) :
    file_with_names = {}
    cur_path = os.getcwd()
    print("The current working directory is %s\n" % cur_path)
    #generate random number for temp csv storage folder
    rand_file_num = random.randint(1000, 9999)
    create_folder = str(rand_file_num)+ "_temp_files"
    print("Create Folder: " + create_folder + "\n")
    abs_path = "/temp/" + create_folder
    #create directory
    try:
        os.makedirs(abs_path)
    except OSError:
        print ("Creation of the directory %s failed\n" % create_folder)
    else:
        print ("Successfully created the directory, adding it to the db %s\n" % create_folder)
        insert_cwd(app, auth_token, abs_path)

    #download files from s3. Make a get request from s3 endpoint
    g_url = "http://file_system:5000/s3/download"
    g_headers = {"Authorization" : 'Bearer ' + auth_token}
    #get only the data for first file in file name list
    if not file_names:
        print("List of given file names is empty")
    else:
        f = file_names[0]
        g_param = {"address" : f}
        r = requests.get(url = g_url, headers = g_headers, params = g_param)
        #not sure if it returns download url or zip file of all files? Need to ask Jake
        #parse data and gather column names while file is open, if valid
        file_data = r.text
        if file_data == None:
            print("No valid file data found\n")
        else:
            print("File data retrieved writing to directory\n")
            col_names = []
            buf = StringIO(file_data)
            first_line = buf.readline()
            splitted = first_line.split(',')
            for word in splitted:
                processed = (word.strip()).lower()
                print(processed)
                col_names.append(processed)
            file_with_names[f] = col_names

            with open(f, 'w') as wFile:
                wFile.write(file_data)
    """
    for f in file_names:
        g_param = {"address" : f}
        r = requests.get(url = g_url, headers = g_headers, params = g_param)
        #parse data and gather column names while file is open, if valid
        file_data = r.text
        if file_data == None:
            print("No valid file data found\n")
        else:
            print("File data retrieved writing to directory\n")
            col_names = []
            buf = StringIO(file_data)
            first_line = buf.readline()
            splitted = first_line.split(',')
            for word in splitted:
                processed = (word.strip()).lower()
                col_names.append(processed)
            files_with_names[f] = col_names

            with open(f, 'w') as wFile:
                wFile.write(file_data)
    """
    #call G's ML stuff
    matchSport(json.dumps(file_with_names), auth_token, app)
#remove temp files after all the files are parsed

def insert_cwd(app, auth_token, cwd):
    with app.app_context():
        resp = decode_auth_token(auth_token)
        if isinstance(resp, str):
            # auth_token isn't valid anymore - that's not good
            print(resp)
        # If its not a string, its a user_id
        status = MLStatus.query.filter_by(user_id=resp).first()
        if not status:
            # Can't find user in status DB - that's not good
            print("Cannot find user in status DB")
        status.working_directory = cwd

        db.session.commit()