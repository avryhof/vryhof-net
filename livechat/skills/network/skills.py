from livechat.personal_assistant.assistant_skill_class import AssistantSkill
from utilities.utility_functions import get_client_ip


class IPAddressSkill(AssistantSkill):
    name = "IP Address Skill"
    utterances = [
        "what is my ip",
        "what is my ip address",
        "ip address",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ip_address = self.chat_session.ip_address

    def handle(self):
        phrase = self.ip_address

        self.log("Saying: {}".format(phrase))

        return phrase
