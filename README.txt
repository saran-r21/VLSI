
We have just one code file for Phase one. The code file is sta_parser.py.
Totally we have 3 files in the zip. Code file, README, and requirements.txt.
The same file parses and generates all 3 of the required files.
Below are the 3 commands that are executed for the code sta_parser.py:

python3.7 sta_parser.py --read_ckt c17.bench
python3.7 sta_parser.py --delays --read_nldm sample_NLDM.lib
python3.7 sta_parser.py --slews --read_nldm sample_NLDM.lib

We can replace the bench c17.bench with any other bench. We can also give a path and it will still work. Based on the commands the outputs will be written to
1. circuits.txt
2. delays.txt
3. slews.txt
