class Collection(object):
    def __init__(self, file, seq_delimiter, seq_parser, point_parser):
        self.set_delimiter = '..'
        self.seq_delimiter = seq_delimiter
        self.file = self._sanitize_file(file)
        self.seq_parser = seq_parser
        self.point_parser = point_parser
        self.states = {}
        self.outputs = {}

        self.sets = self._create_sets()
        self.training = self.sets[0]
        self.testing = self.sets[1]
        self.unique_state_count = len(self.states)
        self.unique_outputs_count = len(self.outputs)

        self.statekeys = self.states.keys()

    def _create_sets(self):
        return [Set(s, self) for s in self._parse_raw_collection()]

    def _parse_raw_collection(self):
        return self.file.split(self.set_delimiter)

    def _sanitize_file(self, file):
        file = open(file).read().splitlines()

        if self.seq_delimiter == '.':
            return '\n'.join(file[:-1])
        else:
            return '\n'.join(file)


class Set(object):
    def __init__(self, raw_set, collection):
        self.collection = collection
        self.state_output_counts = {}
        self.state_counts = {}
        self.sequences = self._create_sequences(raw_set)

    def _create_sequences(self, raw_set):
        return [Sequence(s, self.collection, self)
                for s in self._parse_raw_set(raw_set) if s]

    def _parse_raw_set(self, raw_set):
        return raw_set.split(self.collection.seq_delimiter)


class Sequence(object):
    def __init__(self, raw_sequence, collection, current_set):
        self.collection = collection
        self.set = current_set
        self.points = self._create_points(raw_sequence)

    def _create_points(self, raw_sequence):
        return [Point(p, self.collection, self.set)
                for p in self._parse_raw_sequence(raw_sequence) if p]

    def _parse_raw_sequence(self, raw_sequence):
        return self.collection.seq_parser(raw_sequence)

    def inputs(self):
        return [point.input for point in self.points]

    def outputs(self):
        return [point.output for point in self.points]


class Point(object):
    def __init__(self, raw_point, collection, current_set):
        self.collection = collection
        self.set = current_set
        self.data = self._parse_raw_point(raw_point)

        self.input = self.data['input']
        self.output = self.data['output']

    def _parse_raw_point(self, raw_point):
        # Insert raw point into dict to ensure uniqueness
        parsed_point = self.collection.point_parser(raw_point)
        state = parsed_point['input']
        output = parsed_point['output']
        self.collection.states[state] = True
        self.collection.outputs[output] = True
        state_output = (state, output)

        # Cache state count
        if state not in self.set.state_counts:
            self.set.state_counts[state] = 1
        else:
            self.set.state_counts[state] += 1

        # Cache state ouput pair count
        if state_output not in self.set.state_output_counts:
            self.set.state_output_counts[state_output] = 1
        else:
            self.set.state_output_counts[state_output] += 1

        return parsed_point
