class SessionMemory:
    def __init__(self):
        self.evaluations = []

    def add_evaluation(self, evaluation: dict):
        self.evaluations.append(evaluation)

    def get_summary(self):
        return self.evaluations