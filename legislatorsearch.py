#!/usr/bin/python3.6
import requests
import zipcode
import time
from yattag import Doc
import random

key_list = ['4155f360-e0f4-427c-841a-93b9a20cfeb7',
            '1a53fe15-6b43-4943-9812-e4dadd6b518f',
            '246a5506-c108-48b4-b6d8-69a0100feaca',
            '7e2591ee-e480-45f4-bc0c-a4a47bec06e9']
headers = {
    'X-API-KEY': random.choice(key_list)
}

# class of basic fields for local representative
class Representative:
	def __init__(self,name):
		self.name = name
		self.state = None
		self.district = None
		self.chamber = None
		self.email = None
		self.phone1_type = None
		self.phone1_num = None
		self.phone2_type = None
		self.phone2_num = None
		self.state_legislature = None

	def print_values(self):
		print("name: ", self.name)
		print("state: ",self.state)
		print("district: ", self.district)
		print("chamber: ", self.chamber)
		print("state legislature: ", self.state_legislature)
		print("email: ", self.email)
		print("phone1_type: ", self.phone1_type)
		print("phone1_num: ", self.phone1_num)
		print("phone2_type: ", self.phone2_type)
		print("phone2_num: ", self.phone2_num)
		print("\n")

#BELOW IS CODE TO DYNAMICALLY SEARCH FOR POLITICIANS BASED ON LONGITUDE & LATITUDE
def generate_location_query(user_latitude, user_longitude):
	latitude = user_latitude
	longitude = user_longitude
	query = """
	{
	  people(latitude: %s, longitude: %s, first: 100) {
	    edges {
	      node {
	        name
	        chamber: currentMemberships(classification:["upper", "lower"]) {
	          post {
	            label
	          }
	          organization {
	            name
	            classification
	            parent {
	              name
	            }
	          }
	        }
	      }
	    }
	  }
	}

	""" % (latitude, longitude)
	return query

# BELOW IS HOW TO DYNAMICALLY SEARCH FOR POLITICIANS
def generate_person_query(name):
	politican_name = "\"%s\"" % (name)
	query = """
	{
	  people(first: 1, name:%s) {
	    edges {
	      node {
	        name
	        contactDetails{
	          note
	          type
	          value
	        }
	        chamber: currentMemberships(classification:["upper", "lower"]) {
	          post {
	            label
	          }
	          organization {
	            name
	            classification
	            parent {
	              name
	            }
	          }
	        }
	      }
	    }
	  }
	}
	""" % (politican_name)
	return query

def parse_location_response(response_text):
    zipcode_response_string = response_text.replace("}","").replace("{","").replace("\"","").replace("]","")
    zipcode_response = zipcode_response_string.split("node:")

    # skips the first portion because of neglible text
    major_tings = zipcode_response[1:]

    rep_list =[]
    for iterator in major_tings:
        new_rep ={}
        new_string = iterator.replace("name:","").replace("chamber:[post:label:","").replace("organization:","").replace("classification:","").replace("parent:","")
        rep_info = new_string.split(",")
        current_representative = Representative(rep_info[0])
        if len(rep_info) > 2:
            current_representative.district = rep_info[1]
            current_representative.chamber = rep_info[2]
            # new_rep['chamber']= rep_info[3]
            current_representative.state_legislature = rep_info[4]
            current_representative.state = (rep_info[4].replace(" Legislature","").replace("State","")).strip()

        rep_list.append(current_representative)

    return rep_list


