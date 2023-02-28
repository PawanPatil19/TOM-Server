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
- create new conda environment `tom` using `conda env create -f environment-cpu.yml`
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
- To find/update dependencies, use `pip freeze > requirements.txt` or `conda env export > environment.yml` [ref](https://stackoverflow.com/questions/31684375/automatically-create-requirements-txt)


## Third-party libraries
- [python-fitbit](https://github.com/orcasgit/python-fitbit)


