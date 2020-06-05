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

# from .someSchema import SampleSchema

# client = Client(transport=RequestsHTTPTransport(
#      url='https://openstates.org/graphql', headers={'Authorization': '1a53fe15-6b43-4943-9812-e4dadd6b518f'}), schema=SampleSchema)

# X-API-KEY: 1a53fe15-6b43-4943-9812-e4dadd6b518f
# curl -H 'X-Api-Key: 1a53fe15-6b43-4943-9812-e4dadd6b518f' 'https://openstates.org/graphql' 
headers = {
	'X-API-KEY': '1a53fe15-6b43-4943-9812-e4dadd6b518f'
}

# request.post()
#data can be dictionary or json
query = """
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
"""


payload = {'query': query}
#params ? query = <string>
# body of your request
response=requests.post('https://openstates.org/graphql', headers=headers, params=payload)
# convert to dictionary
print(response.json())

person_dictionary = response.json()
print(person)


# _transport = RequestsHTTPTransport(
#     url= 'https://openstates.org/graphql',
#     use_json=True,
# )
# client = Client(
#     transport=_transport,
#     fetch_schema_from_transport=True,
# )

# print(client.execute(query))

# client = Client(
#     transport=sample_transport,
#     fetch_schema_from_transport=True,
# )

# query = gql('''
#     query getContinents {
#       continents {
#         code
#         name
#       }
#     }
# ''')

# client.execute(query)
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