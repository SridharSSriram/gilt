import requests
import zipcode
import time

headers = {
	'X-API-KEY': '1a53fe15-6b43-4943-9812-e4dadd6b518f'
}

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

	rep_array ={}
	for iterator in major_tings:
		new_rep ={}
		new_string = iterator.replace("name:","").replace("chamber:[post:label:","").replace("organization:","").replace("classification:","").replace("parent:","")
		rep_info = new_string.split(",")
		# initiates a new representative dictionary with following properties: district, legislature, chamber, and parent legislature
		new_rep['district'] = rep_info[1]
		new_rep['legislature'] = rep_info[2]
		new_rep['chamber']= rep_info[3]
		new_rep['parent legislature'] = rep_info[4]

		# adds the representative information to rep_array as an entry with the name of representative as the key 
		rep_array[rep_info[0]] = new_rep
	
	return rep_array

# def parse_legislator_response(response_text):
	#SLEEP ON THIS AND COME BACK TO IT
	# print(response_text)
	# zipcode_response_string = response_text.replace("}","").replace("{","").replace("\"","").replace("]","")
	# # zipcode_response = zipcode_response_string.split("email,value:")
	# # print(zipcode_response_string)

	# start = zipcode_response_string.find("email,value:") + len("email,value:")
	# sub_test = zipcode_response_string[start:]
	# print(sub_test)
	# test = sub_test.split(",")
	# for i in test:
	# 	print(i)
	# print(test[0])
	# end = zipcode_response_string.find("Office,")
	# substring = zipcode_response_string[start:end]
	# print("\n")
	# print(substring)
	
	# zipcode_response = zipcode_response.split("email,value:")

	# print(zipcode_response)

	# skips the first portion because of neglible text
	# major_tings = zipcode_response[1:]

	# rep_array ={}
	# for iterator in major_tings:

	# 	print(iterator)
	# 	new_rep ={}
	# 	new_string = iterator.replace("name:","").replace("chamber:[post:label:","").replace("organization:","").replace("classification:","").replace("parent:","")
	# 	rep_info = new_string.split(",")
	# 	# initiates a new representative dictionary with following properties: district, legislature, chamber, and parent legislature
	# 	new_rep['district'] = rep_info[1]
	# 	new_rep['legislature'] = rep_info[2]
	# 	new_rep['chamber']= rep_info[3]
	# 	new_rep['parent legislature'] = rep_info[4]

	# 	# adds the representative information to rep_array as an entry with the name of representative as the key 
	# 	rep_array[rep_info[0]] = new_rep
	
	# return rep_array


# **** QUERY FOR ZIPCODE SEARCH ****
user_latitude, user_longitude = zipcode.fetch_lat_long('11207')
query = generate_location_query(user_latitude, user_longitude)

# makning API call to fetch the information on local politicians
payload = {'query': query}
request_result=requests.post('https://openstates.org/graphql', headers=headers, params=payload)


rep_array = parse_location_response(request_result.text)

for rep_name in rep_array.keys():
	# print(rep_name)      
	rep_query = generate_person_query(rep_name)
	payload = {'query': rep_query}
	request_result=requests.post('https://openstates.org/graphql', headers=headers, params=payload)
	# parse_legislator_response(request_result.text)

	# buffers by one second to avoid the 1 request/second limit
	time.sleep(1)

'''
Plan for extracting text:

1. Take response as text
2. Split text into lines
3. Use regex to extract after names, classification, organization
4. Create dictionary of people
'''


'''
Below is to search for legislators that represent a given area - this uses latitude/longitude
{
  people(latitude: 40.7460022, longitude: -73.9584642, first: 100) {
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

******* BELOW IS OUTPUT OF ABOVE QUERY  *******
{
  "data": {
    "people": {
      "edges": [
        {
          "node": {
            "name": "Michael Gianaris",
            "chamber": [
              {
                "post": {
                  "label": "12"
                },
                "organization": {
                  "name": "Senate",
                  "classification": "upper",
                  "parent": {
                    "name": "New York Legislature"
                  }
                }
              }
            ]
          }
        },
        {
          "node": {
            "name": "Catherine Nolan",
            "chamber": [
              {
                "post": {
                  "label": "37"
                },
                "organization": {
                  "name": "Assembly",
                  "classification": "lower",
                  "parent": {
                    "name": "New York Legislature"
                  }
                }
              }
            ]
          }
        }
      ]
    }
  }
}
'''


'''

Get information about a specific legislator:

Need to iterate through the list of people provided from above and provided the following:

Below is an example of how we would use each person found from above query 

{
  people(first: 2, name:"Catherine Nolan") {
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



******** BELOW IS THE OUTPUT OF THE ABOVE QUERY ************
{
  "data": {
    "people": {
      "edges": [
        {
          "node": {
            "name": "Catherine Nolan",
            "contactDetails": [
              {
                "note": "Capitol Office",
                "type": "address",
                "value": "LOB 739;Albany, NY 12248"
              },
              {
                "note": "Capitol Office",
                "type": "email",
                "value": "NolanC@nyassembly.gov"
              },
              {
                "note": "Capitol Office",
                "type": "voice",
                "value": "518-455-4851"
              },
              {
                "note": "District Office",
                "type": "address",
                "value": "47-40 21 Street Room 810;Long Island City, NY 11101"
              },
              {
                "note": "District Office",
                "type": "voice",
                "value": "718-784-3194"
              },
              {
                "note": "District Office",
                "type": "fax",
                "value": "718-472-0648"
              }
            ],
            "chamber": [
              {
                "post": {
                  "label": "37"
                },
                "organization": {
                  "name": "Assembly",
                  "classification": "lower",
                  "parent": {
                    "name": "New York Legislature"
                  }
                }
              }
            ]
          }
        }
      ]
    }
  }
}
'''