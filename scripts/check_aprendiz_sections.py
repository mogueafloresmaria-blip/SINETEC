import re

with open('templates/aprendiz.html', 'r', encoding='utf-8') as f:
    text = f.read()

sections = re.findall(r'<section[^>]+id="([^"]+)"', text)
print("Sections found:", sections)

# Also check for any comments <!-- that are not properly closed before a tag
comments = re.findall(r'<!--.*?-->', text, re.DOTALL)
print(f"Total valid HTML comments: {len(comments)}")

# Find any <!-- that might not have a closing --> before the next section
for match in re.finditer(r'<!--(?:(?!-->).)*?<section', text, re.DOTALL):
    print("WARNING: unclosed comment before section at pos:", match.start())
    print(text[match.start():match.end()+40])
