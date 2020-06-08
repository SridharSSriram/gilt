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

	# def to_String(self):
	# 	print(self.name + " " + self.email + " " + self.phone1_type + " " + self.phone1_num)

string = "AsmKarabinchak@njleg.org,note:District Office,type:voice,value:732-548-1406,chamber:[post:label:18,organization:name:Assembly,classification:lower,parent:name:New Jersey Legislature"

test = string.split(",")

karab = Representative('karab')

for substring in test:
	if "chamber" in substring:
		print("yikes")
		break
	
	elif("@" in substring):
		karab.email = substring
		continue
	
	segment = substring.split(":")

	if any(map(str.isdigit, segment[1])):
		segment[1] = segment[1].replace("-","")
	
	if(len(segment)>1):
		if('Office' in segment[1]):
			if(karab.phone1_type is None):
				karab.phone1_type = segment[1]
			else:
				karab.phone2_type=segment[1]
			continue
		
		elif (segment[1] =="voice"):
			continue
		else:
			if "Office" in karab.phone1_type and karab.phone1_num is None:
				karab.phone1_num = segment[1]
			else:
				karab.phone2_num = segment[1]

print(karab.email)
print(karab.phone1_type)
print(karab.phone1_num)
