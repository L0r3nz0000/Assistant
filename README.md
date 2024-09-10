# Installation

```bash
chmod +x install.sh
./install.sh
```

# What is this?

The idea behind this voice assistant is to implement useful functions, such as smart home features, based on a generative model fine-tuned for chat in order to achieve a conversation as natural as possible, unlike the ones offered by other voice assistants like Alexa and Google Home.

# How to use

Start the service with ```sudo systemctl start Assistant```.

You can use the default wake word "jarvis." Wait for the activation sound and then ask your question.
If you want to change the wake word, you can go to [Picovoice](https://console.picovoice.ai/), create your
wake word, and download it into the wake_word_models/ directory

# Functions

* Answer to every type of question (using llama3-70b fine-tuned for chat)
* Execute bash and python scripts
* Tell the current date and time
* Create a timer
* Delete a timer
* Open websites on your browser
* Set an alarm (repeating or one-time)
* Change the speed of the voice according to the user preferences
* Delete all chat history
* Automatically pull new commits from this repo
* Change the master volume
* Turn on and off varius devices
* Control spotify playback
  * Play
  * Pause
  * Next
  * Prev
  * Play a specific song/artist/playlist/album
  * Add to queue
