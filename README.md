# Satellite Frequency Plan Scraper

A satellite frequency plan is a detailed chart/guide that outlines the allocation and usage of different frequency bands for satellite communication. These plans are available on [frequencyplansatellites](http://frequencyplansatellites.altervista.org) in PDF format. This solution implements a web crawler and a PDF scraper to extract transponder definitions and their associated fields, such as frequency, polarity, and bandwidth, into a JSON file.

## Getting Started 

### Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```shell
pip install -r requirements.txt
```

### Usage

```shell
python3 crawler.py && python3 main.py
```

## Solution

### Problem

* satellite frequency plans available online in PDF format
* PDFs are *not* meant to be machine-readable
* PDF -> structured output for programmatic usage

### Desired Output

```json
{
    "satellite": "Nilesat 102",
    "transponder": "31",
    "direction": "Uplink",
    "beam": "ME-NA Beam",
    "polarity": "Horizontal",
    "bandwidth": 33.0,
    "frequency": 17902880000,
    "band": "Ku"
}
```

Extract fields like frequency, polarity, and bandwidth for each transponder definition.

### Download PDFs

* navigate to satellite frequency plan site
* crawl site tree gathering all PDF links 
* download all PDFs to folder

```python
gathering pdf links...
657 PDF links found
downloaded ABS_1.pdf [1/657]
downloaded Koreasat_2.pdf [2/657]
downloaded Eutelsat_W75.pdf [3/657]
...
```

### Transponder Definitions

* extract all elements and their attributes using layout analysis
* sort elements into element types eg. (transponder, frequency, polarity) using attribute based filters
* plot elements on a graph
* for each transponder element, gather field elements using distance in x, y, or xy direction
* gather text from all elements into a transponder definition
* calculate derived fields
* save to output file for offline usage

```python
calculated transponders for ABS_1.pdf [1/657]
calculated transponders for Koreasat_2.pdf [2/657]
calculated transponders for Eutelsat_W75.pdf [3/657]
...
33836 transponder definitions found
```