import hashlib
from markdownify import markdownify as md
from markdownify import MarkdownConverter
from bs4 import BeautifulSoup, Tag
from os import path
from pygments.lexers import guess_lexer, ClassNotFound
import time


class MyConverter(MarkdownConverter):
    def convert_blockquote(self, el, text, convert_as_inline):
        custom_class = el.attrs.get('class', [])
        text.strip()
        return f':::{' '.join(custom_class)}\n{text}\n:::\n\n'
    
    # def convert_h4(self, el, text, convert_as_inline=True):
    #     custom_class = el.attrs.get('class', [])
    #     if 'solution-bad' in custom_class or 'solution-good' in custom_class or 'solution-great' in custom_class:
    #         return f'<h4 class="{' '.join(custom_class)}">{text}</h4>\n\n'
    #     return f'#### {text}\n\n'
    
    def convert(self, el):
        if isinstance(el, Tag):
            if el.name == 'span' and 'MuiBox-root mui-1vu004u' in el.attrs.get('class', []):
                return f'`{el.text}`'
        return super().convert(el)
    
    def convert_img(self, el, text, convert_as_inline):
        # if the src starts with `/`, fix the url with `https://www.hellointerview.com/`
        src = el.attrs.get('src', '')
        if src.startswith('/'):
            src = f'https://www.hellointerview.com{src}'
            el.attrs['src'] = src
        return super().convert_img(el, text, convert_as_inline)
    
    def convert_pre(self, el, text, convert_as_inline):
        code = el.text
        return f'\n```{self.guess_language(code)}\n{code}\n```\n\n'
        
    def guess_language(self, code):
        code = code.strip()
        if 'def ' in code:
            return 'python'
        if "function " in code:
            return 'javascript'
        if 'SELECT ' in code:
            return 'sql'
        if code.startswith('{') and code.endswith('}'):
            return 'json'
        
        try:
            lexer = guess_lexer(code)
            return lexer.aliases[0]
            print(lexer.aliases)
        except ClassNotFound:
            return ''
    
class GitHubMarkdownConverter(MarkdownConverter):
    def convert_blockquote(self, el, text, convert_as_inline):
        custom_class = ' '.join(el.attrs.get('class', []))
        prefix = {
            'info': '[!NOTE]',
            'tip': '[!TIP]',
            # 'problem': '[!PROBLEM]',
            'warning': '[!CAUTION]',
            'solution.bad': '[!WARNING]',
            'solution.good': '[!IMPORTANT]',
            'solution.great': '[!IMPORTANT]'
        }
        
        text = super().convert_blockquote(el, text, convert_as_inline)
        return f'\n> {prefix.get(custom_class, "")}{text}'

def parse_one(converter: MarkdownConverter, html: Tag):
    return converter.convert(str(html))


