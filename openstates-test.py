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

	def print_values(self):
		print("name: ", self.name)
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

		current_representative.district = rep_info[1]
		current_representative.chamber = rep_info[2]
		# new_rep['chamber']= rep_info[3]
		current_representative.legislature = rep_info[4]
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

	current_representative.phone1_type, current_representative.phone1_num = phone1_info[0], phone1_info[1]
	current_representative.phone2_type, current_representative.phone2_num = phone2_info[0], phone2_info[1]


def main(user_zip):
	# **** QUERY FOR ZIPCODE SEARCH ****
	user_latitude, user_longitude = zipcode.fetch_lat_long(user_zip)
	query = generate_location_query(user_latitude, user_longitude)

	# making API call to fetch the information on local politicians
	payload = {'query': query}
	request_result=requests.post('https://openstates.org/graphql', headers=headers, params=payload)


	rep_list = parse_location_response(request_result.text)

	for rep in rep_list:
		rep_query = generate_person_query(rep.name)
		payload = {'query': rep_query}
		request_result=requests.post('https://openstates.org/graphql', headers=headers, params=payload)
		parse_legislator_response(request_result.text, rep)
		rep.print_values()

		# buffers by one second to avoid the 1 request/second limit
		time.sleep(1)

if __name__ == "__main__":
	main('08527')