def parse_legislator_response(response_text, current_representative):
	# removes unnecessary characters in between
	# handles query response as a string
	response_string = response_text.replace("}","").replace("{","").replace("\"","").replace("]","")

	#uses the 'email,value:' portion of string to find the email, then splits the string to start @ email
	start = response_string.find("email,value:") + len("email,value:")
	sub_response = response_string[start:]

	spliced_text = sub_response.split(",")

	# below are used to set phone values for representatives
	phone1_info = [None, None]
	phone2_info=[None, None]

	# used as a placeholder for reps' phone info
	current_phone = []

	for substring in spliced_text:
		# once "chamber" is reached, we are finished with the contactdetails portion of query response
		if "chamber" in substring:
			break

		# if @ is included in response, guaranteed email, so we set appropriate value and continue
		elif("@" in substring):
			current_representative.email = substring
			continue


		segment = substring.split(":")

		# if segment length is 1, then does not contain pertinent info
		if(len(segment)>1):

			# this portion is used to weed out phone numbers from other contact text (applies to addresses, but this is dealt with later)
			if any(map(str.isdigit, segment[1])):
				segment[1] = segment[1].replace("-","")

			# descriptor for contact detail
			if('Office' in segment[1]):
				# wehn current_phone length is 0, we know it has not been initialized with new value
				if(len(current_phone) == 0):
					# appends respective office - District or Capitol
					current_phone.append(segment[1])
					continue

			# below is an indicator we're on right path, and need to continue to phone number
			elif (segment[1] =="voice"):
				continue
			# again, another end of contact details
			elif (segment[1] == "fax"):
				break
			else:
				# this discerns phone numbers from addresses
				if segment[1].isdigit():
					current_phone.append(segment[1])

		# if current_phone <1, we know it's lacking phone number
		if(len(current_phone) == 2):
			if phone1_info[0] is None:
				phone1_info = current_phone
				# clears current_phone to restart processing for phone2 information
				current_phone=[]

			else:
				phone2_info = current_phone
				# if we've detected the same district number, no need to duplicate offering
				if phone2_info[0] == phone1_info[0]:
					phone2_info = [None,None]
				break
	if phone1_info[0] is not None:
		current_representative.phone1_type, current_representative.phone1_num = phone1_info[0], "+1("+ phone1_info[1][:3] + ")-"+phone1_info[1][3:6]+"-"+phone1_info[1][6:]
	else:
		return "Sufficient information does not exist"
	current_representative.phone2_type, current_representative.phone2_num = phone2_info[0], phone2_info[1]
	return "success"

def legislature_title(chamber):
    legislature = chamber.lower()
    if "senate" in legislature:
    	return "State Senator"
    elif "assembly" in legislature:
    	return "Assembly Member"
    elif "house" in legislature:
    	return "Representative"
    else:
    	return ""

def legislature_in_html_response(chamber):
    legislature = chamber.lower()
    if "senate" in legislature:
        return "State Senate"
    elif "assembly" in legislature:
        return "General Assembly"
    elif "house" in legislature:
        return "House of Representatives"
    else:
        return ""

def district_suffix(district):
    if district[-1]== "1" and district != "11":
        return district+"st"
    elif district[-1] =="2" and district != "12":
        return district+"nd"
    elif district[-1] == "3" and district != "13":
        return district+"rd"
    else:
        return district+"th"

