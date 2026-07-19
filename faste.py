import re


pattern = re.compile( )

with open("texto.txt", 'r') as file:
    for line in file:
        match = re.match(pattern, line.removeprefix("connection:").strip())
        print(match.group("garbage"))