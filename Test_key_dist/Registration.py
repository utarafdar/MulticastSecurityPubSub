import uuid
import random
import os

class Registration:

    @staticmethod
    def register(topic):
        participant_id = str(uuid.uuid4())
        pairwise_key = os.urandom(16)
        initial_topic_topic_keys = topic + str(participant_id)+'topic_keys_initial_topic'
        initial_topic_ancestor_keys = topic + str(participant_id) + 'ancestor_keys_initial_topic'
        return pairwise_key, participant_id, initial_topic_topic_keys, initial_topic_ancestor_keys