def generate_email(legislator, user_name):
	newline_character = '%0d%0a'
	tab_character = '%09'
	bullet_character = '%E2%80%A2'
	result =[]
	if legislator.chamber is not None:
		greeting = "Dear %s %s," % (legislature_title(legislator.chamber), legislator.name)+ newline_character + newline_character
	else:
		greeting = "Dear %s," % (legislator.name)+ newline_character + newline_character
	result.append(greeting)

	if legislator.district is not None:
		para1 ='''
			My name is %s and I am one of your concerned constituents in the %s District. I am writing to you today to ask what you are doing, as a member of the %s, to ensure that you are taking actions to allocate resources to create safer communities.
			''' %(user_name, district_suffix(legislator.district),legislator.state_legislature) + newline_character +newline_character
	else:
		para1 ='''
			My name is %s and I am one of your concerned constituents. I am writing to you today to ask what you are doing, as a representative of my region, to ensure that you are taking actions to allocate resources to create safer communities.
			''' %(user_name) + newline_character +newline_character
	result.append(para1)

	para2 = '''
		The deaths of George Floyd and Breonna Taylor have shaken every state in America, as well as multiple countries around the world. Subsequently, the death toll of people killed by police brutality is steadily and unfairly rising as the nation exercises its 1st Amendment right to assemble.
		''' + newline_character + newline_character
	result.append(para2)
	para3 = '''
		In the cases of George Floyd and Breonna Taylor, police have wrongfully murdered a man via brutal force strangulation and raided the home of a civilian without a warrant and subsequently shot her, respectively. The systemic abuse by police officers has created such a dangerous climate that to ensure proper change, we must defund the police and allocate resources to communities that can better protect its people.
		''' +newline_character + newline_character
	result.append(para3)

	if legislator.state is not None:
		para4 = '''
			As a constituent of %s's %s District, I want to make sure that my elected officials are taking the preventative measures necessary to ensure that incidents like this will not occur in the future. With this in mind, I ask the following:
		''' % (legislator.state, district_suffix(legislator.district)) + newline_character + newline_character
	else:
		para4 = '''
			As your constituent, I want to make sure that my elected officials are taking the preventative measures necessary to ensure that incidents like this will not occur in the future. With this in mind, I ask the following:
		''' + newline_character + newline_character
	result.append(para4)

	q1 = tab_character+bullet_character + 'Are you working to effectively ban the use of pepper spray and rubber bullets to de-escalate protests?' + newline_character
	result.append(q1)

	q2 = tab_character + bullet_character + 'Are you working to effectively suspend paid administrative leave for police officers under investigation?' + newline_character
	result.append(q2)

	q3 = tab_character + bullet_character + 'Are you working to withhold pensions and stop the rehiring of police involved in excessive force?' + newline_character
	result.append(q3)

	q4 = tab_character + bullet_character + 'Are you working to require the intervention of police officers if they witness another officer using excessive force? Will officers be reprimanded if they fail to intervene?' + newline_character
	result.append(q4)

	q5 = tab_character + bullet_character + 'Are you working to prioritize budgetary allocation to education, community health organizations, and affordable housing?' + newline_character
	result.append(q5)

	q6 = tab_character + bullet_character + 'Are you working to fund education programs that emphasize anti-racism and inclusion in diverse spaces?' + newline_character
	result.append(q6)

	q7 = tab_character + bullet_character + 'Are you working on increasing the legal accountability of police officers who use effective force? ' + newline_character + newline_character
	result.append(q7)

	para5='''
		The utter lack of monitoring police officers’ actions, combined with police departments’ excessive budget allocation,  has allowed the abuse of power for far too long. Communities are suffering and Black residents are extremely vulnerable to these brutalities.
	''' + newline_character + newline_character
	result.append(para5)

	para6 = '''
		There is a way to fix this injustice and it begins with creating communities that are well funded in comprehensive resources to protect these populations, while also penalizing police officers who use brute force or militarized forms of enforcement.
	'''  + newline_character + newline_character
	result.append(para6)

	para7 = '''
		Black lives have always mattered, do matter, and will continue to matter. I hope you will stand for justice at this time and work to heal a community that is actively hurting. Thank you for your time.
	'''  + newline_character + newline_character

	result.append(para7)

	sign_off = "Sincerely,"  + newline_character
	result.append(sign_off)

	signature = "%s" % (user_name)
	result.append(signature)

	single_email_string = ''.join(result)
	href_a = "mailto: %s?subject=[INSERT YOUR OWN SUBJECT] &amp;body=%s" % (legislator.email, single_email_string)

	return href_a


def get_state_abbreviation(rep_state):
	if "State Senate" in rep_state:
		rep_state= rep_state.replace("State Senate","")
	elif "General Assembly" in rep_state:
		rep_state= rep_state.replace("General Assembly","")
	elif "House of Representatives" in rep_state:
		rep_state= rep_state.replace("House of Representatives","")
	states= {
	    "AL": "Alabama",
	    "AK": "Alaska",
	    "AS": "American Samoa",
	    "AZ": "Arizona",
	    "AR": "Arkansas",
	    "CA": "California",
	    "CO": "Colorado",
	    "CT": "Connecticut",
	    "DE": "Delaware",
	    "DC": "District Of Columbia",
	    "FM": "Federated States Of Micronesia",
	    "FL": "Florida",
	    "GA": "Georgia",
	    "GU": "Guam",
	    "HI": "Hawaii",
	    "ID": "Idaho",
	    "IL": "Illinois",
	    "IN": "Indiana",
	    "IA": "Iowa",
	    "KS": "Kansas",
	    "KY": "Kentucky",
	    "LA": "Louisiana",
	    "ME": "Maine",
	    "MH": "Marshall Islands",
	    "MD": "Maryland",
	    "MA": "Massachusetts",
	    "MI": "Michigan",
	    "MN": "Minnesota",
	    "MS": "Mississippi",
	    "MO": "Missouri",
	    "MT": "Montana",
	    "NE": "Nebraska",
	    "NV": "Nevada",
	    "NH": "New Hampshire",
	    "NJ": "New Jersey",
	    "NM": "New Mexico",
	    "NY": "New York",
	    "NC": "North Carolina",
	    "ND": "North Dakota",
	    "MP": "Northern Mariana Islands",
	    "OH": "Ohio",
	    "OK": "Oklahoma",
	    "OR": "Oregon",
	    "PW": "Palau",
	    "PA": "Pennsylvania",
	    "PR": "Puerto Rico",
	    "RI": "Rhode Island",
	    "SC": "South Carolina",
	    "SD": "South Dakota",
	    "TN": "Tennessee",
	    "TX": "Texas",
	    "UT": "Utah",
	    "VT": "Vermont",
	    "VI": "Virgin Islands",
	    "VA": "Virginia",
	    "WA": "Washington",
	    "WV": "West Virginia",
	    "WI": "Wisconsin",
	    "WY": "Wyoming"
	}

	return list(states.keys())[list(states.values()).index(rep_state.strip())]


