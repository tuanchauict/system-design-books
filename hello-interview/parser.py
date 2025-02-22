from markdownify import markdownify as md
from markdownify import MarkdownConverter
from bs4 import BeautifulSoup, Tag
from os import path

class MyConverter(MarkdownConverter):
    def convert_blockquote(self, el, text, convert_as_inline):
        custom_class = el.attrs.get('class', [])
        return f':::{' '.join(custom_class)}{text}:::\n\n'
    
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
    
    # Remove div with class `MuiGrid-root MuiGrid-item mui-1wxaqej` since this is the image caption which is already included in the image alt text
    for div in soup.find_all('div', class_='MuiGrid-root MuiGrid-item mui-1wxaqej'):
        div.decompose()
    
    # Remove all button
    for button in soup.find_all('button'):
        button.decompose()
    
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
    
    # with open('output.html', 'w') as f:
    #     f.write(str(soup))
    
    return soup

def parse_all(converter: MarkdownConverter, file_path: str):
    with open(file_path, 'r') as f:
        html_str = f.read()
    soup = preprocess(file_path, html_str)
    
    # print(soup.body)
    children = [c for c in soup.body.children if isinstance(c, Tag)]
    print(children[0])
    metadata_node = children[0]
    title = metadata_node.find('h1').text
    
    author = metadata_node.select_one('.mui-ltrqv0')
    difficulty = metadata_node.select_one('.mui-su24yt')
    
    output_file = file_path.replace('.html', '.md')
    with open(output_file, 'w') as f:
        
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
            print('-------------------')
            print(parse_one(converter, child))
            f.write(parse_one(converter, child))
            f.write('\n\n')

if __name__ == '__main__':
    import os
    # Retrieve all html files in the raw folder including subfolders and parse them
    for root, dirs, files in os.walk('./raw'):
        for file in files:
            if file.endswith('.html'):
                print("=" * 100)
                file_path = os.path.join(root, file)
                print(file_path)
                try:
                    parse_all(MyConverter(), file_path)
                except Exception as e:
                    print(file_path)
                    raise e
    
    
