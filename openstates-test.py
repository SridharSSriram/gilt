import requests
import zipcode
import time

headers = {
	'X-API-KEY': '1a53fe15-6b43-4943-9812-e4dadd6b518f'
}

# class of basic fields for local representative
class Representative:
	def __init__(self,name):
		self.name = name
		self.district = None
		self.chamber = None
		self.email = None
		self.phone1_type = None
		self.phone1_num = None
		self.phone2_type = None
		self.phone2_num = None
		self.state_legislature = None

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
		# initiates a new representative dictionary with following properties: district, legislature, chamber, and parent legislature
		current_representative = Representative(rep_info[0])

		current_representative.district = rep_info[1]
		current_representative.chamber = rep_info[2]
		# new_rep['chamber']= rep_info[3]
		current_representative.legislature = rep_info[4]
		rep_list.append(current_representative)
		# adds the representative information to rep_array as an entry with the name of representative as the key 
		# rep_array[rep_info[0]] = new_rep
	
	return rep_list


def parse_legislator_response(response_text, current_representative):

	zipcode_response_string = response_text.replace("}","").replace("{","").replace("\"","").replace("]","")

	start = zipcode_response_string.find("email,value:") + len("email,value:")
	sub_test = zipcode_response_string[start:]
	# print("DIS D SUBTEST", sub_test)
	test = sub_test.split(",")

	for substring in test:
		if "chamber" in substring:
			print("yikes")
			break
		
		elif("@" in substring):
			current_representative.email = substring
			continue
		
		segment = substring.split(":")

		if any(map(str.isdigit, segment[1])):
			segment[1] = segment[1].replace("-","")
		
		if(len(segment)>1):
			if('Office' in segment[1]):
				if(current_representative.phone1_type is None):
					current_representative.phone1_type = segment[1]
				else:
					current_representative.phone2_type=segment[1]
				continue
			
			elif (segment[1] =="voice"):
				continue
			else:
				if "Office" in current_representative.phone1_type and current_representative.phone1_num is None:
					current_representative.phone1_num = segment[1]
				else:
					current_representative.phone2_num = segment[1]



# **** QUERY FOR ZIPCODE SEARCH ****
user_latitude, user_longitude = zipcode.fetch_lat_long('08901')
query = generate_location_query(user_latitude, user_longitude)

# makning API call to fetch the information on local politicians
payload = {'query': query}
request_result=requests.post('https://openstates.org/graphql', headers=headers, params=payload)


rep_list = parse_location_response(request_result.text)

for rep in rep_list:
	print(rep.name)      
	rep_query = generate_person_query(rep.name)
	payload = {'query': rep_query}
	request_result=requests.post('https://openstates.org/graphql', headers=headers, params=payload)
	parse_legislator_response(request_result.text, rep)
	print(rep.name, rep.phone1_type,rep.phone1_num, rep.email, rep.chamber)

	# buffers by one second to avoid the 1 request/second limit
	time.sleep(1)
