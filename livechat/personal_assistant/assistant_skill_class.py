import re

import contractions

from livechat.constants import VALID_CHARS
from livechat.personal_assistant.base_class import BaseClass
from utilities.utility_functions import is_empty


class AssistantSkill(BaseClass):
    name = None
    utterances = []
    params = []
    param_values = dict()

    utterance_expressions = []
    chat_session = None

    assistant_skill = True

    def __init__(self, utterances=False, **kwargs):
        super().__init__(**kwargs)

        self.chat_session = kwargs.get("chat_session")

        if self.name is None:
            self.name = re.sub("([A-Z])", " \\1", self.__class__.__name__).strip()

        if isinstance(utterances, str):
            self.utterances.append(utterances)

        self.utterance_expressions = []
        if isinstance(utterances, list):
            for utterance in utterances:
                self.utterances.append(utterance.lower())

        self.utterance_to_re()

    def __str__(self):
        if not is_empty(self.name):
            return self.name
        else:
            return self.__class__.name

    def utterance_to_re(self):
        re_parts = {"str": "[A-Za-z0-9 ]+?"}

        expression = r"<(.*?):(.*?)>"

        for utterance in self.utterances:
            new_utterance = utterance.lower()
            matches = re.findall(expression, utterance)
            for match in matches:
                replace_this = "<{}:{}>".format(match[0], match[1])
                with_this = "(?P<{}>{})".format(match[1], re_parts.get(match[0]))
                new_utterance = new_utterance.replace(replace_this, with_this)
                if new_utterance[-1] == ")":
                    new_utterance = "{}$".format(new_utterance)

            self.utterance_expressions.append(new_utterance)

    def get_param(self, param_name):
        return self.param_values.get(param_name, False)

    def parse(self, phrase):
        should_respond = False
        responded = False
        match_phrase = contractions.fix(phrase).strip().lower()
        match_phrase_string = "".join([x for x in match_phrase if x in VALID_CHARS])

        self.log(
            f"Name: {self.name}, Query:  {match_phrase}, "
            f"Query(str): {match_phrase_string}, "
            f"Expressions: {self.utterance_expressions}")

        for utterance_expression in self.utterance_expressions:
            if "<phrase>" in utterance_expression and (
                    match_phrase == utterance_expression or re.search(utterance_expression, match_phrase)
            ):
                self.log(f"Regex match: {utterance_expression}")
                m = re.match(utterance_expression, match_phrase)
                if m is not None:
                    for param in self.params:
                        try:
                            self.param_values.update({param: m.group(param)})
                        except IndexError:
                            pass
                        else:
                            self.log(self.param_values)

                responded = self.handle()
                if not is_empty(responded):
                    break

            elif match_phrase_string.lower().strip() == utterance_expression.lower().strip():
                self.log("String match")
                responded = self.handle()
                if not is_empty(responded):
                    break

        return responded

    def handle(self):
        raise NotImplementedError("subclasses of AssistantSkill must provide a handle() method")

    def speak(self, phrase=None):
        if phrase is None:
            phrase = self.param_values.get("phrase")
            print(phrase)
