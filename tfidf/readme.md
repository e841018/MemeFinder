# TFIDF

## Environment
- Python==3.8
- `pip install -r requirements.txt`
- download CkipTagger models: 
  - [iis-ckip](http://ckip.iis.sinica.edu.tw/data/ckiptagger/data.zip)
  - Downloads to ./data.zip (2GB) and extracts to ./data/
- `mkdir models`

## Main Usage
- `tfidf.py`: load dataset and build tfidf model, also retrieve from the input query  

## How To Run
- `python tfidf.py --text_file <text_file_path> --tfidf_path <tfidf_model_path> --index_path <index_model_path> --tagger_path <tagger_model_path>`
- example: `tfidf.sh`

## Functions Usage Example
- build model
```
tfidf = TFIDF(all_text)
tfidf.build_models(tfidf_path, index_path)
```
- get retrieval results
```
indices, scores = tfidf.retrieve(queryStr, k=10)
imageId, text = tfidf.get_result(indices[0])
```
## Dataset
- ocr test results form images
  - `ocr_texts/text.csv`

## References
- https://github.com/ckiplab/ckiptagger
- https://github.com/andyh0913/ML2019SPRING/blob/master/final/src/retriever.py#L17
