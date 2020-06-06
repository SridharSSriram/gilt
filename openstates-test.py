import requests
import zipcode

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

# **** QUERY FOR ZIPCODE SEARCH ****
user_latitude, user_longitude = zipcode.fetch_lat_long('08820')
query = generate_location_query(user_latitude, user_longitude)

# makning API call to fetch the information on local politicians
payload = {'query': query}
response=requests.post('https://openstates.org/graphql', headers=headers, params=payload)

stored_tings = response.text
ting = stored_tings.replace("}","")
ting = ting.replace("\"","")
ting = ting.split('{')

for i in ting:
	print(i)

'''
Plan for extracting text:

1. Take response as text
2. Split text into lines
3. Use regex to extract after names, classification, organization
4. Create dictionary of people
'''



# **** QUERY FOR PERSON SEARCH ****
# politican_name = "Catherine Nolan"
# query = generate_person_query(politican_name)


# convert to dictionary

# need to reconcile legislator names!!!
# print(response.json())
# for item in response.text.:
# 	print(item)
# person = {"name": politican_name}

# stored_tings = response.text
# ting = stored_tings.replace("}","")
# ting = ting.replace("\"","")
# ting = ting.split('{')

# for i in ting:
# 	print(i)


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