def preprocess(file_path: str, html_str: str):
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
    
    
    # Replace all div with class `MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded Mui-expanded MuiAccordion-gutters mui-ifi55z` with blockquote and solution.bad class
    for div in soup.find_all('div', class_='MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded MuiAccordion-gutters mui-ifi55z'):
        div.name = 'blockquote'
        div.attrs = {'class': 'solution-bad'}
    # Replace all div with class `MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded MuiAccordion-gutters mui-nhbct3` with blockquote and solution.good class
    for div in soup.find_all('div', class_='MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded MuiAccordion-gutters mui-nhbct3'):
        div.name = 'blockquote'
        div.attrs = {'class': 'solution-good'}
    # Replace all div with class `MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded MuiAccordion-gutters mui-11r69q9` with blockquote and solution.great class
    for div in soup.find_all('div', class_='MuiPaper-root MuiPaper-elevation MuiPaper-rounded MuiPaper-elevation0 MuiAccordion-root MuiAccordion-rounded MuiAccordion-gutters mui-11r69q9'):
        div.name = 'blockquote'
        div.attrs = {'class': 'solution-great'}
        
    # Replace all div with class `MuiBox-root mui-1fz7ihe` with blockquote and problem class
    for div in soup.find_all('div', class_='MuiBox-root mui-1fz7ihe'):
        div.name = 'blockquote'
        div.attrs = {'class': 'problem'}
        
    # Replace all div with class `MuiTypography-root MuiTypography-body1 mui-1p1f0ag` with p tag
    for div in soup.find_all('div', class_='MuiTypography-root MuiTypography-body1 mui-1p1f0ag'):
        div.name = 'p'
        
    # Replace all div with with id `panel1bh-header` with h4 tag
    for div in soup.select('#panel1bh-header'):
        div.name = 'h4'
        if 'mui-1ev8i4f' in div.attrs.get('class', []):
            div.attrs = {'class': 'solution-bad'}
        elif 'mui-guv1gb' in div.attrs.get('class', []):
            div.attrs = {'class': 'solution-good'}
        elif 'mui-3ujfba' in div.attrs.get('class', []):
            div.attrs = {'class': 'solution-great'}
        
    # Convert all Approach and Challenge to bold
    for div in soup.find_all(class_='MuiTypography-root MuiTypography-body1 mui-1quhbks', recursive=True):
        div.name = 'strong'
        
    # Remove all svg with class
    for svg in soup.select('svg[class]'):
        svg.decompose()
    # Remove all svg with attribute `data-slot="icon"`
    for svg in soup.find_all('svg', attrs={'data-slot': 'icon'}):
        svg.decompose()
    
    # Replace all svg without class with img tag and extract the svg content to file with the name of the input file + index of the svg tag
    image_dir = path.dirname(file_path)
    image_prefix = path.basename(file_path).split('.')[0]
    for i, svg in enumerate(soup.find_all('svg', class_=False, recursive=True), start=1):
        view_box = svg.attrs.get('viewbox', '0 0 0 0')
        # If svg does not have width and height attributes, set from viewBox
        if 'width' not in svg.attrs:
            svg.attrs['width'] = view_box.split(' ')[2]
        if 'height' not in svg.attrs:
            svg.attrs['height'] = view_box.split(' ')[3]
        svg_name = f'{image_prefix}_{i:02}.svg'
        with open(f'{image_dir}/{svg_name}', 'w') as f:
            f.write(str(svg))
        img = soup.new_tag('img')
        img.attrs = {'src': svg_name}
        svg.replace_with(img)
    
    # Read all items by class `MuiGrid-root MuiGrid-container MuiGrid-direction-xs-column mui-1tdxmx0`, inside this has 2 elements, 1st is the image under `object` tag, 2nd is the caption
    # Replace this with img tag with src point to `data` attribute of the object tag, alt is the caption
    for i, div in enumerate(soup.find_all('div', class_='MuiTypography-root MuiTypography-body1 mui-1qj780c', recursive=True), start=1):
        object_tag = div.find('object')
        if not object_tag:
            continue
        # caption is from 'MuiGrid-root MuiGrid-item mui-1wxaqej' class
        caption = div.find('div', class_='MuiGrid-root MuiGrid-item mui-1wxaqej')
        
        caption_text = caption.select_one('span').text.strip() if caption else ''
        img = soup.new_tag('img')
        img.attrs = {'src': object_tag.attrs.get('data', ''), 'alt': caption_text}
        div.replace_with(img)
        
    # Remove all button
    for button in soup.find_all('button'):
        button.decompose()
        
    # Remove div with class `MuiGrid-root MuiGrid-item mui-1wxaqej` since this is the image caption which is already included in the image alt text
    for div in soup.find_all('div', class_='MuiGrid-root MuiGrid-item mui-1wxaqej'):
        div.decompose()
        
    
    return soup

def parse_all(converter: MarkdownConverter, file_path: str):
    with open(file_path, 'r') as f:
        html_str = f.read()
    soup = preprocess(file_path, html_str)
    
    root = soup.body if not soup.select_one('#markdown') else soup.select_one('#markdown')
    # print(soup.body)
    children = [c for c in root.children if isinstance(c, Tag)]
    # print(children[0])
    metadata_node = children[0]
    title = metadata_node.find('h1').text
    
    author = metadata_node.select_one('.mui-ltrqv0')
    difficulty = metadata_node.select_one('.mui-su24yt')
    
    output_file = file_path.replace('.html', '.md')
    with open(output_file, 'w') as f:
        f.write(f'<!-- {get_hash(file_path)} -->\n')
        
        f.write(f'{title}\n')
        f.write('=' * len(title))
        if author or difficulty:
            f.write('\n\n```')
            if author:
                f.write(f'\nAuthor: {author.text}')
            if difficulty:
                f.write(f'\nLevel : {difficulty.text.upper()}')
            f.write('\n```\n\n')
        
        for child in children[1:]:
            # print('-------------------')
            # print(parse_one(converter, child))
            f.write(parse_one(converter, child))
            f.write('\n\n')
            

def should_parse(filepath: str):
    if not filepath.endswith('.html'):
        return False
    html_filepath = filepath
    if not os.path.exists(html_filepath.replace('.html', '.md')):
        return True
    
    hash = get_hash(html_filepath)
    
    with open(html_filepath.replace('.html', '.md'), 'r') as f:
        if f.readline().strip() != f'<!-- {hash} -->':
            return True
    return False
    

def get_hash(file_path: str):
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


if __name__ == '__main__':
    converter = MyConverter()
    import os
    # Retrieve all html files in the raw folder including subfolders and parse them
    for root, dirs, files in os.walk('./raw'):
        for file in files:
            file_path = os.path.join(root, file)
            if not should_parse(file_path):
                continue
            
            print("=" * 100)
            file_path = os.path.join(root, file)
            print(file_path)
            try:
                parse_all(converter, file_path)
            except Exception as e:
                print(file_path)
                raise e
    
    
