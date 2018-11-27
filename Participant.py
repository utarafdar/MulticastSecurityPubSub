class Participant:
    def __init__(self, pairwise_key, participant_id):
        self.pairwise_key = pairwise_key
        self.participant_id = participant_id
        self.topics = []

    def add_topic(self, topic):
        # need to include logic for tree arrays
        self.topics.append(topic)
