# OpenTutor

OpenTutor is a chrome extension that allows you to ask questions about the lecture material you are currently in.
Using the Watson Assistant interface, the OpenAI API, Modal for cloud deployment and Lantern for vector
embeddings database, we are able to load context at an amazing speed for MIT courses.

Unlike fine-tuning a model, which takes time and can get really expensive to do, OpenTutor creates an embedding
of the lecture material and uses that to find the most relevant answer to your question. This allows us to load
the context you are interested in to the OpenAI API and get a response back in a matter of seconds. Loading new
material is also a matter of seconds, as we only need to create a new embedding and add it to the database.

## Setup

1) Download chrome-extension.
2) Go to Chrome Extensions chrome://extensions/.
3) Enable Developer Mode.
4) In 'Load Unpacked', select the chrome-extension folder you downloaded.

## Usage

Go to any OCW website and click on the extension. If the website has been processed, you'll see a chatbot pop up
in the bottom right of the screen. Then, you can interact with this chatbot to ask questions about the specific
lecture material you are currently in.


## Development

To run the internal development processes,

Install lantern locally
`docker run -p 65431:5432 -e 'POSTGRES_PASSWORD=postgres' lanterndata/lantern:latest-pg15`

