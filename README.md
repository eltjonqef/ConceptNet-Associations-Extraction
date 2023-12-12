# Subgraphs Creation

Here is the source code with which the triplets can be created

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements.

```bash
pip install -r requirements.txt
```
## Configuration

All the configuration needed to run the tool is inside the config folder which was provided. <br />
Inside config/config.yml you can view or change the parameters or the files that hold the restrains for the subgraph creation. If you need to change eg. the relations for the edges, you need to change the file that the config.yml points to or if you don't want to change the file itself you can change were the config file points to.<br />
Basically, you can change everything as long as inside the configuration folder there is a file called config.yml and the files that is points to exist.

## Execution

To execute the software you just need to run:

```bash
python main.py config

```
Or you can also use your own configuration folder. The tool will automatically create all the folders that are needed for the output. <br />
Note that it will take some minutes to download and build the conceptnet database the first time you run the code.

# Neo4j Measurements
In the repository there also exists the code to run measurements with neo4j. Just like the subgraph creation, it also need a configuration folder as a parameter.

## Execution

To execute the software you just need to run:

```bash
python neo4jDatabase.py config

```