from mp3tagger.classes.slider import List


from typing import List, Tuple, TypedDict


class SectionData(TypedDict):
    group_control: int
    label: str
    scales: List[Tuple[str, int]]