from math import dist, isclose
from statistics import mean
import json
import re
import matplotlib
import matplotlib.pyplot as plt
import pdfplumber

matplotlib.use('TkAgg')

class Element:
    def __init__(self, page, element):
        self.page = page
        self.x = mean([element['x0'], element['x1']])
        self.y = mean([element['y0'], element['y1']])
        self.height = element['height']
        self.width = element['width']
        self.text = element['text'].strip() if element.get('text') else None
        self.color = element.get('non_stroking_color')
    
    def closest(self, element_type, x_comparison = None, y_comparison = None):
        elements = {
            'satellite': self.page.satellites,
            'transponder': self.page.transponders,
            'direction': self.page.directions,
            'beam': self.page.beams,
            'polarity': self.page.polarities,
            'bandwidth': self.page.bandwidths,
            'frequency': self.page.frequencies,
            'box': self.page.boxes
        }

        elements = elements[element_type]

        if x_comparison == 'equal':
            elements = list(filter(lambda x: isclose(x.x, self.x, rel_tol=0.05), elements))
        elif x_comparison == 'greater':
            elements = list(filter(lambda x: x.x > self.x, elements))
        elif x_comparison == 'lesser':
            elements = list(filter(lambda x: x.x < self.x, elements))

        if y_comparison == 'same':
            elements = list(filter(lambda x: isclose(x.y, self.y, rel_tol=0.05), elements))
        elif y_comparison == 'greater':
            elements = list(filter(lambda x: x.y > self.y, elements))
        elif y_comparison == 'lesser':
            elements = list(filter(lambda x: x.y < self.y, elements))

        if not elements:
            return None

        element = min(elements, key=lambda x: dist([self.x, self.y], [x.x, x.y]))

        return element

class Page:
    def __init__(self, page):
        self.satellites = [Element(self, element) for element in page.filter(lambda x: x['height'] == 48).textboxhorizontals]
        self.boxes = [Element(self, element) for element in page.filter(lambda x: x.get('fill') == True).rects]
        # transponder can also be vertical (T C N)
        self.transponders = [Element(self, element) for element in page.filter(lambda x: x['height'] > 8 and x['width'] < 25 and x.get('text') and not any(field in x['text'].strip().lower() for field in ['horizontal', 'vertical', 'lhcp', 'rhcp', 'left', 'right', 'beam', 's', 'north', 'south', 'east', 'west', 'middle', 'central', 'global', 'america', 'europe', 'asia', 'australia', 'africa', 'indochina'])).textboxhorizontals]
        self.transponders += [Element(self, element) for element in page.filter(lambda x: x['height'] > 8 and x['width'] < 25 and x.get('text') and x['text'].strip() == 'T C N').textboxverticals]
        self.directions = [Element(self, element) for element in page.filter(lambda x: x['height'] == 24 and x.get('text') and 'link' in x['text']).textboxhorizontals]
        self.beams = [Element(self, element) for element in page.filter(lambda x: x['height'] == 12 and x.get('text') and 'note' not in x['text'].strip().lower() and any(beam in x['text'].strip().lower() for beam in ['beam', 's', 'north', 'south', 'east', 'west', 'middle', 'central', 'global', 'america', 'europe', 'asia', 'australia', 'africa', 'indochina', 'brazil', 'argentina', 'chile', 'uruguay', 'paraguay'])).textboxhorizontals]
        self.polarities = [Element(self, element) for element in page.filter(lambda x: x['height'] == 12 and x.get('text') and x['text'].strip().lower() in ['horizontal', 'vertical', 'lhcp', 'rhcp', 'left', 'right']).textboxhorizontals]
        # some have (correction?) bandwidths which are right next to previous
        self.bandwidths = [Element(self, element) for element in page.filter(lambda x: x['height'] == 8 and x.get('text') and re.search(r'\d', x['text'])).textboxhorizontals]
        # some have (correction?) frequencies which are right next to previous and in between boxes
        self.frequencies = [Element(self, element) for element in page.textboxverticals]

class Pdf:
    laparams = { 'line_overlap': 0.5, 'char_margin': 0.75, 'word_margin': 0.1, 'line_margin': 0.01, 'boxes_flow': 0.5, 'detect_vertical': True, 'all_texts': False }

    def __init__(self, path):
        pdf = pdfplumber.open(path, laparams=self.laparams)
        self.pages = [Page(page) for page in pdf.pages]

    def show(self):
        for index, page in enumerate(self.pages):
            fig, ax = plt.subplots(num=f'Page {index + 1} Elements')
            def plot(element):
                ax.plot(element.x, element.y, marker='o', markersize=4, color='blue')
                ax.annotate(element.text, (element.x, element.y))
            for satellite in page.satellites: plot(satellite)
            for transponder in page.transponders: plot(transponder)
            for direction in page.directions: plot(direction)
            for beam in page.beams: plot(beam)
            for polarity in page.polarities: plot(polarity)
            for bandwidth in page.bandwidths: plot(bandwidth)
            for frequency in page.frequencies: plot(frequency)
            ax.set_title(f'Page {index + 1}')
        return plt.show()