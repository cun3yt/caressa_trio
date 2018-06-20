from random import randint


class FetchRandomMixin:
    @staticmethod
    def fetch_random_item(query_set, exclude_list=None):
        exclude_list = [] if exclude_list is None else exclude_list
        exclude_count = len(exclude_list)
        count = query_set.all().count() - exclude_count

        if count <= 0:
            return None
        random_slice = randint(0, count-1)
        result_set = query_set.exclude(id__in=exclude_list).all()[random_slice: random_slice+1]
        return result_set[0]
