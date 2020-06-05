# import graphene

# class Query(graphene.ObjectType):
#   hello = graphene.String(name=graphene.String(default_value="World"))

#   def resolve_hello(self, info, name):
#     return 'Hello ' + name

# schema = graphene.Schema(query=Query)
# result = schema.execute('{ hello }')
# print(result.data['hello']) # "Hello World"

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import requests
import zipcode

headers = {
	'X-API-KEY': '1a53fe15-6b43-4943-9812-e4dadd6b518f'
}

# code that takes zipcode given by user and returns the latitude and longitude necesssary to input into first query
user_latitude, user_longitude = zipcode.fetch_lat_long('08820')

#data can be dictionary or json

# BELOW IS HOW TO DYNAMICALLY SEARCH FOR POLITICIANS
'''
politican_name = "\"Catherine Nolan\""
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
'''


#BELOW IS CODE TO DYNAMICALLY SEARCH FOR POLITICIANS BASED ON LONGITUDE & LATITUDE
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


payload = {'query': query}
#params ? query = <string>
# body of your request
response=requests.post('https://openstates.org/graphql', headers=headers, params=payload)
# convert to dictionary
print(response.json())

person_dictionary = response.json()

# print(person_dictionary['node'])


# print(person_dictionary['email'])

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