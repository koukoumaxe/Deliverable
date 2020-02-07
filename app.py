import requests
import json
import collections
import math
from requests import ConnectionError
from flask import Flask, request
from flask_restplus import Resource, Api
from bs4 import BeautifulSoup
from lxml.html import fromstring
from lxml.html import tostring
import yaml
import copy
import dateparser
import datetime
from datetime import datetime
from opencage.geocoder import OpenCageGeocode



app = Flask("app_name")
key = 'c278683aaaa94a36a1a82e84db0c4148'
geocoder = OpenCageGeocode(key)
full_url = "https://pastebin.com/UFJQRcun"


def convert_to_yaml(doc):
    new_doc = doc.replace("\r\n\r\n", "\r\n---")
    
    return new_doc

def clean_html (htmlText):
    word_starts_at = '">'
    word_ends = "</"
    clean_start = htmlText.partition(word_starts_at)[2]
    clean_end = clean_start.partition(word_ends)[0]
    return clean_end

def curly_input_to_dict(curly_input):
    date_dict = {}
    date_list = []
    input_list = curly_input.split(",")

    separator = ":"
    for entry in input_list:
        key = entry.partition(separator)[0].replace("{","")
        key = key.replace("}", "")
        key = key.replace(" ", "")
        value = entry.partition(separator)[2].replace("'","")
        value = value.replace("}", "")
        value = value.replace(" ", "")
        date_dict[key]=value
    print(date_dict)
    return date_dict

def soup_query (page_content):
    soup = BeautifulSoup(page_content, 'lxml')
    html_text = soup.find_all("textarea", {"id": "paste_code"})         
    text = clean_html(str(html_text))
    return text

def fill_dict_from_yaml (text_yaml):
    user_dic = {}
    users_list = []
    time_dict = {}
    time_list = []
    type_list = []
    date_list = []
    separator = " - "
    ent_separator = "\r\n"
    for data in yaml.safe_load_all(text_yaml):
        for key, value in data.items():
            if (str(key) != "Check-in history"):
                user_dic[(key)]= value
            if (str(key) == "Check-in history"):
                # print(value)
                words =value.split(' ')
                # print(words)
                # for (i=0 in range(5):
                #     type_list.append(words[i::5])
                # date_list = type_list[0]
                date_list = [words[x:x+5] for x in range(0, len(words), 5)]
                # print(date_list)
                user_dic[key] = date_list
                # print(type_list)
            # else:
            #     # temp_list = str(value).splitlines()
            #     # temp_list = temp_str.split(',')
            #     print(str(value))
            #     temp_list = str(value).partition(ent_separator)[0]
            #     for entry in temp_list:
                    
            #         list_perlog = entry.split(',')
            #         for log in list_perlog: 
            #             print(log)
            #             temp_key= str(log).partition(separator)[0]
            #             temp_value = str(log).partition(separator)[2]
            #             time_dict[(temp_key)] = temp_value
            #         time_list.append(copy.deepcopy(time_dict))
            #         user_dic[(key)] = time_list
        users_list.append(copy.deepcopy(user_dic))
    # print(users_list)
    return users_list


@app.route('/proximity_date_query', methods=['POST'])
def proximity_date_query():
    if request.method == 'POST':
        date_dict = {}
        distance = request.form['m']
        date_query = request.form['dateRange']
        date_dict = curly_input_to_dict(date_query)
        # print(date_j["from"])
        # to_date = date_j["to"]
        
        
        # for key, value in date_dict.items():
        #     print(date_dict[key])
        # parsed_date = dateparser.parse(date_range_query)

        page = requests.get(full_url)
        try:
            if(page.status_code==200):
                src = page.content
                text = soup_query(src)
                yaml_text = convert_to_yaml(text)
                profile_list = fill_dict_from_yaml(yaml_text)

                return_list = []
                # print (profile_list)
                date_range = []
                for entry in profile_list:
                    for log_list in entry["Check-in history"]:
                        
                        from_date = datetime.strptime(date_dict["from"], '%d.%m.%Y') 
                        to_date = datetime.strptime(date_dict["to"], '%d.%m.%Y')
                        check_date = datetime.strptime(log_list[0], '%d.%m.%Y')
                        if(from_date < check_date < to_date):
                            date_range.append(log_list[3]+" "+log_list[4])
                            # distance = math.sqrt( ((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2) )
                        
                # for nameq in name_query:
                #     for entry in profile_list:     
                #         if((entry["name"] == nameq)):
                #             for log_list in entry["Check-in history"]:
                #                 print(log_list)
                #                 parsed_from_list = dateparser.parse(log_list[0])
                #                 if(parsed_date.date() == parsed_from_list.date()):
                #                     return_list.append( (str(entry["name"])+": " + str(log_list[3]) + " " + str(log_list[4])+ " Place: "+(location_name[0]['formatted'])))

                # return(str(return_list))
            return " end:"
        except ConnectionError as e:
            print (e)
            return e
        except ConnectionAbortedError as e:
            print (e)
            return e
    return "Not OK"

