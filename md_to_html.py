import markdown
import os

def md_to_html(md):
    return markdown.markdown(md)

# Convert all .md files from task1 and task1/drivers to .html and save them in task2 and task2/drivers
for path in ['task1', 'task1/drivers']:
    for file in os.listdir(path):
        if file.endswith('.md'):
            with open(f'{path}/{file}', 'r') as f:
                html = md_to_html(f.read())
            new_path = path.replace('task1', 'task2')
            with open(f'{new_path}/{file.replace(".md", ".html")}', 'w') as f:
                f.write(html)