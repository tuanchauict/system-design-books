from markdownify import markdownify as md
from markdownify import MarkdownConverter
from bs4 import BeautifulSoup, Tag


class MyConverter(MarkdownConverter):
    def convert_blockquote(self, el, text, convert_as_inline):
        custom_class = el.attrs.get('class', [])
        return f'<blockquote class="{' '.join(custom_class)}">{text}</blockquote>\n\n'
    
    def convert_h4(self, el, text, convert_as_inline=True):
        custom_class = el.attrs.get('class', [])
        if 'solution-bad' in custom_class or 'solution-good' in custom_class or 'solution-great' in custom_class:
            return f'<h4 class="{' '.join(custom_class)}">{text}</h4>\n\n'
        return f'#### {text}\n\n'
    
    def convert(self, el):
        if isinstance(el, Tag):
            if el.name == 'span' and 'MuiBox-root mui-1vu004u' in el.attrs.get('class', []):
                return f'`{el.text}`'
        return super().convert(el)

def parse_one(html: Tag):
    return MyConverter().convert(str(html))


def preprocess(html_str: str):
    soup = BeautifulSoup(html_str, 'html.parser')
    # Replace all <span class="MuiBox-root mui-1vu004u"> tag with `code` tag
    for span in soup.find_all('span', class_='MuiBox-root mui-1vu004u', recursive=True):
        span.name = 'code'
        span.attrs = {}
    # Replace all div with class `MuiBox-root mui-1ygn9bx` with blockquote and info class
    for div in soup.find_all('div', class_='MuiBox-root mui-1ygn9bx', recursive=True):
        div.name = 'blockquote'
        div.attrs = {'class': 'info'}
    # Replace all div with class `MuiBox-root mui-1147lff` with blockquote and tip class
    for div in soup.find_all('div', class_='MuiBox-root mui-1147lff', recursive=True):
        div.name = 'blockquote'
        div.attrs = {'class': 'tip'}
    # Replace all div with class `MuiBox-root mui-o9fqh4` or `MuiBox-root mui-8d9r5j` with blockquote and warning class
    for div in soup.find_all('div', class_='MuiBox-root mui-o9fqh4', recursive=True):
        div.name = 'blockquote'
        div.attrs = {'class': 'warning'}
    for div in soup.find_all('div', class_='MuiBox-root mui-8d9r5j', recursive=True):
        div.name = 'blockquote'
        div.attrs = {'class': 'warning'}
    
    
    
    # Remove div with class `MuiGrid-root MuiGrid-item mui-1wxaqej` since this is the image caption which is already included in the image alt text
    for div in soup.find_all('div', class_='MuiGrid-root MuiGrid-item mui-1wxaqej'):
        div.decompose()
    
    # Remove all button
    for button in soup.find_all('button'):
        button.decompose()
        
    # Replace all div with class `MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded Mui-expanded MuiAccordion-gutters mui-ifi55z` with blockquote and solution.bad class
    for div in soup.find_all('div', class_='MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded Mui-expanded MuiAccordion-gutters mui-ifi55z'):
        div.name = 'blockquote'
        div.attrs = {'class': 'solution.bad'}
    # Replace all div with class `MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded MuiAccordion-gutters mui-11r69q9` with blockquote and solution.good class
    for div in soup.find_all('div', class_='MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded MuiAccordion-gutters mui-11r69q9'):
        div.name = 'blockquote'
        div.attrs = {'class': 'solution.good'}
    # Replace all div with class `MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded MuiAccordion-gutters mui-11r69q9` with blockquote and solution.great class
    for div in soup.find_all('div', class_='MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded MuiAccordion-gutters mui-11r69q9'):
        div.name = 'blockquote'
        div.attrs = {'class': 'solution.great'}
        
    # Replace all div with with id `panel1bh-header` with h4 tag
    for div in soup.select('#panel1bh-header'):
        div.name = 'h4'
        if 'mui-1ev8i4f' in div.attrs.get('class', []):
            div.attrs = {'class': 'solution-bad'}
        elif 'mui-guv1gb' in div.attrs.get('class', []):
            div.attrs = {'class': 'solution-good'}
        elif 'mui-3ujfba' in div.attrs.get('class', []):
            div.attrs = {'class': 'solution-great'}
        
    return soup

def parse_all(html_str: str):
    soup = preprocess(html_str)
        
    children = soup.find(True).find_all(recursive=False)
    
    with open('output.md', 'w') as f:
        for child in children[:]:
            print('-------------------')
            print(child)
            print(child.attrs.get('class'))
            print(">")
            print(parse_one(child))
            f.write(parse_one(child))
            f.write('\n')

if __name__ == '__main__':
    with open('sample.html', 'r') as f:
        html_str = f.read()
        parse_all(html_str)
