import os
import re
import sys
from abc import ABC, abstractmethod

import grpc
import pyaudio
from dotenv import load_dotenv

from auth import authorization_metadata
from tinkoff.cloud.stt.v1 import stt_pb2, stt_pb2_grpc
from tinkoff.cloud.tts.v1 import tts_pb2, tts_pb2_grpc

sys.path.append("..")
load_dotenv()

ENDPOINT = os.environ.get("ENDPOINT") or "stt.tinkoff.ru:443"
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
SAMPLE_RATE = 48000


class SpeechCommand(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class TTS(SpeechCommand):
    """
    Text To Speech
    """
    def __init__(self, phrase):
        phrase = phrase.replace('&nbsp;', '. ')
        self._ssml = '<speak><p>' + phrase + '</p></speak>'
        self._text  = re.sub(r'\<[^>]*\>', '', phrase)
        stub = tts_pb2_grpc.TextToSpeechStub(
            grpc.secure_channel(
                ENDPOINT,
                grpc.ssl_channel_credentials()
            )
        )
        metadata = authorization_metadata(
            API_KEY,
            SECRET_KEY,
            "tinkoff.cloud.tts"
        )
        request = tts_pb2.SynthesizeSpeechRequest(
            input=tts_pb2.SynthesisInput(
                text=self._text,
                ssml=self._ssml
            ),
            audio_config=tts_pb2.AudioConfig(
                audio_encoding=tts_pb2.LINEAR16,
                speaking_rate=1,
                sample_rate_hertz=SAMPLE_RATE
            )
        )
        self._responses = stub.StreamingSynthesize(
            request,
            metadata=metadata
        )

    def execute(self) -> None:
        pyaudio_lib = pyaudio.PyAudio()
        f = pyaudio_lib.open(
            output=True,
            channels=1,
            format=pyaudio.paInt16,
            rate=SAMPLE_RATE
        )
        for key, value in self._responses.initial_metadata():
            if key == "x-audio-num-samples":
                print(self._text)
                print("Estimated audio duration is "
                      + str(int(value) / SAMPLE_RATE)
                      + " seconds"
                )
                break
        for stream_response in self._responses:
            f.write(stream_response.audio_chunk)


class STT(SpeechCommand):
    """
    Speech To Text
    """
    def __init__(self, recognize):
        self._recognize = recognize
        r = stt_pb2.StreamingRecognizeRequest()
        r.streaming_config.config.encoding = stt_pb2.AudioEncoding.LINEAR16
        r.streaming_config.config.sample_rate_hertz = 16000
        r.streaming_config.config.num_channels = 1
        r.streaming_config.config.enable_denormalization = True
        r.streaming_config.config.enable_automatic_punctuation = True
        r.streaming_config.config.vad_config.silence_duration_threshold = 1.20
        r.streaming_config.single_utterance = True
        r.streaming_config.config.speech_contexts.append(
            stt_pb2.SpeechContext(
                phrases = [
                    stt_pb2.SpeechContextPhrase(
                        text=text,
                        score=10.0
                    ) for text in self._recognize.context_words
                ]
            )
        )
        metadata = authorization_metadata(
            API_KEY,
            SECRET_KEY,
            "tinkoff.cloud.stt"
        )
        stub = stt_pb2_grpc.SpeechToTextStub(
            grpc.secure_channel(
                ENDPOINT,
                grpc.ssl_channel_credentials()
            )
        )
        self._responses = stub.StreamingRecognize(
            self.requests(r),
            metadata=metadata
        )

    def execute(self) -> None:
        self._recognize.recognition_utterance(self._responses)
        self._recognize.search_intents()
        self._recognize.search_entities()
        self._recognize.search_products()
        self._recognize.search_name()
        self._recognize.search_city()
        self._recognize.search_digit()


    @staticmethod
    def requests(request):
        try:
            yield request
            pyaudio_lib = pyaudio.PyAudio()
            f = pyaudio_lib.open(
                input=True,
                channels=1,
                format=pyaudio.paInt16,
                rate=16000
            )
            for data in iter(lambda: f.read(800), b''):
                request = stt_pb2.StreamingRecognizeRequest()
                request.audio_content = data
                yield request
        except Exception as e:
            print("Got exception in generate_requests", e)
            raise


class Invoker:
    _on_speak = None
    _on_listen = None

    def set_on_speak(self, ssml: SpeechCommand):
        self._on_speak =  TTS(ssml)

    def set_on_listen(self, recognize: SpeechCommand):
        self._on_listen = STT(recognize)

    def do_speak(self):
        if isinstance(self._on_speak, SpeechCommand):
            print("\nRobot:", end=" ")
            self._on_speak.execute()

    def  do_listen(self):
        if isinstance(self._on_listen, SpeechCommand):
            print("\nCustomer: ", end=" ")
            self._on_listen.execute()

    def do_conversation(self) -> None:
        if isinstance(self._on_speak, SpeechCommand):
            print("\nRobot:", end=" ")
            self._on_speak.execute()
        if isinstance(self._on_listen, SpeechCommand):
            print("\nCustomer: ", end=" ")
            self._on_listen.execute()
