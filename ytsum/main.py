from youtube_transcript_api import YouTubeTranscriptApi
from ollama import Client
import pyperclip
import argparse
import os

def get_path_to_cache(id): 
    os.makedirs(os.path.dirname('./cache/'), exist_ok=True)
    return  './cache/' + id + '.txt'

def get_transcript(link):
    video_id = link.split("=")[1].split("&")[0]

    cacheFilePath = get_path_to_cache(video_id)
    text = ''

    ## Cache into file the transcript
    try:
        with open(cacheFilePath, "r") as f:
            text = f.read()
    except IOError:
        tr = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([obj['text'] for obj in tr])

        with open(cacheFilePath, "w+") as f:
            f.write(text)

    return text, video_id


def get_summary(ollama_url, ollama_model, transcript, video_id, force=False):
    cacheFilePath = get_path_to_cache(video_id + '_response')
    text = ''

    if (force):
        try:
            os.remove(cacheFilePath)
        except OSError:
            pass

    ## Cache into file the response
    try:
        with open(cacheFilePath,"r") as f:
            text = f.read()
    except IOError:
        content = """
            Summarize in few key takeaways the transcript TEXT bellow. Format it with title, section headers and points within the section.
         
            TEXT:
            {text}
        """.format(text=transcript)

        ollama = Client(host=ollama_url)
        response = ollama.generate(model=ollama_model, options={ 'temperature': 0.1 }, prompt=content)

        text = response['response']
        
        with open(cacheFilePath, "w+") as f:
            f.write(text)

    return text


def main():
    parser=argparse.ArgumentParser(
        prog='''Youtube video Summarizer''',
        description='''Summarizing a youtube video in few key points.''',
        epilog="""Both the YT transcrpit and the Summary are cached for optimised usage.""")
    parser.add_argument('link', help='The link to the youtube video to summarize')
    parser.add_argument('--ollama_url', default='http://localhost:11434', help='The url of a running ollama instance.')
    parser.add_argument('--ollama_model', default='mistral', help='The model name for the ollama instance.')
    parser.add_argument('-f', action='store_true', default=False, help='Force to regenerate the message with LLM instead of using the cache.')
    parser.add_argument('-c', action='store_true', default=False, help='Copy the response to the clipboard in the end.')
    args=parser.parse_args()

    transcript, id = get_transcript(args.link)
    response = get_summary(args.ollama_url, args.ollama_model, transcript, id, args.f)

    print(response)
    
    if (args.c):
        pyperclip.copy(response)
        print('Response successfully copied to the clipboard.')

if __name__ == "__main__":
    main()
