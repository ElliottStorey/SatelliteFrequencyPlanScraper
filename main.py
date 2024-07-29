import os
import json
from pdf import Pdf

bands = {
    (30, 300): 'ELF',
    (300, 3000): 'VF',
    (3 * 10**3, 30 * 10**3): 'VLF',
    (30 * 10**3, 300 * 10**3): 'LF',
    (0.3 * 10**6, 3 * 10**6): 'MF',
    (3 * 10**6, 30 * 10**6): 'HF',
    (30 * 10**6, 1000 * 10**6): 'VHF',
    (1 * 10**9, 2 * 10**9): 'L',
    (2 * 10**9, 3.7 * 10**9): 'S',
    (3.7 * 10**9, 8 * 10**9): 'C',
    (8 * 10**9, 12.4 * 10**9): 'X',
    (12.4 * 10**9, 18 * 10**9): 'Ku',
    (18 * 10**9, 26.5 * 10**9): 'K',
    (26.5 * 10**9, 40 * 10**9): 'Ka'
}

def get_transponders(path):
    transponders = []
    pdf = Pdf(path)
    # pdf.show()
    for page in pdf.pages:
        bandwidths = {}
        for bandwidth in page.bandwidths:
            try:
                bandwidths[bandwidth.closest('box').width] = float(bandwidth.text.replace(',', '.'))
            except:
                continue
        for transponder in page.transponders:
            satellite = transponder.closest('satellite', y_comparison='greater')
            satellite = getattr(satellite, 'text', None)
            if not satellite: continue

            direction = transponder.closest('direction', y_comparison='greater')
            direction = getattr(direction, 'text', None)
            if not direction: continue

            beam = transponder.closest('beam', y_comparison='greater')
            beam = getattr(beam, 'text', None)

            polarity = transponder.closest('polarity', x_comparison='lesser', y_comparison='equal')
            polarity = getattr(polarity, 'text', None)

            box = transponder.closest('box', x_comparison='equal', y_comparison='equal')
            if not box: continue

            frequency = transponder.closest('frequency', x_comparison='equal')
            if not frequency: continue

            try:
                frequency = float(frequency.text.replace(',', '.')) * 10**6
            except:
                continue

            bandwidth = bandwidths.get(box.width)

            band = None
            for frequency_range, name in bands.items():
                if frequency_range[0] < frequency < frequency_range[1]: band = name

            if not band: continue
            
            if any(transponder.text == field for field in [satellite, direction, beam, polarity, bandwidth, frequency]): continue

            transponders.append({
                'satellite': satellite,
                'transponder': transponder.text,
                'direction': direction,
                'beam': beam,
                'polarity': polarity,
                'bandwidth': bandwidth,
                'frequency': int(frequency),
                'band': band
            })
    return transponders

pdfs_dir = 'pdfs'
if not os.path.exists(pdfs_dir): raise Exception('PDF directory does not exist')
pdfs = os.listdir(pdfs_dir)

transponders = []

for index, pdf in enumerate(pdfs):
    path = f'{pdfs_dir}/{pdf}'
    transponders += get_transponders(path)
    print(f'calculated transponders for {pdf} [{index + 1}/{len(pdfs)}]')

with open('transponders.json', 'w') as file:
    file.write(json.dumps(transponders, indent=2))

print(len(transponders), 'transponder definitions found')