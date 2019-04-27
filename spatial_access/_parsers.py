# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science


class BaseParser:

    @staticmethod
    def encode_source_id(source_id):
        return source_id

    @staticmethod
    def encode_dest_id(dest_id):
        return dest_id

    @staticmethod
    def decode_source_id(source_id):
        return source_id

    @staticmethod
    def decode_dest_id(dest_id):
        return dest_id

    @staticmethod
    def decode_vector_source_ids(vector):
        return vector

    @staticmethod
    def decode_vector_dest_ids(vector):
        return vector

    @staticmethod
    def encode_vector_source_ids(vector):
        return vector

    @staticmethod
    def encode_vector_dest_ids(vector):
        return vector

    @staticmethod
    def encode_filename(filename):
        return filename.encode('utf-8')

    @staticmethod
    def encode_category(category):
        return category.encode('utf-8')

    @staticmethod
    def decode_source_to_dest_array_dict(array_dict):
        return array_dict

    @staticmethod
    def decode_dest_to_source_array_dict(array_dict):
        return array_dict

    @staticmethod
    def decode_vector_of_dest_tuples(tuple_array):
        return tuple_array

    @staticmethod
    def decode_vector_of_source_tuples(tuple_array):
        return tuple_array


class IntStringParser(BaseParser):

    @staticmethod
    def encode_dest_id(dest_id):
        return dest_id.encode('utf-8')

    @staticmethod
    def decode_dest_id(dest_id):
        return dest_id.decode()

    @staticmethod
    def decode_vector_dest_id(vector):
        return [item.decode() for item in vector]

    @staticmethod
    def encode_vector_dest_ids(vector):
        return [item.encode('utf-8') for item in vector]

    @staticmethod
    def decode_source_to_dest_array_dict(array_dict):
        return {key: [item.decode() for item in value] for key, value in array_dict.items()}

    @staticmethod
    def decode_dest_to_source_array_dict(array_dict):
        return {key.decode(): value for key, value in array_dict.items()}

    @staticmethod
    def decode_vector_of_dest_tuples(tuple_array):
        return [(a.decode(), b) for a, b in tuple_array]


class StringIntParser(BaseParser):

    @staticmethod
    def encode_source_id(source_id):
        return source_id.encode('utf-8')

    @staticmethod
    def decode_source_id(source_id):
        return source_id.decode()

    @staticmethod
    def decode_vector_source_ids(vector):
        return [item.decode() for item in vector]

    @staticmethod
    def encode_vector_source_ids(vector):
        return [item.encode('utf-8') for item in vector]

    @staticmethod
    def decode_source_to_dest_array_dict(array_dict):
        return {key.decode(): value for key, value in array_dict.items()}

    @staticmethod
    def decode_dest_to_source_array_dict(array_dict):
        return {key: [item.decode() for item in value] for key, value in array_dict.items()}

    @staticmethod
    def decode_vector_of_source_tuples(tuple_array):
        return [(a.decode(), b) for a, b in tuple_array]


class StringStringParser(BaseParser):

    @staticmethod
    def encode_source_id(source_id):
        return source_id.encode('utf-8')

    @staticmethod
    def encode_dest_id(dest_id):
        return dest_id.encode('utf-8')

    @staticmethod
    def decode_source_id(source_id):
        return source_id.decode()

    @staticmethod
    def decode_dest_id(dest_id):
        return dest_id.decode()

    @staticmethod
    def decode_vector_source_ids(vector):
        return [item.decode() for item in vector]

    @staticmethod
    def decode_vector_dest_ids(vector):
        return [item.decode() for item in vector]

    @staticmethod
    def encode_vector_dest_ids(vector):
        return [item.encode('utf-8') for item in vector]

    @staticmethod
    def encode_vector_source_ids(vector):
        return [item.encode('utf-8') for item in vector]

    @staticmethod
    def decode_source_to_dest_array_dict(array_dict):
        return {key.decode(): [item.decode() for item in value] for key, value in array_dict.items()}

    @staticmethod
    def decode_dest_to_source_array_dict(array_dict):
        return {key.decode(): [item.decode() for item in value] for key, value in array_dict.items()}

    @staticmethod
    def decode_vector_of_dest_tuples(tuple_array):
        return [(a.decode(), b) for a, b in tuple_array]

    @staticmethod
    def decode_vector_of_source_tuples(tuple_array):
        return [(a.decode(), b) for a, b in tuple_array]