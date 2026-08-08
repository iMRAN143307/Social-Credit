import csv
#import google.generativeai as genai
#from google.api_core import exceptions
import random

#genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

#model = genai.GenerativeModel('gemini-1.5-flash')

new_data = []

with open('new.csv', mode='r', newline="", encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        new_data.append(row)

for item in new_data:
    if len(item) > 2:
        said = item[2]

        item[2] = random.randint(-100, 100)

#for item in new_data:
#    if len(item) > 2:
#        said = item[2]
#
#        try:
#            response = model.generate_content(
#                f"Return an integer between -100 and 100 that is the social credit score of this message. Return ONLY the integer: {said}"
#            )
#
#            score = response.text.strip()
#            item[2] = (score)
#
#        except exceptions.ResourceExhausted as e:
#            print(f"Rate Limit Error: {e}")
#
#        except exceptions.ServiceUnavailable as e:
#            print(f"Connection Error: {e}")
#
#        except exceptions.InvalidArgument as e:
#            print(f"Bad Request Error: {e}")
#            item.append("-100")

with open("new.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(new_data)
