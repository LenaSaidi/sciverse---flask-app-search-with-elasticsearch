# Run grobide image:
<!-- docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 lfoppiano/grobid:0.8.0-arm

docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 lfoppiano/grobid:0.8.0-arm

docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.0 -->

> grobid_client --input ./test.pdf --output ./ processFulltextDocument

docker run --rm --init --ulimit core=0 -p 8070:8070 lfoppiano/grobid:0.8.0

then run example.py


{
  "title": "",
  "abstract": "",
  
  "authors": [
    {
      "name": "",  #required: the author should have a name
      "email": "",
      "institutions": [
        {
          "institution_name": ""
        }
      ]
    },
  ],
  "keywords": [
    "",
    "",
    ""
  ],
  "references": #all the text content of references in the xml file, 
  #each reference has analytic
  [
    "Reference 1",
    "Reference 2"
  ],
  "full_text": "",#all the text of the <body>, or all the paragraphes in the body
}


#_____________________________________________________________________


