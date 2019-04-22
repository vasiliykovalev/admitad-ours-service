import json
from typing import Optional, NamedTuple, List, Tuple
from collections import Counter
from urllib.parse import urlsplit


class Event(NamedTuple):
    client_id: str
    location: str
    referer: str

    @classmethod
    def from_dict(cls, json_dict: dict) -> 'Event':
        return cls(
            json_dict['client_id'],
            json_dict['document.location'],
            json_dict['document.referer'],
        )


class OursService:
    AFFILIATE_HOSTS = ['referal.ours.com', 'ad.theirs1.com', 'ad.theirs2.com']
    OURS_HOST = 'referal.ours.com'

    def __init__(self, log_path: str):
        self.log_path = log_path

    def _is_affiliate_referer(self, link: str) -> bool:
        return urlsplit(link).hostname in self.AFFILIATE_HOSTS

    def _is_ours_referer(self, link: Optional[str]) -> bool:
        return urlsplit(link).hostname == self.OURS_HOST

    def _is_checkout(self, link: str) -> bool:
        return urlsplit(link).path.startswith('/checkout')

    def process_log(self) -> List[Tuple[str, int]]:
        """
        :return: list of pairs, where
        first: winning our referer link,
        second: won times.
        Sorted by second.
        """
        user_last_aff_referer = {}
        ours_winning_ref = Counter()

        with open(self.log_path) as log:
            for line in log:
                event = json.loads(line, object_hook=Event.from_dict)
                if self._is_affiliate_referer(event.referer):
                    user_last_aff_referer[event.client_id] = event.referer

                elif self._is_checkout(event.location):
                    last_ref = user_last_aff_referer.get(event.client_id)
                    if self._is_ours_referer(last_ref):
                        ours_winning_ref[last_ref] += 1

        return ours_winning_ref.most_common()