@app.route('/name_date_query_bbox', methods=['POST'])
def name_date_query_bbox():
    if request.method == 'POST':
        name_query = request.form['name'].split(', ')
        date_query = request.form['date']
        parsed_date = dateparser.parse(date_query)
        print(name_query)
        page = requests.get(full_url)
        try:
            if(page.status_code==200):
                src = page.content
                text = soup_query(src)
                yaml_text = convert_to_yaml(text)
                profile_list = fill_dict_from_yaml(yaml_text)

                return_list = []
                for nameq in name_query:
                    for entry in profile_list:     
                        if((entry["name"] == nameq)):
                            for log_list in entry["Check-in history"]:
                                print(log_list)
                                parsed_from_list = dateparser.parse(log_list[0])
                                if(parsed_date.date() == parsed_from_list.date()):
                                    return_list.append( (str(entry["name"])+": " + str(log_list[3]) + " " + str(log_list[4])))

                return(str(return_list))
            return " end:"
        except ConnectionError as e:
            print (e)
            return e
        except ConnectionAbortedError as e:
            print (e)
            return e
    return "Not OK"

@app.route('/name_date_query', methods=['POST'])
def name_date_query():
    if request.method == 'POST':
        name_query = request.form['name'].split(', ')
        date_query = request.form['date']
        parsed_date = dateparser.parse(date_query)
        print(name_query)

        page = requests.get(full_url)
        try:
            if(page.status_code==200):
                src = page.content
                text = soup_query(src)
                yaml_text = convert_to_yaml(text)
                profile_list = fill_dict_from_yaml(yaml_text)

                return_list = []
                for nameq in name_query:
                    for entry in profile_list:     
                        if((entry["name"] == nameq)):
                            for log_list in entry["Check-in history"]:
                                print(log_list)
                                parsed_from_list = dateparser.parse(log_list[0])
                                if(parsed_date.date() == parsed_from_list.date()):
                                    coord1 = log_list[3].replace(",", "")
                                    coord2 = log_list[4].replace(",", "")
                                    location_name = geocoder.reverse_geocode(float(coord1), float(coord2))
                                    return_list.append( (str(entry["name"])+": " + str(log_list[3]) + " " + str(log_list[4])+ " Place: "+(location_name[0]['formatted'])))
                return(str(return_list))
            return " end:"
        except ConnectionError as e:
            print (e)
            return e
        except ConnectionAbortedError as e:
            print (e)
            return e
    return "Not OK"

@app.route('/age_sex_query', methods=['POST'])
def age_sex_query():
    if request.method == 'POST':
        age_query = int(request.form['age'])
        sex_query = request.form['sex']

        page = requests.get(full_url)
        # print(full_url)
        # print (page.status_code)
        try:
            if(page.status_code == 200):
                src = page.content
                text = soup_query(src)
                yaml_text = convert_to_yaml(text)
                profile_list = fill_dict_from_yaml(yaml_text)

                # user_dic = {}
                # profile_list = []

                # for data in yaml.safe_load_all(yaml_text):
                #     for key, value in data.items():
                #         user_dic[(key)]= value
                #     profile_list.append(copy.deepcopy(user_dic))
                # print(str(profile_list))

                return_list = []
                for entry in profile_list:
                    if((entry["age"] >= age_query) and (entry["sex"] == sex_query)):
                        return_list.append(json.dumps(entry["name"]))
                return str(return_list)
        except ConnectionError as e:
            print (e)
            return e
        except ConnectionAbortedError as e:
            print (e)
            return e

@app.route('/')
def get():
    return {
			"status": "Got new data"
		}

if __name__ == "__main__":
    # flask_app = Flask(__name__)
    # app = Api(app = flask_app)

    # name_space = app.namespace('main', description='Main APIs')
    app.run(debug=True)