def generate_HTML_legislator_code(legislator, user_name):
	doc, tag, text = Doc().tagtext()
	with tag('div', klass='card'):
		if(legislator.chamber is not None):
			with tag('h4', style="font-weight: 600;"):
				rep_title = "%s" %(legislature_title(legislator.chamber))
				text(rep_title)
		with tag('h2'):
			rep_name = "%s" %(legislator.name)
			doc.asis(rep_name)
# 			text(rep_name)
		with tag('span', klass = 'metainfo',style="font-weight: 400"):
			if(legislator.state is not None):
				rep_state = "%s" %(get_state_abbreviation(legislator.state))
			else:
				rep_state = "N/A"
			text(rep_state)
			doc.asis("&ensp;&bull;&ensp;")
		with tag('span', klass='metainfo',style="font-weight: 400"):
			if legislator.chamber is not None:

				rep_legislature = "%s" % (legislature_in_html_response(legislator.chamber))
			else:
				rep_legislature = "N/A"
			text(rep_legislature)
			doc.asis("&ensp;&bull;&ensp;")
		with tag('span', klass = 'metainfo', style="font-weight: 500"):
			if legislator.district is not None:
				rep_district = "%s District" %(district_suffix(legislator.district))
			else:
				rep_district="N/A"
			text(rep_district)
		doc.asis("<br><br>")
		with tag('p', klass = 'email'):
			with tag('i', klass = "fa fa-envelope-o m-r-6 email"):
			 	text()
			doc.asis("&emsp;&emsp;")
			with tag('a', href = generate_email(legislator, user_name),klass="email",style=" font-family: 'Source Sans Pro', sans-serif;font-weight: 500;"):
				rep_email = "  %s" %(legislator.email)
				text(rep_email)
			doc.asis("&emsp;")
			with tag('span', klass="material-icons"):
			    text("call_made")
		if(legislator.phone1_type is not None):
			with tag('p',klass='phone'):
				with tag('i', klass = "fa fa-phone m-r-6"):
					text()
				doc.asis("&emsp;&emsp;")
				with tag('a',href="tel:" +legislator.phone1_num,style="font-weight: 500;"):
				    rep_phone1 = "  %s (%s)" %(legislator.phone1_num, legislator.phone1_type, )
				    text(rep_phone1)
		if(legislator.phone2_type is not None):
			with tag('p',klass='phone'):
				with tag('i', klass = "fa fa-phone m-r-6"):
					text()
				doc.asis("&emsp;&emsp;")
				with tag('a',href="tel:" +legislator.phone2_num,style="font-weight: 500;"):
				    rep_phone2 = "%s phone number: %s" %(legislator.phone2_type, legislator.phone2_num)
				    text(rep_phone2)
	result = doc.getvalue()
	final_result = result.replace("amp;","")
	return final_result


def trigger_search(user_zip,user_name):
    # **** QUERY FOR ZIPCODE SEARCH ****
    user_latitude, user_longitude = zipcode.fetch_lat_long(user_zip)
    if user_latitude is None or user_longitude is None:
        return "error: Apparently, you inputted a zipcode that does not exist in the US or we do not have it in our system"
    query = generate_location_query(user_latitude, user_longitude)

    # making API call to fetch the information on local politicians
    payload = {'query': query}
    request_result=requests.post('https://openstates.org/graphql', headers=headers, params=payload)
    while "quota exceeded" in request_result.text:
        # return "error: Site is currently down because of too much traffic. Sorry - please check back in a couple of hours!"
        request_result=requests.post('https://openstates.org/graphql', headers=headers, params=payload)
    rep_list = parse_location_response(request_result.text)

    # html tags are made with all of the content for each representative so that they can be ported over to website in Flask
    reps_html_tags =[]
    for rep in rep_list:
        rep_query = generate_person_query(rep.name)
        payload = {'query': rep_query}
        request_result=requests.post('https://openstates.org/graphql', headers=headers, params=payload)

        leg_response_parsed = parse_legislator_response(request_result.text, rep)
        if leg_response_parsed is "success":

	        html_tags = generate_HTML_legislator_code(rep,user_name)
	        reps_html_tags.append(html_tags)
        # buffers by one second to avoid the 1 request/second limit
        time.sleep(1)
    return reps_html_tags