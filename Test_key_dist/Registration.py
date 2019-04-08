import uuid
import random


class Registration:

    @staticmethod
    def register(topic):
        participant_id = str(uuid.uuid4())
        pairwise_key = random.randrange(1000, 99999)
        initial_topic_topic_keys = topic + str(pairwise_key)+'topic_keys_initial_topic'
        initial_topic_ancestor_keys = topic + str(pairwise_key) + 'ancestor_keys_initial_topic'
        return pairwise_key, participant_id, initial_topic_topic_keys, initial_topic_ancestor_keys