import requests

code = '''age = 20
if age >= 18:
    print("You are eligible to vote!")
else:
    print("You are not eligible to vote.")'''

r = requests.post('http://127.0.0.1:5000/run', json={'code': code})
print(r.json())

