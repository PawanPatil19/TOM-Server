# TOM-Server-Python
A server for TOM

## Publications
- [publication_name](publication_link), VENUE'XX
```
<Bibtext>

```

## Contact person
- [Name](personal_website)


## Project links
- Project folder: [here](project_link)
- Documentation: [here](guide_link)
- [Version info](VERSION.md)


## Requirements
- make sure `pyhton3` is installed


## Installation
- install `conda` (e.g., [Anaconda](https://docs.anaconda.com/anaconda/install/)/[Miniconda](https://docs.conda.io/en/latest/miniconda.html))
- create new conda environment `tom` using `conda env create -f environment.yml`
- activate `tom` environment, `conda activate tom`
- create a file `fitbit_credential.json` with Fitbit credentials (Note: json format must be correct)
-- ```json
      {
      "client_id": "XXXXX",
      "client_secret": "YYYYYYYYYYYY"
      }
      ```


## Application execution 
- run `main.py` (e.g., `python main.py`)
- for tests, run `pytest`


## References
- [Structuring Your Project](https://docs.python-guide.org/writing/structure/)
- [Modules](https://docs.python.org/3/tutorial/modules.html#packages)
- [python-testing](https://realpython.com/python-testing/)


## Third-party libraries
- [python-fitbit](https://github.com/orcasgit/python-fitbit)


