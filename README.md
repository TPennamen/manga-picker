# Manga Picker

A little project in python to compile manga scans from the https://scansmangas.xyz website in pdf file for e-reader.


## How to install

You can setup a virtualenv and/or just install requirements to launch the programm

```
pip install -r requirements.txt
```

## How to use it

```
python run.py --manga=<manga-name>
```
The result will be in output directory.
You can also put an optional argument <b>agg</b> which make each pdf file an aggregation of agg number of scans in each pdf file.

```
python run.py --manga=<manga-name> --agg=2
```