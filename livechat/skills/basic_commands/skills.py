import random

from livechat.personal_assistant.assistant_skill_class import AssistantSkill


class SpeakSkill(AssistantSkill):
    name = "Speak Skill"
    utterances = ["say <str:phrase>", "repeat <str:phrase>"]
    params = ["phrase"]

    def handle(self):
        phrase = self.param_values.get("phrase")

        return phrase


class HelloSkill(AssistantSkill):
    name = "Hello Skill"
    utterances = ["hi", "hello", "howdy", "hola", "hidey-ho"]

    def handle(self):
        phrase = random.choice(self.utterances)
        self.log("Saying: {}".format(phrase))

        return phrase
