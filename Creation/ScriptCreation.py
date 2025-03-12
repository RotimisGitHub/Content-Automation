import random
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import requests
from moviepy.editor import *
import tempfile
import os
import python_to_postgres as Postgres
from Creation.capcutAutomation import collectSubtitles
from reddit_image import create_reddit_image

load_dotenv(".env")

API_KEY = os.environ.get("MICROSOFT_AZURE_TTS_1")
ENDPOINT = os.environ.get("MICROSOFT_AZURE_TTS_ENDPOINT")
REGION = os.environ.get("MICROSOFT_AZURE_TTS_REGION")


class Script:
    """
    A class for automating content creation from Reddit posts, including identifying gender, generating subtitles,
    creating voiceovers, and producing a final video.

    Attributes:
        subreddit_q (str): The subreddit from which the story data is derived.
        data (dict): A dictionary containing the content data for processing.
        gender (str): The identified gender perspective of the story.
        background_video (VideoFileClip): The raw background video without audio.
    """

    def __init__(self, subreddit_q, data):
        """
        Initialize the Script class.

        Args:
            subreddit_q (str): The name of the subreddit from which the data originates.
            data (dict): A dictionary containing the story, its ID, URL, and other associated metadata.
        """
        self.subreddit_q = subreddit_q
        self.data = data
        self.output_directory = f'/Users/rotimi_jatto/PycharmProjects/Proper_Projects/ContentAutomation/Creation/FinalVideos/{self.data["Id"]}'
        self.gender = self._identifyGender()
        self.story_audio = self.createVoiceOvers()
        self.background_video = self._applyFade(self._create_raw_video(), 'out', 0.5)
        self.reddit_post = create_reddit_image(self.data["Author"], self.data["Title"])
        self.reddit_post_image_clip = self._applyFade(ImageClip(self.reddit_post).set_duration(5), 'out')
        self.background_audio = AudioFileClip(
            'media/Undertale OST - fallen down (slowed + reverb) - Sunshine (youtube).mp3').volumex(0.2)

    def _identifyGender(self):
        """
        Identify the gender perspective of the story using an LLM (Language Learning Model).

        Returns:
            str: The gender perspective of the story, either 'male' or 'female'.
        """
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        prompt = PromptTemplate(
            input_variables=["story"],
            template='''
                Given the context of the story: {story}. Use one word to identify whether the story is written from the 
                perspective of a male or female.
            '''
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        gender = chain.run(self.data["Story"])
        return gender

    def _voice_over_helper(self, response):

        temp_audioFile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

        with open(temp_audioFile.name, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        audioClip = AudioFileClip(temp_audioFile.name)
        print(f"Successfully acquired audio: {audioClip.filename}")

        return audioClip

    def createVoiceOvers(self):
        # Set up the headers
        headers = {
            'Ocp-Apim-Subscription-Key': API_KEY,
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
        }

        # Set up the URL
        url = f"{ENDPOINT}/cognitiveservices/v1"

        # Construct the SSML (Speech Synthesis Markup Language) request
        if self.gender == "Female":
            gender = "Female"
            name = 'en-US-AriaNeural'
        else:
            gender = 'Male'
            name = 'en-US-GuyNeural'

        ssml = f"""
        <speak version='1.0' xml:lang='en-US'>
            <voice xml:lang='en-US' xml:gender='{gender}' name='{name}'>
            <prosody rate="-5%" pitch="2%">
                {self.data["Story"]}
                </prosody>
            </voice>
        </speak>
        """

        # Make the request
        response = requests.post(url, headers=headers, data=ssml.encode('utf-8'))

        # Check the response
        if response.status_code == 200:
            # Save the audio content to a file
            voice_over = self._voice_over_helper(response)
            return voice_over
        else:
            print(f"Error: {response.status_code}, {response.text}, \n{response.links}, \n{response.content}")

    def _create_raw_video(self):
        """
        Create a raw background video by stitching together random video clips and overlaying the voiceover.

        Returns:
            VideoFileClip: The video clip with the applied voiceover and correct duration.
        """
        directory_of_backgrounds = (
            "/Users/rotimi_jatto/PycharmProjects/Proper_Projects/ContentAutomation/Creation/Background_Videos/"
        )
        background_videos = [directory_of_backgrounds + i for i in os.listdir(directory_of_backgrounds) if
                             i.endswith('.mp4')]

        selected_video = random.choice(background_videos)
        video_clip = VideoFileClip(selected_video).without_audio().set_duration(self.story_audio.duration)

        print(f"This Video is {self.story_audio.duration} in duration length.")

        return video_clip

    def create_tiktok_clips(self):
        combined_audio = CompositeAudioClip([self.story_audio, self.background_audio])
        tiktok_video = CompositeVideoClip(
            [self.background_video, self.reddit_post_image_clip.set_position(("center", "center"))]).set_audio(
            combined_audio)
        clip_list = []
        clipDivider = tiktok_video.duration // 60

        for i in range(clipDivider):
            start_time = i * (tiktok_video.duration / clipDivider)
            if not i == clipDivider - 1:
                end_time = (i + 1) * (tiktok_video.duration / clipDivider)
            else:
                end_time = tiktok_video.duration
            sub_clipped = tiktok_video.subclip(start_time, end_time)
            clip_list.append(sub_clipped)


        try:

            tiktok_file_paths = {}

            for index, vid in enumerate(clip_list, start=1):
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video_file:

                    vid.write_videofile(temp_video_file.name, fps=60,
                                        temp_audiofile="temp-audio.m4a",
                                        remove_temp=True,
                                        codec="libx264", audio_codec="aac")

                collectSubtitles(self.data['subreddit query'] + self.data['Id'] + f" part {index}",
                                 temp_video_file.name)
                temp_video_file.close()
                if index == 1:
                    self.upload_to_database()

        except Exception as e:
            raise Exception(f"Error encountered during video writing: {e}")
        finally:
            # Clean up resources (important for large video/audio files)
            self.background_video.close()
            self.story_audio.close()

        return tiktok_file_paths

    def _applyFade(self, media, in_or_out: str, fade_time: float = 1):
        """
        Apply a fade-in or fade-out effect to a video clip.

        Args:
            media: The video clip to apply the fade effect to.
            in_or_out (str): Specifies whether to apply 'in', 'out', or 'both' fade directions.
            fade_time (float): The duration of the fade effect in seconds.

        Returns:
            VideoFileClip: The video clip with the fade effect applied.
        """
        if in_or_out == "in":
            faded = transfx.fadein(media, fade_time)
        elif in_or_out == 'out':
            faded = transfx.fadeout(media, fade_time)
        elif in_or_out == 'both':
            faded = transfx.fadein(media, fade_time)
            faded = transfx.fadeout(faded, fade_time)
        else:
            raise ValueError("Please input a proper fade value: 'in', 'out', or 'both'.")

        return faded

    def upload_to_database(self):
        """
        Upload the story, gender, subtitles, and final video file paths to the Postgres database.

        """

        postgres_handler_init = Postgres.PGHandler("reddit_data")
        postgres_handler_init.insert_to_table(self.data["Id"], self.data["subreddit query"], self.data["Title"],
                                              self.data["Url"], "now()", "now()", None,
                                              self.data['Author'])
