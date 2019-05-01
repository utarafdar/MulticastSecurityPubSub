import uuid
import random
import os
import nacl.utils


class Registration:

    @staticmethod
    def register(topic):
        # participant_id = str(uuid.uuid4())
        participant_id = "testParticiapnt123"
        pairwise_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
        # pairwise_key = os.urandom(16)
        initial_topic_topic_keys = topic + str(participant_id)+'topic_keys_initial_topic'
        initial_topic_ancestor_keys = topic + str(participant_id) + 'ancestor_keys_initial_topic'
        return pairwise_key, participant_id, initial_topic_topic_keys, initial_topic_ancestor_keys