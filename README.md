# PoliCond:  Conditional Privacy Policy Analysis Using Contextually Enhanced LLMs

PoliCond is a framework designed for analyzing privacy policies' internal contradictions based on LLM + Domain-specific Ontologies. 
It enables the automated generation of policy summaries and textual contradiction detection.
Ontologies' design figure can been found in `figures` folder.

## Get started

To begin using PoliCond, first install the required dependencies:

```bash
pip install -r requirements.txt
```

The main configuration items can be found in `config.py`, which controls the behavior of various components within the framework. 

The launcher.py serves as the primary entry point for executing the analysis pipeline. 

We provide example usage for file `launcher.py`, and you can run them by:

```bash
> $KEY= "xxx"
> $URL= "xxx"
> python .\launcher.py ".\test\Bluesky\4_Bluesky_cleaned.html" --key $KEY --url $URL
```
This will prompt LLMs to generate untrusted summaries for the policy content in the file `test/4_Bluesky_cleaned.html`.

Next we will run the analysis script to generate a readable yaml file  as a policy's summary and compute its contradiction. 

During the analysis, we will check its tuple form, check and normalize it with ontologies.

Run: 

```bash
python .\analyze_launcher.py --single --jsonl ".\test\Bluesky\analysis.jsonl"  --policy ".\test\Bluesky\4_Bluesky_cleaned.html" --output ".\test\Bluesky\Bluesky.yaml" --name "Bluesky"
```
And we can see related outputs in folder `test`.
Next, you can also run the `post_launcher.py` to infer more tuples from existing results.

## Demo Video
We supplemented a demo video in the release page to show how to use PoliCond.
To note, it was recorded in a previous version of PoliCond, which described both contradiction detection and a deprecated implementation of compliance check.
We hope users can find it helpful and ignore the deprecated part (compliance check).


## Folder structure

The repository is organized into the following components:

1. analyzer:  wrapped methods to generate readable policy summaries (in yaml format), invoked by analyzer_launcher.py.
   - `analyzer.py`: generates readable policy summaries from jsonl files
   - `post_analysis.py`: infer more tuples from existing results, whose input is the readable policy summaries.
2. contradiction - Implements contradiction detection algorithms and analysis tools  
   - `contradiction/rule.py` is the entrance point for contradiction detection
   - `higher_condition` and `lower_condition` and `no_condition` stores the defined rules
   - `contradiction\policyLint_cmp.py` is used to compare the results.
3. datasets - Stores input data files and processed datasets used in analysis
   - apps: stores the crawled htmls and the crawler scripts
      - datasets\apps\README.md: contains descrptive information about the crawled htmls
   - apps-PoliCond-DeepSeek: stores the results processed by the pipeline + Deepseek V3 model 
   - apps-PoliGraph: stores the results processed by the PoliGraph
   - apps-PolicyLint: stores the results processed by the PolicyLint and scripts used to transform its results
   - `datasets/collectionStmt`: stores the LLM-labelled statements for collection statements 
     - used-prompt.md`: stores the prompt and some arguments used to generate the collection statements
   - ontology-stat: stores the ontology statistical analysis results;
     - like `datasets/ontology-stat/condition-ontology.csv` stores the condition ontology's count in each file
     - `datasets/ontology-stat/condition-ontology-agg.csv` stores the coverage and total count
4. evals - Contains evaluation scripts. To note, most of evaluation results are stored in `datasets`.
   - scripts to generate part of figures or tables in the paper
5. ontology - Defines the ontological structure and knowledge representation framework
   - every folder stores at least 2 yaml files, one defines the subsumptive relation, 
     and the other defines the regex mappings of other items. 
   - every folder has  'handler.py' file, which is used to load the regex mappings and provide APIs for mapping strings 
     to ontology items, and also judge the relationship between two items.
   - `condition`: `ontology/condition/definition` stores the definition of each condition.
   - `data`: store data definitions and relationships
   - `entity`: stores entity definitions and relationships
   - old_ontology: stores the old ontology design and implementation, which is used to generate or evaluate the old results. If you want to use the old ontology, please rename existing `ontology` directory to another name, and rename the `old_ontology` directory to `ontology`.
6. pipeline - Core processing pipeline components that orchestrate the analysis workflow
   - `prompt_pipeline` and `async_prompt_pipeline` are two parallel processing pipelines that can generate LLM's results.
   - `prompt_template.py` stores the systemPrompt and userPrompt templates. 
7. util - Utility functions and helper modules used across the system
8. node.py: core data structure 'node' representing a 4-tuple, whose class name is CollectionNode or CollectionNodeWithContext
9. launcher.py: entry point for running the prompt engine, invoking LLMs and saving results as jsonl files
10. analyze_launcher.py: entry point for running the scripts to generate readable policy summaries from jsonl files
    - input: jsonl files by LLMs, privacy policy files
11. config.py: configuration items and logger config. 
   - set KEY and BASE_URL in config.py to run the pipeline
   - it also defines the logger by method `get_logger()`, which contains two implementations: one is normal logger, and the other is a logger that may hide sensitive information for double-blind review.
12. figures: stores figures about 3 ontologies, entity ontology, condition ontology, data ontology.

To note, node.py defines the fundamental data structures (4-tuples), and the configuration file (config.py) defines key variables.

## Verifiability

Generally, the `dataset` folder, the `evals` folder and the `ontology` folder are easy to verify.

### Check Summary & Contradiction Identification Function

Run analysis on single file:
```bash
> $KEY= "xxx"
> $URL= "xxx"
> python .\launcher.py ".\test\Bluesky\4_Bluesky_cleaned.html" --key $KEY --url $URL
> python .\analyze_launcher.py --single --jsonl ".\test\Bluesky\Bluesky\analysis.jsonl"  --policy ".\test\Bluesky\4_Bluesky_cleaned.html" --output ".\test\Bluesky\Bluesky.yaml" --name "Bluesky"
```

Run analysis on batch files:
```bash
> python .\launcher.py ".\test\batch" --key $KEY --url $URL
> python .\analyze_launcher.py --batch --jsonl ".\test\batch"  --policy ".\test\batch" --output ".\test\batch"
```