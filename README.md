# LSB_RGB
LSB embeddor and extractor. Using three RGB colors.

This tools allows to embedd text or files into PNG files, using Lest Significant Bit technique. 

# Installation
This tool uses Pillow image library. Install with : 
```shell
pip install Pillow
```

# Usage
Help : 
```
  positional arguments:
    image                 Image to embed/extract data
  
  options:
    -h, --help            show this help message and exit
    -t TEXT, --text TEXT  Text to be embedded
    -f FILE, --file FILE  File to be embedded (.txt in plain text, other in binary)
    -d [{horizontal,vertical,diagonal}], --direction [{horizontal,vertical,diagonal}]
                          Direction to embed with
    -o OUTPUT, --output OUTPUT
                          File to output extracted data (.txt in plain text, other in binary)
```

# Examples
## Embed text 
```python
python LSB.py image.png -t 'Secret message'
```

## Embed file 
```python
python LSB.py image.png -f secret.pdf
```

## Extract text 
```python
python LSB.py image.png
```

## Embed file 
```python
python LSB.py image.png -o extracted.pdf
```  
